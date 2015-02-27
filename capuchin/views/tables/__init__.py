from flask import url_for
import random

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
        return "<th>{}</th>".format(v)

    def td(self, value, record):
        c = "class=\"{}\"".format(self.cls) if self.cls else ""
        return "<td {}>{}</td>".format(c, self.formatter(value, record))

class Table(object):
    cls = None
    columns = []

    def __init__(self, client):
        self.client = client

    def render(self, q="*", from_=0, size=10, sort=None):
        records = self.cls.records(self.client, q, from_, size, sort)
        me = "{}.{}".format(
            self.__module__,
            self.__class__.__name__
        )
        id = "{}{}".format("table", random.randint(9999, 99999999))
        th = [c.th(me, id, sort, q=q, from_=from_, size=size) for c in self.columns]
        tr = []
        for r in records.hits:
            td = ["<tr>"]
            for c in self.columns:
                levels = c.field.split(".")
                val = r
                for i in levels: val = val.get(i, {})
                td.append(c.td(val, r))
            td.append("</tr>")
            tr.append("".join(td))
        return "<table id=\"{}\" class=\"table\"><thead><tr>{}</tr></thead><tbody>{}</tbody></table>".format(
            id,
            "".join(th),
            "".join(tr)
        )
