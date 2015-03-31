from capuchin.models import ESObject
from capuchin import config
from flask import url_for


class Post(ESObject):
    TYPE = config.POST_RECORD_TYPE

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

    def url(self):
        return url_for('engagement.view', id=self.id)

    def _idparts(self):
        return self.id.split('_')

    @property
    def page_id(self):
        (page_id, _post_id) = self._idparts()
        return page_id

    @property
    def fbid(self):
        (_page_id, post_id) = self._idparts()
        return post_id
