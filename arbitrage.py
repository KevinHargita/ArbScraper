import json
import pandas as pd
from selenium import webdriver
from bovada_spider import BovadaSpider
from betonline_spider import BetonlineSpider

if __name__ == '__main__':
    with open('./config.json') as f:
        config = json.load(f)
    driver = webdriver.Chrome(r'C:\Users\Kevin\Documents\Programming\chromedriver_win32\chromedriver.exe')
    
    #bovada
    bovada_spider = BovadaSpider(driver, config['sites']['bovada']['url'])
    bovada_spider.load()
    print(bovada_spider.df)

    #betonline
    betonline_spider = BetonlineSpider(driver, config['sites']['betonline']['url'])
    betonline_spider.load()
    print(betonline_spider.df)

    merged_df = pd.merge(bovada_spider.df, betonline_spider.df, on=['player_1', 'player_2'], suffixes=('_bovada', '_betonline'))
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(merged_df)

    driver.quit()
