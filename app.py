from flask import Flask, request, Response
from SelicExtractor import SelicExtractor
import config
from datetime import datetime
from Logger import ScraperLogger
import logging

ScraperLogger()

app = Flask('app')


def get_client_ip_address():
    return request.remote_addr

@app.route("/", methods=["GET"])
def health_check():
    logging.info(f'BCB-Selic scraper received / request from {get_client_ip_address()}. Health checking...')
    return Response(
            "[{'returnStatus': 'success'}, {'statusCode': '200'}, {'message': 'alive'}]", 
            status=200, 
            mimetype='application/json'
        )

@app.route("/run", methods=["GET"])
def extract_from_bcb():
    logging.info(f'BCB-Selic scraper received /run request from {get_client_ip_address()}.')
    selic_extractor = SelicExtractor()

    try:
        raw = selic_extractor.scrape()
        selic_df = selic_extractor.clean(raw)
        selic_extractor.convert_df_to_parquet(selic_df, 'output.parquet')

        file_name_on_gcs = datetime.today().strftime('%Y_%m_%d_' + 'selic.parquet')

        selic_extractor.upload_file_to_gcs('economia-webscraper', f'bcb-selic/{file_name_on_gcs}', 'output.parquet')
        logging.info(f'Finished scraper execution.')
        
        return Response(
            "[{'returnStatus': 'success'}, {'statusCode': '200'}]", 
            status=200, 
            mimetype='application/json'
        )

    except Exception as e:
        return Response(
            "[{'returnStatus': 'fail'}, {'statusCode': '500'}, {'message': "+str(e)+"}]", 
            status=500, 
            mimetype='application/json'
        )
