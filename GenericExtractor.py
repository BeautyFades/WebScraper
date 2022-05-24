import os
import logging
import config

if config.environment == 'dev':
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '.gitignore/keyfile.json'


log = logging.getLogger('app.sub')

class GenericExtractor():
    def __init__(self, 
                webdriver_path: str = '/usr/bin/chromedriver/chromedriver', 
                ):
        '''
            Base class for webscraper extractor instances. 

            :param str webdriver_path: Chrome Webdriver's absolute path. Default: '/usr/bin/chromedriver/chromedriver'
        '''

        self.webdriver_path = webdriver_path

