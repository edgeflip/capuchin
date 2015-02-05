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

class SocialAccount(orm.EmbeddedDocument):
    TWITTER = 'twitter'
    FACEBOOK = 'fb'
    GOOGLE = 'google'
    LINKEDIN = 'linkedin'

    type = field.Char()
    username = field.Char()
    id = field.Char()
    token = field.Char()
    secret = field.Char()
    avatar = field.Char()
    app_id = field.Char()
    permissions = orm.List(type=unicode)

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
    social_accounts = orm.List(type=SocialAccount)

    def social_account(self, account_type=None):
        for sa in self.social_accounts:
            if sa.type == account_type: return sa
        sa = SocialAccount()
        sa.type = account_type
        return sa

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
