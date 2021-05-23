# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import scrapy
import logging
import pandas as pd
from datetime import date
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


# %%
class PatientSpider(scrapy.Spider):
    name = "patient_check"
    start_urls = ['https://ncov.moh.gov.vn/web/guest/trang-chu']
    rows = []
    out = 'MOH_PaitentTable_' + date.today().strftime("%d_%m") + '.csv'

    def __init__(self):
        logging.getLogger('scrapy').propagate = False

    def close(self, reason):
        df_out = pd.DataFrame(self.rows)
        df_out.to_csv(self.out,index=False)
        print("Hoàn tất. Dữ liệu đã được xuất ra file " + self.out)

    def parse(self, response):
        for patient in response.xpath('//*[@class="table table-striped table-covid19"]//tbody/tr'):
            p_dict={'BN': patient.xpath('td[1]//text()').extract_first(),
                    'Age': patient.xpath('td[2]//text()').extract_first(),
                    'Location': patient.xpath('td[3]//text()').extract_first(),
                    'Status': patient.xpath('td[4]//text()').extract_first(),
                    'Nationality': patient.xpath('td[5]//text()').extract_first()}
            self.rows += [p_dict]


# %%
process = CrawlerProcess(get_project_settings())
process.crawl(PatientSpider)
process.start()
input("Nhấn phím 2 để thưa ngài. Nhấn Enter để thoát, ")





