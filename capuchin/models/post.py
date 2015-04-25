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

    @property
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
