from app import db
import datetime


class User(db.Model):
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


class Caps(db.Model):
    __tablename__ = "ca[s"
    id = db.Column(db.Integer, primary_key=True)
    capdate = db.Column(db.DateTime)
    rsn = db.Column(db.String(14), index=True, unique=True)
    captype = db.Column(db.Integer, index=True, unique=False)

    def __init__(self, capdate, rsn, captype):
        self.rsn = rsn
        self.captype = captype
        self.capdate = capdate