from werkzeug.security import generate_password_hash, check_password_hash
from app import db
import datetime


class Users(db.Model):
    __tablename__ = "users"
    id = db.Column('user_id', db.Integer, primary_key=True)
    username = db.Column('username', db.String(50), unique=True, index=True)
    password_hash = db.Column('password', db.String(128))
    email = db.Column('email', db.String(50), unique=True, index=True)
    #registered_on = db.Column('registered_on', db.DateTime)
    #is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email
        #self.registered_on = datetime.utcnow()

    @property
    def password(self):
        """ Prevent password from being accessed"""
        raise AttributeError('Password is not a readable attribute.')

    @password.setter
    def password(self, password):
        """Set password to a hashed password"""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """Check if hashed password matches actual password."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True

    @property
    def is_active(self):
        """Always True, as all users are active."""
        return True

    @property
    def is_anonymous(self):
        """Always False, as anonymous users aren't supported."""
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<User: {}>'.format(self.username)


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