from werkzeug.wsgi import peek_path_info
from capuchin import config
from capuchin.app import Capuchin
import logging

def create_app():
    logging.info("Initializing")
    try:
        _app = Capuchin()
        _app.configure_dbs()
    except Exception as e:
        logging.exception(e)
    def app(env, start_response):
        if peek_path_info(env) == "healthcheck":
            _app.config['SERVER_NAME'] = None
        else:
            _app.config['SERVER_NAME'] = config.SERVER_NAME

        return _app(env, start_response)

    logging.info("Running")
    return app

app = create_app()
