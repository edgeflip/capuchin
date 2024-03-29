from flask import url_for, request
from capuchin.util.pagination import Pagination
from capuchin.util.jsontools import JavascriptEncoder
import random
import json
import logging
import math

class Column(object):

    def __init__(self, field, title, cls="", sortable=False, formatter=None):
        self.field = field
        self.title = title
        self.sortable = sortable
        self.formatter = formatter if formatter else lambda v, r: v
        self.cls = cls

    def th(self, cls, id, sort, **kwargs):
        v = self.title
        if self.sortable:
            if sort:
                s_dir = 'desc' if sort[1] == 'asc' else 'asc'
            else:
                s_dir = 'asc'
            link = url_for(
                'tables.index',
                cls=cls,
                field=self.field,
                dir=s_dir,
                **kwargs
            )
            v = u'<a class="table_sort" data-id="{}" href="{}">{}</a>'.format(id, link, v)
        return u"<th>{}</th>".format(v)

    def td(self, value, record):
        c = u"class=\"{}\"".format(self.cls) if self.cls else ""
        return u"<td {}>{}</td>".format(c, self.formatter(value, record))

class Table(object):

    cls = None
    columns = []

    def __init__(self, client, obj=None, records=None, raw=None):
        self.client = client
        self.records = records
        self.obj = obj
        self.raw = raw
        self.total = len(self.records) if self.records else 0

    def build_pagination(self, cls, id, sort, from_, size, total, **kwargs):
        if not self.pagination: return ""
        if total <= size: return ""
        try:
            current_page=int(math.ceil(from_/size))+1
        except:
            current_page=1
        pagination = Pagination(current_page, size, total)
        pages = ["<nav><ul class=\"pagination\">"]
        field = sort[0] if sort else '_id'
        dir = sort[1] if sort else 'desc'
        for page in pagination.iter_pages():
            if page:
                if page != pagination.page:
                    pages.append("<li><a class=\"pager\" data-id=\"{}\"href=\"{}\">{}</a></li>".format(
                        id,
                        url_for(
                            'tables.index',
                            cls=cls,
                            obj=self.obj,
                            field=field,
                            dir=dir,
                            page=page,
                            size=size,
                            **kwargs
                        ),
                        page)
                    )
                else:
                    pages.append("<li><a class='pager' href=\"#\">{}</a></li>".format(page))
            else:
                pages.append("<li><a class='pager'>...</a></li>")
        if pagination.has_next:
            pages.append("<li><a class=\"pager\" data-id=\"{}\" href=\"{}\">{}</a></li>".format(
                id,
                url_for(
                    'tables.index',
                    cls=cls,
                    obj=self.obj,
                    field=field,
                    dir=dir,
                    page=pagination.page+1,
                    size=size,
                    **kwargs
                ),
                "Next &raquo;")
            )
        pages.append("</ul></nav>")
        return u"".join(pages)

    def get_records(self, q, from_, size, sort):
        records = self.records if self.records else self.cls.records(self.client, q, from_, size, sort)
        total = records.total
        return records, total

    def tr(self, record):
        url = record.url
        id = record.id
        url_attribute = u' data-url="{}"'.format(url) if url else ''
        object_attribute = u' data-object="{}"'.format(id) if id else ''
        return u'<tr{}{}>'.format(object_attribute, url_attribute)

    def build_rows(self, records):
        tr = []
        for record in records.hits:
            td = [self.tr(record)]
            for column in self.columns:
                value = record
                for level in column.field.split("."):
                    value = value.get(level, {})
                td.append(column.td(value, record))
            td.append(u"</tr>")
            tr.append(u"".join(td))
        return tr

    def render(self, q="*", from_=0, size=10, sort=None, pagination=True):
        self.pagination = pagination
        url = request.base_url
        records, total = self.get_records(q, from_, size, sort)
        me = ".".join("{}.{}".format(
            self.__module__,
            self.__class__.__name__
        ).split(".")[3:])
        id = u"table{}".format(random.randint(9999, 99999999))
        q_encoded = json.dumps(q, cls=JavascriptEncoder)
        th = [c.th(me, id, sort,
                   obj=self.obj,
                   q=q_encoded,
                   from_=0,
                   size=size,
                   pagination=pagination,
                   url=url) for c in self.columns]
        tr = self.build_rows(records)
        to = from_+size if total >= from_+size else total
        info = u'<div class="table-info"><span class="total"><span class="pagination-info">{} - {} of {}</span></div>'.format(
            from_ + 1,
            to,
            total
        )
        table = info + (
            u'<div class=table-responsive>'
            u'<table class="table table-striped table-hover table-compact" data-source="{}">'
            u'<thead><tr>{}</tr></thead><tbody>{}</tbody></table></div>'
            .format(
                url_for(
                    'tables.index',
                    cls=me,
                    field=sort and sort[0],
                    dir=sort and sort[1],
                    obj=self.obj,
                    q=q_encoded,
                    from_=from_,
                    size=size,
                    pagination=pagination,
                    url=url
                ),
                u"".join(th),
                u"".join(tr),
            )
        )
        pagination = self.build_pagination(me, id, sort, from_=from_, size=size, total=total, q=json.dumps(q, cls=JavascriptEncoder), pagination=self.pagination, url=url)
        return u"<div id=\"{}\">{}{}</div>".format(id, table, pagination)


class MongoTable(Table):

    def get_records(self, q, from_, size, sort):
        q = q if q and q!="*" else {}
        q.update({'client':self.client._id})
        logging.debug("MONGO QUERY: {}".format(q))

        if sort:
            sort = [(sort[0], 1 if sort[1] == 'asc' else -1)]
        else:
            sort = [('created', -1)]

        records = self.cls.find(q).sort(sort).skip(int(from_)).limit(int(size))
        total = records.count()
        return records, total

    def build_rows(self, records):
        tr = []
        for record in records:
            td = [self.tr(record)]
            for column in self.columns:
                levels = column.field.split(".")
                value = record
                for level in levels:
                    value = getattr(value, level, '')
                td.append(column.td(value, record))
            td.append(u"</tr>")
            tr.append(u"".join(td))
        return tr
