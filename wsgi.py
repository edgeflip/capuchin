from werkzeug.wsgi import peek_path_info
from capuchin import config
from capuchin import db
from capuchin.app import Capuchin
from gevent import monkey
import logging

monkey.patch_all()

def create_app():
    logging.info("Initializing")
    def app(env, start_response):
        _app = Capuchin()
        if peek_path_info(env) == "healthcheck":
            _app.config['SERVER_NAME'] = None
        else:
            _app.config['SERVER_NAME'] = config.SERVER_NAME

        return _app(env, start_response)

    logging.info("Running")
    return app

app = create_app()
