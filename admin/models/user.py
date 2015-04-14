import humongolus as orm
import humongolus.field as field
from capuchin.util import password
from slugify import slugify

class User(orm.Document):
    _db = "capuchin_admin"
    _collection = "users"
    _indexes = [
        orm.Index('email', key=('email', 1), unique=True),
    ]

    name = field.Char()
    email = field.Char()
    password = field.Char()
    last_login = field.Date()

    @staticmethod
    def passwords_match(pwd, cpwd):
        if pwd == cpwd: return True
        return False

    def save(self):
        if not password.identify(self.password):
            self.password = password.encrypt_password(self.password)
        return super(User, self).save()

    def verify_pwd(self, pwd):
        return password.check_password(pwd, self.password)

    def is_authenticated(self):
        if self._id: return True
        return False

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self._id)
