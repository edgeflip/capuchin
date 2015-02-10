def app(env, start_response):
    import os
    from werkzeug.wsgi import peek_path_info
    from capuchin import Capuchin
    from capuchin import config
    _app = Capuchin()
    os.environ['SERVER_NAME'] = env['SERVER_NAME']
    if peek_path_info(env) == "healthcheck":
        _app.config['SERVER_NAME'] = None
    else:
        _app.config['SERVER_NAME'] = config.SERVER_NAME

    return _app(env, start_response)
