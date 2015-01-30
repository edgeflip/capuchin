import logging
logging.basicConfig(level=logging.INFO)
from capuchin import Capuchin
from flask_pjax import PJAX
app = Capuchin()
PJAX(app)
logging.info("running")
