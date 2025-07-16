import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CelesTrak API configuration
    CELESTRAK_API_URL = 'https://celestrak.org/NORAD/elements/gp.php'
    CELESTRAK_UPDATE_INTERVAL = 300  # 5 minutes instead of 1 minute

    # Scheduler configuration
    SCHEDULER_API_ENABLED = True
