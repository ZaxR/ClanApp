from app import db
import datetime


class Users(db.Model):
    __tablename__ = "users"
    id = db.Column('user_id', db.Integer, primary_key=True)
    username = db.Column('username', db.String(20), unique=True, index=True)
    password = db.Column('password', db.String(10))
    email = db.Column('email', db.String(50), unique=True, index=True)
    registered_on = db.Column('registered_on', db.DateTime)

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email
        #self.registered_on = datetime.utcnow()

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return #unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.username)


class Accounts(db.Model):
    __tablename__ = "accounts"
    id = db.Column(db.Integer, primary_key=True)
    rsn = db.Column(db.String(15), index=True, unique=False)

    def __init__(self, rsn):
        self.rsn = rsn
        self.past_rsns = []
        self.version = "RS3"
        self.inClan = "Yes"
        self.rank = None # How do I inherit this value from the Player who owns this account?
        self.caps = {}  # its own class?; wk number: 1/5 options from rank sheet
        self.recruits = {}  # its own class?: recruit_transaction_id: date, recruit_name, enter/leave, points?
        self.events = {}  # its own class?: event_transaction_id: begin_date, end_date, [participants], points?
        self.clanXp = 0  # pull live from latest db entry


class Caps(db.Model):
    __tablename__ = "caps"
    id = db.Column(db.Integer, primary_key=True)
    capdate = db.Column(db.String(15), index=True, unique=False)  # db.Column(db.DateTime)
    week = db.Column(db.String(15), index=True, unique=False)
    rsn = db.Column(db.String(15), index=True, unique=False)
    captype = db.Column(db.Integer, index=True, unique=False)

    def __init__(self, capdate, week, rsn, captype):
        self.capdate = capdate
        self.week = week
        self.rsn = rsn
        self.captype = captype

    def serialize(self):
        return {
            'capdate': self.capdate,
            'week': self.week,
            'rsn': self.rsn,
            'captype': self.captype
        }