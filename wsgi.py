from werkzeug.wsgi import peek_path_info
from werkzeug.wsgi import DispatcherMiddleware
from capuchin import config as capuchin_config
from capuchin.app import Capuchin
from admin.app import CapuchinAdmin
from gevent import monkey
import logging

monkey.patch_all()

def create_capuchin_app():
    logging.info("Initializing Capuchin")
    def app(env, start_response):
        _app = Capuchin()
        if peek_path_info(env) == "healthcheck":
            _app.config['SERVER_NAME'] = None
        else:
            _app.config['SERVER_NAME'] = capuchin_config.SERVER_NAME

        return _app(env, start_response)

    logging.info("Capuchin Running")
    return app

def create_admin_app():
    logging.info("Initializing Admin")
    def app(env, start_response):
        _app = CapuchinAdmin()
        return _app(env, start_response)

    logging.info("Admin Running")
    return app

app = DispatcherMiddleware(create_capuchin_app(), {
    '/admin': create_admin_app()
})
