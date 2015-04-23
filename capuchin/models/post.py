from capuchin.models import ESObject, escape_query
from capuchin import config, db
from flask import url_for


class Post(ESObject):
    TYPE = config.POST_RECORD_TYPE

    class Search(object):
        index = config.ES_INDEX
        doc_type = 'post'
        query_fields = ['_all']
        return_fields = ['_id']

    @classmethod
    def filter(cls, client, q, sort):
        q = {
            "query": {
                "query_string": {
                    "default_field": "message",
                    "query": q
                }
            },
            "filter": {
                "term": {
                    "client": str(client._id)
                }
            },
            "sort": sort
        }
        return q

    @classmethod
    def search(cls, client, query, size=10, start=0):
        q = {
            "query":{
                "filtered":{
                    "query":{
                        "query_string":{
                            "fields":cls.Search.query_fields,
                            "query":escape_query(query),
                        }
                    },
                    "filter":{
                        "term":{
                            "client":str(client._id)
                        }
                    }
                }
            }
        }
        ES = db.init_elasticsearch()
        res = ES.search(
            index=cls.Search.index,
            doc_type=cls.Search.doc_type,
            body=q,
            from_=start,
            size=size
        )
        return res

    def url(self):
        return url_for('engagement.view', id=self.id)

    @staticmethod
    def _split_id(full_id):
        return full_id.split('_')

    @classmethod
    def make_fb_url(cls, full_id):
        (page_id, post_id) = cls._split_id(full_id)
        return 'https://facebook.com/{}/posts/{}'.format(page_id, post_id)

    @property
    def page_id(self):
        (page_id, _post_id) = self._split_id(self.id)
        return page_id

    @property
    def fbid(self):
        (_page_id, post_id) = self._split_id(self.id)
        return post_id
