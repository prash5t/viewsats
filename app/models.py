from datetime import datetime
import json
from app.extensions import db


class Satellite(db.Model):
    __tablename__ = 'satellites'

    norad_id = db.Column(db.Integer, primary_key=True)
    object_name = db.Column(db.String(128), index=True)
    object_id = db.Column(db.String(64), index=True)
    epoch = db.Column(db.DateTime)
    inclination = db.Column(db.Float)
    eccentricity = db.Column(db.Float)
    mean_motion = db.Column(db.Float)
    bstar = db.Column(db.Float)
    raw_json = db.Column(db.Text)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Satellite {self.object_name}>'

    def to_dict(self):
        return {
            'norad_id': self.norad_id,
            'name': self.object_name,
            'object_id': self.object_id,
            'launch_epoch': self.epoch.isoformat() + 'Z' if self.epoch else None,
            'inclination': self.inclination,
            'eccentricity': self.eccentricity,
            'mean_motion': self.mean_motion,
            'bstar': self.bstar,
            'last_updated': self.last_updated.isoformat() + 'Z' if self.last_updated else None
        }

    @property
    def tle_data(self):
        """Get the TLE data from raw_json"""
        if not self.raw_json:
            return None
        try:
            data = json.loads(self.raw_json)
            return data
        except (json.JSONDecodeError, TypeError):
            return None

    @staticmethod
    def from_celestrak_json(data):
        """Create or update a Satellite instance from CelesTrak JSON data"""
        epoch = datetime.strptime(
            data['EPOCH'], '%Y-%m-%dT%H:%M:%S.%f') if 'EPOCH' in data else None

        return {
            'norad_id': int(data.get('NORAD_CAT_ID')),
            'object_name': data.get('OBJECT_NAME'),
            'object_id': data.get('OBJECT_ID'),
            'epoch': epoch,
            'inclination': float(data.get('INCLINATION', 0)),
            'eccentricity': float(data.get('ECCENTRICITY', 0)),
            'mean_motion': float(data.get('MEAN_MOTION', 0)),
            'bstar': float(data.get('BSTAR', 0)),
            'raw_json': json.dumps(data),
            'last_updated': datetime.utcnow()
        }
