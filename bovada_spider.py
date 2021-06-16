import json
from spider import Spider
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import pandas as pd


class BovadaSpider(Spider):

    def __init__(self, driver, url):
        Spider.__init__(self, driver, url)
        self.df = pd.DataFrame(columns=['player_1', 'player_2', 'money_line_1', 'money_line_2', 'event_name'])
    
    def load(self):
        self.driver.get(self.url)
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'showMore')))
            print('Page loaded, ready for scraping')
        except:
            print('TimeOut')
        
        unloaded_groups = self.driver.find_elements_by_css_selector('.header-collapsible__icon.icon-plus')
        for group in unloaded_groups:
            group.click()
        self.scrape()

    def scrape(self):
        events = self.driver.find_elements_by_css_selector('.grouped-events')

        for event in events:
            event_name = event.find_elements_by_css_selector('a.league-header-collapsible__description')[0].text
            match_list = event.find_elements_by_css_selector('sp-coupon')
            for match in match_list:
                players = list(map(lambda p: p.text, match.find_elements_by_css_selector('.name')))
                odds_raw = list(map(lambda o: o.text, match.find_elements_by_css_selector('.empty-bet, .bet-price')))
                odds = list(map(lambda o: convert_american_to_decimal(o), odds_raw))

                player_1 = players[0]
                money_line_1 = odds[2]
                player_2 = players[1]
                money_line_2 = odds [3]

                match_data = {
                    'player_1': player_1,
                    'money_line_1': money_line_1,
                    'player_2': player_2,
                    'money_line_2': money_line_2,
                    'event_name' : event_name
                }
                self.df = self.df.append(match_data, ignore_index=True)

def convert_american_to_decimal(american_odd):
    if american_odd != '':
        if american_odd[0] == '-':
            decimal_odd = (1 + (100 / int(american_odd[1:])))
            return decimal_odd
        if american_odd[0] == '+':
            decimal_odd = (1 + (int(american_odd[1:]) / 100))
            return decimal_odd
        if american_odd == 'EVEN':
            return 2
        else:
            return None
    else:
        return None
    


if __name__ == '__main__':
    with open('./config.json') as f:
        config = json.load(f)
    driver = webdriver.Chrome(r'C:\Users\Kevin\Documents\Programming\chromedriver_win32\chromedriver.exe')
    bovada_spider = BovadaSpider(driver, config['sites']['bovada']['url'])
    bovada_spider.load()
    print(bovada_spider.df)
    driver.quit()
