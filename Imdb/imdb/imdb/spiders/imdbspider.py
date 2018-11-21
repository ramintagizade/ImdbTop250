import scrapy
from imdb.items import ImdbItem
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
import io
from scrapy.http import HtmlResponse
import logging
from scrapy import Spider
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher

class ImdbSpider(scrapy.Spider) :
    name = "imdbspider"
    allowed_domains = ["imdb.com"]
    start_urls = "https://www.imdb.com/chart/top"

    def __init__(self) :
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def start_requests(self):
        
        self.imdb = ImdbItem()
        self.items = {}
        self.ids = 0
        self.initialize = False
        yield scrapy.Request(self.start_urls, self.parse)

    def parse(self,response) :
        self.get_movie_entity(response)
        if response.xpath(".//tbody[@class='lister-list']/tr/td[@class='titleColumn']/a/@href").extract() :
            urls = response.xpath(".//tbody[@class='lister-list']/tr/td[@class='titleColumn']/a/@href").extract()
        
            for url in urls: 
                self.ids = self.ids  + 1
                yield scrapy.Request("https://www.imdb.com" + url, callback=self.parse_details,dont_filter=True,meta={'itemId': self.ids-1})

        yield self.imdb

    def parse_details(self,response) :

        itemId = response.meta["itemId"]
        duration = response.xpath(".//div[@class='title-overview']/div/div[@class='vital']/div[@class='title_block']/div/div[@class='titleBar']/div[@class='title_wrapper']/div[@class='subtext']/time/text()").extract()
        duration = [x.strip() for x in duration]
        genreDateCountryArray = response.xpath(".//div[@class='title-overview']/div/div[@class='vital']/div[@class='title_block']/div/div[@class='titleBar']/div[@class='title_wrapper']/div[@class='subtext']/a/text()").extract()
        genre_arr_len = len(genreDateCountryArray)
        genre = ",".join([genreDateCountryArray[x].strip() for x in range(genre_arr_len-1)])
        issue_date = genreDateCountryArray[genre_arr_len-1].split("(")[0]
        issue_country =  genreDateCountryArray[genre_arr_len-1][genreDateCountryArray[genre_arr_len-1].find("(")+1:genreDateCountryArray[genre_arr_len-1].find(")")]
        summary_item =  response.xpath(".//div[@class='title-overview']//div[@class='credit_summary_item']").extract()
        summary_item[0] = HtmlResponse(url=response.url, body=summary_item[0],encoding='utf-8').xpath(".//a/text()").extract()
        summary_item[2] = HtmlResponse(url=response.url, body=summary_item[2],encoding='utf-8').xpath(".//a/text()").extract()
        stars = summary_item[2][0:len(summary_item[2])-1]
        directors = str(summary_item[0])
        metascore = response.xpath(".//div[@class='title-overview']//div[@class='plot_summary_wrapper']//div[@class='titleReviewBarItem']/a//span/text()").extract()
        popularity = response.xpath(".//div[@class='title-overview']//div[@class='plot_summary_wrapper']/div[@class='titleReviewBar ']/div[@class='titleReviewBarItem']/div[@class='titleReviewBarSubItem']//span[@class='subText']/text()").extract()
        popularity = "".join(re.findall('\d+',str(popularity))) 
    
        if not self.initialize :
            self.imdb["id"] = []
            self.imdb["title"] = []
            self.imdb["rating"] = []
            self.imdb["duration"] = []
            self.imdb["genre"] = []
            self.imdb["issue_date"] = []
            self.imdb["issue_country"] = []
            self.imdb["directors"] = []
            self.imdb["stars"] = []
            self.imdb["metascore"] = []
            self.imdb["popularity"] = []
            self.initialize = True

        self.imdb["id"].append(self.items["id"][itemId])
        self.imdb["title"].append(self.items["title"][itemId])
        self.imdb["rating"].append(self.items["rating"][itemId])
        self.imdb["duration"].append(str(duration))
        self.imdb["genre"].append(str(genre))
        self.imdb["issue_date"].append(str(issue_date))
        self.imdb["issue_country"].append(str(issue_country))
        self.imdb["directors"].append(str(directors))
        self.imdb["stars"].append(",".join(x for x in stars ))
        self.imdb["metascore"].append(str(metascore))
        self.imdb["popularity"].append(str(popularity))
            
        yield self.imdb
        
    def get_movie_entity(self , response) :
        
        self.imdb["id"] = response.xpath(".//tbody[@class='lister-list']/tr/td[@class='posterColumn']/span[@name='rk']/@data-value").extract()
        self.imdb["title"] = response.xpath(".//tbody[@class='lister-list']/tr/td[@class='titleColumn']/a/text()").extract()
        self.imdb["rating"] = response.xpath(".//tbody[@class='lister-list']/tr/td[@class='ratingColumn imdbRating']/strong/text()").extract()
        self.items["id"] = self.imdb["id"]
        self.items["title"] = self.imdb["title"]
        self.items["rating"] = self.imdb["rating"]

    def spider_closed(self, spider):
        logging.info("ids  " + str(self.ids))
        logging.info('Spider closed: %s', spider.name)
        data = ET.Element('entries')  
        for i in range(self.ids) :
            entry = ET.SubElement(data, 'entry')
            itemId = ET.SubElement(entry,"id") 
            for k in self.imdb.keys():
                if k == "id" :
                    item = itemId
                else :
                    item = ET.SubElement(entry, k)   
                s =  self.imdb[k][i].strip()
                item.text  = s.strip("[]").strip("\n\t\r").lstrip("\n").rstrip("\n").strip("u'\n ").strip("'")
                
            mydata = minidom.parseString(ET.tostring(data)).toprettyxml()
            myfile = io.open("output.xml", "w",encoding='utf8') 
            myfile.write(mydata)  
        
        logging.info("output xml finished")