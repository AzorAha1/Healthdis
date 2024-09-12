from datetime import timedelta

class Config:
    SECRET_KEY = 'dc21a9cb05847ffd9d5a37b67857042b'
    SQLALCHEMY_DATABASE_URI = 'mysql://faiz:12345@localhost/healthdis'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)