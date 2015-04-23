import humongolus as orm
import humongolus.field as field
from capuchin.util import password
from slugify import slugify

class Slug(orm.Field):

    def clean(self, val, doc=None):
        return slugify(val)

class Competitor(orm.EmbeddedDocument):
    id = field.Char()
    name = field.Char()

class PageCategory(orm.EmbeddedDocument):
    id = field.Char()
    name = field.Char()

class SocialAccount(orm.EmbeddedDocument):
    TWITTER = 'twitter'
    FACEBOOK = 'facebook'
    GOOGLE = 'google'
    LINKEDIN = 'linkedin'

    type = field.Char()
    id = field.Char()
    name = field.Char()
    app_id = field.Char()
    token = orm.Field()
    secret = field.Char()
    avatar = field.Char()
    permissions = orm.List(type=unicode)
    categories = orm.List(type=PageCategory)
    last_sync = field.Date()

    def __call__(self, *args, **kwargs):
        data = kwargs.pop('data', {})
        self._map(data)
        return self

class FacebookPage(orm.EmbeddedDocument):
    name = field.Char()
    token = field.Char()
    id = field.Char()
    permissions = orm.List(type=unicode)
    categories = orm.List(type=PageCategory)

class SocialAccounts(orm.List):

    def __getattr__(self, account_type):
        for a in self:
            if a.type == account_type: return a
        a = SocialAccount()
        a.type = account_type
        self.append(a)
        return a

class Client(orm.Document):
    _db = "capuchin"
    _collection = "clients"

    _indexes = [
        orm.Index('name', key=('name', 1), unique=True),
    ]

    name = field.Char()
    slug = Slug()
    description = field.Char()
    social = SocialAccounts(type=SocialAccount)
    competitors = orm.List(type=Competitor)
    last_post = field.Date()


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
    social = SocialAccounts(type=SocialAccount)
    facebook_pages = orm.List(type=FacebookPage)

    @staticmethod
    def passwords_match(pwd, cpwd):
        if pwd == cpwd: return True
        return False

    def save(self):
        if not password.identify(self.password):
            self.password = password.encrypt_password(self.password)
        return super(Admin, self).save()

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
        self.logger.info(unicode(self._id))
        return unicode(self._id)

class AccountToken(orm.Document):
    _db = "capuchin"
    _collection = "account_tokens"

    admin = field.DocumentId(type=Admin)

Client.admins = orm.Lazy(type=Admin, key='client')


class Message(orm.Document):
    _db = "capuchin"
    _collection = "client_messages"
    _indexes = [
        orm.Index('read', key=('read', 1)),
    ]

    text = field.Char()
    link = field.Char()
    client = field.DocumentId(type=Client)
    read = field.Date()

Client.messages = orm.Lazy(type=Message, key='client')
