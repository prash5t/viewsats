from app.extensions import db
from app.models import Satellite


def upsert_satellite(data):
    """
    Insert or update a satellite record

    Args:
        data (dict): Satellite data from CelesTrak

    Returns:
        Satellite: The created or updated satellite object
    """
    satellite_data = Satellite.from_celestrak_json(data)
    norad_id = satellite_data['norad_id']

    satellite = Satellite.query.get(norad_id)
    if satellite is None:
        satellite = Satellite(**satellite_data)
        db.session.add(satellite)
    else:
        for key, value in satellite_data.items():
            setattr(satellite, key, value)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

    return satellite


def get_satellite(norad_id):
    """
    Get a satellite by its NORAD ID

    Args:
        norad_id (int): NORAD catalog ID

    Returns:
        Satellite: The satellite object if found, None otherwise
    """
    return Satellite.query.get(norad_id)


def get_satellites(limit=None, offset=0, updated_since=None):
    """
    Get a list of satellites with optional filtering

    Args:
        limit (int, optional): Maximum number of records to return
        offset (int, optional): Number of records to skip
        updated_since (datetime, optional): Filter by last update time

    Returns:
        list: List of Satellite objects
    """
    query = Satellite.query

    if updated_since:
        query = query.filter(Satellite.last_updated >= updated_since)

    query = query.order_by(Satellite.norad_id)

    if limit:
        query = query.limit(limit)

    if offset:
        query = query.offset(offset)

    return query.all()
