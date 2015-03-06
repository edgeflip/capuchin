from flask import url_for
from capuchin.util.pagination import Pagination
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
                'tables.sort',
                cls=cls,
                field=self.field,
                dir=s_dir,
                **kwargs
            )
            v = "<a class=\"table_sort\" data-id=\"{}\" href=\"{}\">{}</a>".format(id, link, v)
        return u"<th>{}</th>".format(v)

    def td(self, value, record):
        c = u"class=\"{}\"".format(self.cls) if self.cls else ""
        return u"<td {}>{}</td>".format(c, self.formatter(value, record))

class Table(object):
    cls = None
    columns = []

    def __init__(self, client, records=None):
        self.client = client
        self.records = records

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
                            'tables.page',
                            cls=cls,
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
                    'tables.page',
                    cls=cls,
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

    def build_rows(self, records):
        tr = []
        for r in records.hits:
            logging.info(type(r))
            td = [u"<tr data-url=\"{}\">".format(r.url())]
            for c in self.columns:
                levels = c.field.split(".")
                val = r
                for i in levels: val = val.get(i, {})
                td.append(c.td(val, r))
            td.append(u"</tr>")
            tr.append(u"".join(td))

        return tr

    def render(self, q="*", from_=0, size=10, sort=None, pagination=True):
        self.pagination = pagination
        records, total = self.get_records(q, from_, size, sort)
        me = ".".join("{}.{}".format(
            self.__module__,
            self.__class__.__name__
        ).split(".")[3:])
        id = u"{}{}".format("table", random.randint(9999, 99999999))
        th = [c.th(me, id, sort, q=json.dumps(q), from_=0, size=size, pagination=pagination) for c in self.columns]
        tr = self.build_rows(records)
        table =  u" <table class=\"table table-striped table-hover\"><thead><tr>{}</tr></thead><tbody>{}</tbody></table>".format(
            u"".join(th),
            u"".join(tr)
        )
        pagination = self.build_pagination(me, id, sort, from_=from_, size=size, total=total, q=json.dumps(q))
        return u"<div id=\"{}\">{}{}</div>".format(id, table, pagination)

class MongoTable(Table):

    def get_records(self, q, from_, size, sort):
        q = q if q and q!="*" else {}
        if sort:
            d = 1 if sort[1]=='asc' else -1
            sort = [(sort[0], d)]

        sort = sort if sort else [('_id',1)]
        records = self.cls.find(q).sort(sort).skip(int(from_)).limit(int(size))
        total = records.count()
        return records, total

    def build_rows(self, records):
        tr = []
        for r in records:
            td = [u"<tr data-url=\"{}\">".format(r.url)]
            for c in self.columns:
                levels = c.field.split(".")
                val = r
                for i in levels:
                    try:
                        val = getattr(val, i)
                    except:
                        val = ""
                td.append(c.td(val, r))
            td.append(u"</tr>")
            tr.append(u"".join(td))

        return tr
