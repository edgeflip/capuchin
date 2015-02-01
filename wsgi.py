try:
    import logging
    logging.basicConfig(level=logging.DEBUG)
    from capuchin import Capuchin
    from flask_pjax import PJAX
    app = Capuchin()
    PJAX(app)
    logging.info("running")
except Exception as e:
    logging.exception(e)
