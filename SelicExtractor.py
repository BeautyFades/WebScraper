from selenium import webdriver
from selenium.webdriver.chrome.options import Options  
from selenium.webdriver.common.by import By
import pandas as pd
import numpy as np
from time import sleep
from datetime import datetime
import os
from google.cloud import storage
import logging
from GenericExtractor import GenericExtractor
import config

if config.environment == 'dev':
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '.gitignore/keyfile.json'


log = logging.getLogger('app.sub')

class SelicExtractor(GenericExtractor):

    def __init__(self,
                webdriver_path: str = '/usr/bin/chromedriver/chromedriver'
                ):
        '''
            Class responsible for the Selic National rate extraction process. 

            :param str webdriver_path: Chrome webdriver's absolute path
        '''
        super().__init__()

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        self.driver = webdriver.Chrome(self.webdriver_path, options=chrome_options)
        self.driver.set_page_load_timeout(40)


    # Pythonic fixed-size list chunker
    def divide_chunks(self, l, n):
        for i in range(0, len(l), n): 
            yield l[i:i + n]


    def scrape(self) -> pd.DataFrame:
        log.info('Starting BCB-Selic scraper...')

        finished = 0
        while finished == 0:
            try:
                self.driver.get("https://www.bcb.gov.br/controleinflacao/historicotaxasjuros/")
                sleep(1)
                finished = 1
                log.info('Request finished successfully. Extracting table...')
            except Exception as e:
                sleep(1)
                log.error('Failed to finish request: ' + str(e))
                break


        raw_table = self.driver.find_elements(By.XPATH, f'//*[@id="historicotaxasjuros"]/tbody/tr/td')
        return raw_table

    def clean(self, table):

        COLS = ['n_reuniao', 'data_reuniao', 'vies_reuniao', 'datas_vigencia', 'meta_selic_aa', 'tban_am', 'taxa_selic_am', 'taxa_selic_aa']
        element_list = []

        for x in range (len(table)):
            # Primary data cleaning
            element_list.append(table[x].text.replace('º', '').replace('ex.', '').replace(' ', ''))
        
        self.driver.close()

        chunked_list = list(self.divide_chunks(element_list, 8))

        df = pd.DataFrame(chunked_list, columns=COLS)

        # Drop unused columns
        df = df.drop(columns=['vies_reuniao', 'tban_am'])

        # Split 'datas_vigencia' into a start date and an end date
        df[['data_inicio_vigencia', 'data_fim_vigencia']] = df['datas_vigencia'].str.split('-', n=1, expand=True)

        # Replace empty objects with NULL values
        df = df.replace('', np.nan)

        # Remove duplicate meetings where 'data_reuniao' is NULL
        df = df.dropna(subset=['data_reuniao'])

        # Drop unused column 'datas_vigencia'
        df = df.drop(['datas_vigencia'], axis=1)

        # Reorder dataframe
        df = df[['n_reuniao', 'data_reuniao', 'data_inicio_vigencia', 'data_fim_vigencia', 'meta_selic_aa', 'taxa_selic_aa', 'taxa_selic_am']]

        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)

        log.info('Extracted chunked list:')
        log.info(chunked_list)
        log.info('-----')
        log.info('First row example:')
        log.info(df.iloc[0])
        log.info('Table extracted and cleaned successfully!')


        return df

    
    def upload_to_gcs(self, 
                    dataframe: pd.DataFrame
                    ):
        
        dataframe.to_parquet(f'latest_output.parquet', index=False)

        try:
            log.info('Attempting upload to GCS...')
            gcs_client = storage.Client()
            bucket = gcs_client.get_bucket('economia-webscraper')

            file_name = datetime.today().strftime('%Y_%m_%d_' + 'selic.parquet')
            bucket.blob(f'bcb-selic/{file_name}').upload_from_filename('latest_output.parquet', content_type='application/octet-stream')
            log.info('Successfully uploaded to GCS! Finishing execution...')
        
        except Exception as e:
            log.error('Error uploading to GCS: ' + e)
