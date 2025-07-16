from datetime import datetime
from skyfield.api import load, EarthSatellite
from skyfield.timelib import Time
from app.utils import get_satellite


def calculate_positions(norad_ids):
    """
    Calculate current positions for given satellites

    Args:
        norad_ids (list): List of NORAD catalog IDs

    Returns:
        dict: Dictionary with timestamp and satellite positions
    """
    # Load the timescale
    ts = load.timescale()
    now = ts.now()

    positions = []
    for norad_id in norad_ids:
        satellite = get_satellite(norad_id)
        if not satellite:
            continue

        try:
            # Create Skyfield satellite object from TLE data
            satrec = EarthSatellite(
                satellite.raw_json['TLE_LINE1'],
                satellite.raw_json['TLE_LINE2'],
                satellite.object_name,
                ts
            )

            # Calculate geocentric position
            geocentric = satrec.at(now)
            subpoint = geocentric.subpoint()

            positions.append({
                'norad_id': norad_id,
                'lat': subpoint.latitude.degrees,
                'lon': subpoint.longitude.degrees,
                'alt_km': subpoint.elevation.km
            })

        except Exception as e:
            # Log error and skip this satellite
            continue

    return {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'positions': positions
    }
