from werkzeug.security import generate_password_hash, check_password_hash
from app import db
import datetime


class Users(db.Model):
    __tablename__ = "users"
    id = db.Column('user_id', db.Integer, primary_key=True)
    username = db.Column('username', db.String(50), unique=True, index=True)
    password_hash = db.Column('password', db.String(128))
    email = db.Column('email', db.String(50), unique=True, index=True)
    # registered_on = db.Column('registered_on', db.DateTime)
    # is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email
        # self.registered_on = datetime.utcnow()

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


class Players(db.Model):
    __tablename__ = "players"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(15), index=True, unique=False)
    last_name = db.Column(db.String(15), index=True, unique=False)
    discord_name = db.Column(db.String(15), index=True, unique=False)
    website_name = db.Column(db.String(15), index=True, unique=False)

    birthday = db.Column(db.Date, index=True, unique=False)
    age = db.Column(db.Integer, index=True, unique=False)
    rs_start_date = db.Column(db.Date, index=True, unique=False)
    years_playing_rs = db.Column(db.Integer, index=True, unique=False)
    gender = db.Column(db.String(15), index=True, unique=False)
    city = db.Column(db.String(15), index=True, unique=False)
    state = db.Column(db.String(15), index=True, unique=False)
    country = db.Column(db.String(15), index=True, unique=False)

    gp_donations = db.Column(db.Integer, index=True, unique=False)
    cash_donations = db.Column(db.Integer, index=True, unique=False)

    def __init__(self):
        self.first_name = None
        self.last_name = None
        self.discord_name = None
        self.website_name = None
        self.birthday = None
        self.age = None
        self.rs_start_date = None
        self.years_playing_rs = None
        self.gender = None
        self.city = None
        self.state = None
        self.country = None
        self.gp_donations = None
        self.cash_donations = None


class Accounts(db.Model):
    __tablename__ = "accounts"
    id = db.Column(db.Integer, primary_key=True)
    rsn = db.Column(db.String(15), index=True, unique=False)
    in_clan = db.Column(db.String(3), index=True, unique=False)
    version = db.Column(db.String(15), index=True, unique=False)
    rank = db.Column(db.String(15), index=True, unique=False)
    join_date = db.Column(db.Date, index=True, unique=False)

    # Analytics
    cap_points = db.Column(db.Integer, index=True, unique=False)
    recruit_points = db.Column(db.Integer, index=True, unique=False)
    event_points = db.Column(db.Integer, index=True, unique=False)
    xp_points = db.Column(db.Integer, index=True, unique=False)
    past_rsns = db.Column(db.String(15), index=True, unique=False)
    leave_date = db.Column(db.Date, index=True, unique=False)

    def __init__(self, rsn, in_clan, join_date, leave_date=None):
        self.rsn = rsn
        self.in_clan = in_clan
        self.version = "RS3"
        self.rank = "Recruit"
        self.join_date = join_date
        self.cap_points = 0
        self.recruit_points = 0
        self.event_points = 0
        self.xp_points = 0
        self.past_rsns = ""
        self.leave_date = leave_date


class Ranks(db.Model):
    __tablename__ = "ranks"
    id = db.Column(db.Integer, primary_key=True)
    rank = db.Column(db.String(15), index=True, unique=False)
    points_required = db.Column(db.Integer, index=True, unique=False)
    cap_recruits_required = db.Column(db.Integer, index=True, unique=False)
    description = db.Column(db.String(50), index=True, unique=False)

    def __init__(self, rank, points_required, cap_recruits_required, description):
        self.rank = rank
        self.points_required = points_required
        self.cap_recruits_required = cap_recruits_required
        self.description = description


class Caps(db.Model):
    __tablename__ = "caps"
    id = db.Column(db.Integer, primary_key=True)
    capdate = db.Column(db.Date, index=True, unique=False)
    week = db.Column(db.String(15), index=True, unique=False)
    rsn = db.Column(db.String(15), index=True, unique=False)
    captype = db.Column(db.Integer, index=True, unique=False)

    # Analytics
    possible_caps = db.Column(db.Integer, index=True, unique=False)
    cap_count = db.Column(db.Integer, index=True, unique=False)
    cap_percentage = db.Column(db.Integer, index=True, unique=False)
    cap_streak = db.Column(db.Integer, index=True, unique=False)
    last_cap = db.Column(db.Date, index=True, unique=False)

    def __init__(self, capdate, week, rsn, captype,
                 possible_caps, cap_count, cap_percentage, cap_streak, last_cap=None):
        self.capdate = capdate
        self.week = week
        self.rsn = rsn
        self.captype = captype
        self.possible_caps = possible_caps
        self.cap_count = cap_count
        self.cap_percentage = cap_percentage
        self.cap_streak = cap_streak
        self.last_cap = last_cap

    def serialize(self):
        return {
            'capdate': self.capdate,
            'week': self.week,
            'rsn': self.rsn,
            'captype': self.captype
        }


class Recruits(db.Model):
    __tablename__ = "recruits"
    id = db.Column(db.Integer, primary_key=True)
    recruit_date = db.Column(db.Date, index=True, unique=False)
    activity_type = db.Column(db.String(15), index=True, unique=False)
    recruiter = db.Column(db.String(15), index=True, unique=False)
    recruit = db.Column(db.String(15), index=True, unique=False)
    points = db.Column(db.Integer, index=True, unique=False)
    change_to_recruit_count = db.Column(db.Integer, index=True, unique=False)

    def __init__(self, recruit_date, activity_type, recruiter, recruit, points, change_to_recruit_count):
        self.recruit_date = recruit_date
        self.activity_type = activity_type
        self.recruiter = recruiter
        self.recruit = recruit
        self.points = points
        self.change_to_recruit_count = change_to_recruit_count


class Events(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)

    event_date = db.Column(db.Date, index=True, unique=False)
    host = db.Column(db.String(15), index=True, unique=False)
    activity_type = db.Column(db.String(15), index=True, unique=False)
    description = db.Column(db.String(15), index=True, unique=False)
    attendee_count = db.Column(db.Integer, index=True, unique=False)
    points = db.Column(db.Integer, index=True, unique=False)  # 0 or 1, if count>=5

    def __init__(self, event_date, host, activity_type, description, attendee_count, points):
        self.event_date = event_date
        self.host = host
        self.activity_type = activity_type
        self.description = description
        self.attendee_count = attendee_count
        self.points = points


class XP(db.Model):
    __tablename__ = "xp"
    id = db.Column(db.Integer, primary_key=True)
    rsn = db.Column(db.String(15), index=True, unique=False)
    xp = db.Column(db.Integer, index=True, unique=False)
    # something to capture timestamp of last pull

    def __init__(self, rsn, xp):
        self.rsn = rsn
        self.xp = xp
