import json
import ast

def parse_email(val):
    try:
        handle = val.split("@")[0]
        domain = val.split("@")[-1]
    except:
        handle = None
        domain = None
    return {
        "email":val,
        "handle":handle,
        "domain":domain
    }

def parse_array(val):
    try:
        v = ast.literal_eval(val)
        if isinstance(v, basestring):
            print "still string!"
            print v
            v = json.loads(v)
            return v
        return v
    except Exception as e: pass

    try:
        v = json.loads(val)
        return v
    except: pass

    return None

def split(val):
    return val.split(" ")

class User(dict):
    key_parsers = {
        "quotes":parse_array,
        "music":parse_array,
        "affiliations":parse_array,
        "devices":parse_array,
        "books":parse_array,
        "tv":parse_array,
        "sports":parse_array,
        "languages":parse_array,
        "interests":parse_array,
        "movies":parse_array,
        "email": parse_email,
        "top_words": split
    }

    def __init__(self, obj):
        super(User, self).__init__()
        self.parse(obj)

    def parse(self, obj):
        for k,v in obj.iteritems():
            if k in self.key_parsers:
                try:
                    v = self.key_parsers[k](v)
                except Exception as e: pass

            v = None if not v else v
            self[k] = v
