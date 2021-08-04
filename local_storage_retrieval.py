import json
import pandas as pd

# Phải có Firefox trong máy mới chạy được script này nhá
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager

driver = webdriver.Firefox(executable_path=GeckoDriverManager().install()) 
url='https://tiemchungcovid19.gov.vn/portal'
driver.get(url)

result = driver.execute_script("return window.localStorage.getItem('mapDataCountryLevel');")

data = json.loads(result)
with open('vaccination_data.json','w',encoding='utf-8') as f:
    json.dump(data,f,ensure_ascii=False)

df = pd.DataFrame.from_dict(data)
df.to_csv('vaccination.csv')