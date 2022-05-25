from flask import Flask, request, Response
import logging, sys
from SelicExtractor import SelicExtractor
import config
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] | [%(levelname)s] >>> %(message)s', 
                              '%Y-%m-%d %H:%M:%S %Z')
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)


app = Flask('app')


def get_client_ip_address():
    return request.remote_addr

@app.route("/", methods=["GET"])
def health_check():
    return Response(
            "[{'returnStatus': 'success'}, {'statusCode': '200'}, {'message': 'alive'}]", 
            status=200, 
            mimetype='application/json'
        )

@app.route("/run", methods=["GET"])
def extract_from_bcb():
    app.logger.info(f'BCB-Selic scraper received /run request from {get_client_ip_address()}.')
    selic_extractor = SelicExtractor()

    try:
        raw = selic_extractor.scrape()
        selic_df = selic_extractor.clean(raw)
        selic_extractor.convert_df_to_parquet(selic_df, 'output.parquet')

        file_name_on_gcs = datetime.today().strftime('%Y_%m_%d_' + 'selic.parquet')

        selic_extractor.upload_file_to_gcs('economia-webscraper', f'bcb-selic/{file_name_on_gcs}', 'output.parquet')
        app.logger.info(f'Finished scraper execution.')
        
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
