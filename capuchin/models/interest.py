import humongolus as orm
import humongolus.field as field

class Interest(orm.Document):
    _db = "capuchin"
    _collection = "interests"

    name = field.Char()
