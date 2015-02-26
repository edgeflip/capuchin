from capuchin.models import ESObject
from capuchin import config

class Post(ESObject):
    TYPE = config.POST_RECORD_TYPE
