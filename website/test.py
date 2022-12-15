import datetime
import smtplib
import ssl
import time

import pandas as pd
from flask_apscheduler import APScheduler
from sqlalchemy import and_

from __init__ import db

from .models import Post, Search, User

result = db.query.join(Search).filter(Search.frequency=='daily')