import humongolus as orm
import humongolus.field as field
from passlib.apps import custom_app_context as pwd_context

class FacebookPage(orm.EmbeddedDocument):
    category = field.Char()
    name = field.Char()
    access_token = field.Char()
    id = field.Integer()
    perms = orm.List(type=unicode)
    default = field.Boolean(default=False)

class Client(orm.Document):
    _db = "capuchin"
    _collection = "clients"

    _indexes = [
        orm.Index('name', key=('name', 1), unique=True),
    ]

    name = field.Char()
    description = field.Char()
    facebook_pages = orm.List(type=FacebookPage)

class Admin(orm.Document):
    _db = "capuchin"
    _collection = "client_admins"
    _indexes = [
        orm.Index('email', key=('email', 1), unique=True),
    ]

    name = field.Char()
    email = field.Char()
    password = field.Char()
    last_login = field.Date()
    client = field.DocumentId(type=Client)

    @staticmethod
    def passwords_match(pwd, cpwd):
        if pwd == cpwd: return True
        return False

    def save(self):
        self.password = pwd_context.encrypt(self.password, category='admin')
        return super(Admin, self).save()

    def verify_pwd(self, pwd):
        if pwd_context.verify(pwd, self.password): return True
        return False

    def is_authenticated(self):
        if self._id: return True
        return False

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        self.logger.info(unicode(self._id))
        return unicode(self._id)
