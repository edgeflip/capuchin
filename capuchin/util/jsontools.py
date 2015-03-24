import json
import datetime
import time
from bson.objectid import ObjectId
from humongolus.field import DocumentId, DynamicDocument
from humongolus import Lazy

class JavascriptEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            try:
                return (time.mktime(obj.timetuple())+(obj.microsecond/1000000.0))*1000
            except:
                pass
        if isinstance(obj, ObjectId): return str(obj)
        if not isinstance(obj, (DocumentId, DynamicDocument, Lazy)):
            try:
                return obj.json()
            except:
                return str(obj)
