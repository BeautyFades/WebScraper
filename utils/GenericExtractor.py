import os
import logging
import config as config
import pandas as pd
from google.cloud import storage
from google.oauth2 import service_account


class GenericExtractor():

    def __init__(self, 
                webdriver_path: str = '/usr/bin/chromedriver/chromedriver', 
                ):
        '''
            Base class for webscraper extractor instances. 

            :param str webdriver_path: Chrome Webdriver's absolute path. Default: '/usr/bin/chromedriver/chromedriver'
        '''

        self.webdriver_path = webdriver_path


    def convert_df_to_parquet(self, df: pd.DataFrame, file_path: str) -> None:
        try:
            return df.to_parquet(file_path, index=False)
        except Exception as e:
            logging.error('Failed to convert to .parquet: ' + str(e))
            raise Exception


    def upload_file_to_gcs(self,
                        bucket_name: str, 
                        file_path_in_bucket: str, 
                        local_file_path: str, 
                        content_type: str = 'application/octet-stream', 
                        creds: service_account.Credentials = None
                        ) -> None:

        logging.info(f'Uploading {local_file_path} to GCS as {file_path_in_bucket} on bucket {bucket_name}.')

        try:
            gcs_client = storage.Client(creds)
            bucket = gcs_client.get_bucket(bucket_name)
            return bucket.blob(file_path_in_bucket).upload_from_filename(local_file_path, 
                                                    content_type=content_type)
                                                    
        
        except Exception as e:
            logging.error('Failed to upload: ' + str(e))
            raise Exception