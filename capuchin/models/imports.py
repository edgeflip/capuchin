import humongolus as orm
import humongolus.field as field

class ImportOrigin(orm.Document):
    _db = "capuchin"
    _collection = "import_origin"

    name = field.Char()
