import humongolus as orm
from humongolus import field

class City(orm.Document):
    _db = "capuchin"
    _collection = "cities"

    _indexes = [
        orm.Index("zip", key=('zip', 1), unique=True),
        orm.Index("city", key=('city', 1)),
        orm.Index("state", key=('state', 1)),
        orm.Index("full_state", key=('state', 1)),
    ]

    zip = field.Char()
    state = field.Char()
    full_state = field.Char()
    city = field.Char()
    lat = field.Float()
    lng = field.Float()
