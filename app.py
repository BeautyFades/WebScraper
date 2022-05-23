from flask import Flask, request, Response
import logging, sys
from SelicExtractor import SelicExtractor

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
    selic_extractor = SelicExtractor(
                    webdriver_path='/usr/bin/chromedriver/chromedriver'
                    )

    try:
        selic_df = selic_extractor.scrape()
        selic_extractor.upload_to_gcs(selic_df)
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
