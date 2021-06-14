# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import scrapy
import logging
import re
import pandas as pd
from datetime import date
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


# %%
class PatientSpider(scrapy.Spider):
    name = "patient_check"
    #start_urls = ['https://ncov.moh.gov.vn/web/guest/trang-chu']
    start_urls = ['https://ncov.moh.gov.vn/web/guest/trang-chu?p_p_id=corona_trangchu_top_CoronaTrangchuTopPortlet_INSTANCE_RrVAbIFIPL7v&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&_corona_trangchu_top_CoronaTrangchuTopPortlet_INSTANCE_RrVAbIFIPL7v_delta=100&_corona_trangchu_top_CoronaTrangchuTopPortlet_INSTANCE_RrVAbIFIPL7v_resetCur=false&_corona_trangchu_top_CoronaTrangchuTopPortlet_INSTANCE_RrVAbIFIPL7v_cur='+str(i) for i in range(1,10)]
    rows = []
    out = 'MOH_PatientTable_' + date.today().strftime("%d_%m") + '.csv'

    def __init__(self):
        logging.getLogger('scrapy').propagate = False

    def close(self, reason):
        df_out = pd.DataFrame(self.rows)[::-1]
        #df_out['Patient'] = df_out['Patient'].str[2:].apply(lambda x: re.sub(r'^[0-9]','',x))#.astype(int)
        df_out['Patient'] = df_out['Patient'].apply(lambda x: re.sub(r'^[0-9]+','',x), convert_dtype=True)#.astype(int)
        #print(df_out.dtypes)
        df_out.sort_values(by=['Patient'],inplace=True,ascending=True)
        df_out.to_csv(self.out,index=False)
        print("Hoàn tất. Dữ liệu đã được xuất ra file " + self.out)

    def parse(self, response):
        for patient in response.xpath('//*[@class="table table-striped table-covid19"]//tbody/tr'):
            p_dict={'Patient': patient.xpath('td[1]//text()').extract_first(),#.rstrip(),
                    'Age': patient.xpath('td[2]//text()').extract_first(),
                    'Location': patient.xpath('td[3]//text()').extract_first(),
                    'Status': patient.xpath('td[4]//text()').extract_first(),
                    'Nationality': patient.xpath('td[5]//text()').extract_first()}
            if p_dict['Age']:
                self.rows += [p_dict]

        # next_page = /page-{}/ where {} number of page.
        #next_page = response.xpath('//a[@data-tip="Next page"]/@href').extract_first()
        #scrapy.Request(url='',callback=self.parse)
        # next_page = https://sanet.st/page-{}/ where {} number of page.
        #next_page = response.urljoin(next_page)



# %%
process = CrawlerProcess(get_project_settings())
process.crawl(PatientSpider)
process.start()
input("Nhấn phím 2 để thưa ngài. Nhấn Enter để thoát, ")





