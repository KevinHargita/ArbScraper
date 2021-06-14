import json
from spider import Spider
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import pandas as pd

class BetonlineSpider(Spider):
    def __init__(self, driver, url):
        Spider.__init__(self, driver, url)
        self.df = pd.DataFrame(columns=['player_1', 'player_2', 'money_line_1', 'money_line_2', 'event_name'])
    
    def load(self):
        self.driver.get(self.url)
        try:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.middle-category__sport[data-group="Tennis"]+ul')))
        except Exception as e:
            print(e)
        event_pages = self.driver.find_elements_by_css_selector('a.middle-category__sport[data-group="Tennis"]+ul a.last-category__button-text[href*="/tennis/"]')
        self.scrape(list(map(lambda e: {
                'url' : e.get_attribute('href'),
                'event_name' : e.get_attribute('data-content')
            }, event_pages))
        )

    def scrape(self, event_pages):
        for event in event_pages:
            self.driver.get(event['url'])
            try:
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.offering-games__dategroup-content')))
            except Exception as e:
                print(e)
            match_list = self.driver.find_elements_by_css_selector('.offering-games__timegroup-content')
            for match in match_list:
                players = list(map(lambda p: p.text, match.find_elements_by_css_selector('td.lines-row__team-name span:first-child')))
                odds_raw = list(map(lambda o: o.text, match.find_elements_by_css_selector('td.lines-row__money div.bet-pick__wager-line')))
                odds = list(map(lambda o: convert_american_to_decimal(o), odds_raw))

                if len(odds) != 0:
                    player_1 = ' '.join(players[1].split(', ')[::-1])
                    money_line_1 = odds[1]
                    player_2 = ' '.join(players[0].split(', ')[::-1])
                    money_line_2 = odds [0]

                    match_data = {
                        'player_1': player_1,
                        'money_line_1': money_line_1,
                        'player_2': player_2,
                        'money_line_2': money_line_2,
                        'event_name' : event['event_name']
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
        else:
            return None
    else:
        return None

        
if __name__ == '__main__':
    with open('./config.json') as f:
        config = json.load(f)
    driver = webdriver.Chrome(r'C:\Users\Kevin\Documents\Programming\chromedriver_win32\chromedriver.exe')
    betonline_spider = BetonlineSpider(driver, config['sites']['betonline']['url'])
    betonline_spider.load()
    print(betonline_spider.df)
    driver.quit()