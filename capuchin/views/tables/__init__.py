from flask import url_for
import random
import json

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

    def get_records(self, q, from_, size, sort):
        return self.records if self.records else self.cls.records(self.client, q, from_, size, sort)

    def build_rows(self, records):
        tr = []
        for r in records.hits:
            td = [u"<tr>"]
            for c in self.columns:
                levels = c.field.split(".")
                val = r
                for i in levels: val = val.get(i, {})
                td.append(c.td(val, r))
            td.append(u"</tr>")
            tr.append(u"".join(td))

        return tr

    def render(self, q="*", from_=0, size=10, sort=None):
        records = self.get_records(q, from_, size, sort)
        me = "{}.{}".format(
            self.__module__,
            self.__class__.__name__
        )
        id = u"{}{}".format("table", random.randint(9999, 99999999))
        th = [c.th(me, id, sort, q=json.dumps(q), from_=from_, size=size) for c in self.columns]
        tr = self.build_rows(records)
        return u"<table id=\"{}\" class=\"table table-striped\"><thead><tr>{}</tr></thead><tbody>{}</tbody></table>".format(
            id,
            u"".join(th),
            u"".join(tr)
        )

class MongoTable(Table):

    def get_records(self, q, from_, size, sort):
        q = q if q and q!="*" else {}
        if sort:
            d = 1 if sort[1]=='asc' else -1
            sort = [(sort[0], d)]

        sort = sort if sort else [('_id',1)]
        records = self.cls.find(q).sort(sort).skip(int(from_)).limit(int(size))
        return records

    def build_rows(self, records):
        tr = []
        for r in records:
            td = [u"<tr>"]
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
