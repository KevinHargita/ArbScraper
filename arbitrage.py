import json
import pandas as pd
import time
from selenium import webdriver
from bovada_spider import BovadaSpider
from betonline_spider import BetonlineSpider

if __name__ == '__main__':
    with open('./config.json') as f:
        config = json.load(f)
    driver = webdriver.Chrome('./chromedriver.exe')

    arb_found = False
    while not arb_found:
        #bovada
        bovada_spider = BovadaSpider(driver, config['sites']['bovada']['url'])
        bovada_spider.load()

        #betonline
        betonline_spider = BetonlineSpider(driver, config['sites']['betonline']['url'])
        betonline_spider.load()

        merged_df = pd.merge(bovada_spider.df, betonline_spider.df, on=['player_1', 'player_2'], suffixes=('_bovada', '_betonline'))
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
            print(merged_df)

        calc_df = merged_df
        calc_df['percent_1'] = calc_df.apply(lambda row: (1 / max(row['money_line_1_bovada'], row['money_line_1_betonline'])) * 100, axis=1)
        calc_df['percent_2'] = calc_df.apply(lambda row: (1 / max(row['money_line_2_bovada'], row['money_line_2_betonline'])) * 100, axis=1)
        calc_df['percent_total'] = calc_df.apply(lambda row: row['percent_1'] + row['percent_2'], axis=1)
        calc_df['is_arb'] = calc_df.apply(lambda row: (row['percent_total'] < 100), axis=1)
        print(calc_df)

        final_df = calc_df.loc[calc_df['is_arb'] == True]
        if not final_df.empty:
            arb_found = True
            print(final_df)
        else:
            print('No arb found')
            time.sleep(600)
    driver.quit()
