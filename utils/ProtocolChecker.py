from selenium import webdriver
from selenium.webdriver.chrome.options import Options  
from selenium.webdriver.common.by import By
from time import sleep
import os
import logging
from utils.GenericExtractor import GenericExtractor
import utils.config as config

class ProtocolChecker(GenericExtractor):

    def __init__(self):
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
        self.driver.set_page_load_timeout(30)

    
    def print_screen(self):
        logging.info('Requesting IP information...')

        finished = 0
        while finished == 0:
            try:
                self.driver.get("https://www.iplocation.net/")
                sleep(1)
                finished = 1
                logging.info('Request finished successfully.')
            except Exception as e:
                sleep(1)
                logging.error('Failed to finish request: ' + str(e))
                raise e

        sleep(2)
        self.driver.save_screenshot('latest_ip_info.png')
        return True
