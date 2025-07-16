from datetime import datetime
from skyfield.api import load, EarthSatellite
from skyfield.timelib import Time
from app.utils import get_satellite
from flask import current_app


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
            # Get TLE data
            tle_data = satellite.tle_data
            if not tle_data or 'TLE_LINE1' not in tle_data or 'TLE_LINE2' not in tle_data:
                current_app.logger.warning(
                    f"Missing TLE data for satellite {norad_id}")
                continue

            # Create Skyfield satellite object from TLE data
            satrec = EarthSatellite(
                tle_data['TLE_LINE1'],
                tle_data['TLE_LINE2'],
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
            current_app.logger.error(
                f"Error calculating position for satellite {norad_id}: {str(e)}")
            continue

    return {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'positions': positions
    }
