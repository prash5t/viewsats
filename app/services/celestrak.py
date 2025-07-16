import requests
import json
from datetime import datetime
from flask import current_app
from app.utils import upsert_satellite


class CelesTrakError(Exception):
    """Base exception for CelesTrak service errors"""
    pass


def fetch_active_satellites():
    """
    Fetch active satellite data from CelesTrak API

    Returns:
        list: List of processed satellite records

    Raises:
        CelesTrakError: If there's an error fetching or processing the data
    """
    params = {
        'GROUP': 'active',
        'FORMAT': 'tle'  # Changed to 'tle' format since json-tle seems unreliable
    }

    try:
        response = requests.get(
            current_app.config['CELESTRAK_API_URL'],
            params=params,
            timeout=30
        )
        response.raise_for_status()

        # Parse TLE data from text response
        tle_text = response.text.strip().split('\n')
        satellites = []

        # Process TLE data in groups of 3 lines
        for i in range(0, len(tle_text), 3):
            if i + 2 >= len(tle_text):
                break

            name = tle_text[i].strip()
            line1 = tle_text[i + 1].strip()
            line2 = tle_text[i + 2].strip()

            # Extract NORAD ID from line 1 (columns 3-7)
            try:
                norad_id = int(line1[2:7])
            except (ValueError, IndexError):
                current_app.logger.warning(f"Invalid TLE line 1: {line1}")
                continue

            # Create satellite data dictionary
            sat_data = {
                'OBJECT_NAME': name,
                'NORAD_CAT_ID': str(norad_id),
                'OBJECT_ID': line1[9:17].strip(),
                'EPOCH': _parse_tle_epoch(line1[18:32].strip()),
                'MEAN_MOTION': float(line2[52:63]),
                'ECCENTRICITY': float('0.' + line2[26:33]),
                'INCLINATION': float(line2[8:16]),
                'TLE_LINE1': line1,
                'TLE_LINE2': line2
            }

            satellites.append(sat_data)

        if not satellites:
            raise CelesTrakError("No valid TLE data received from CelesTrak")

        processed_satellites = []
        for sat_data in satellites:
            try:
                satellite = upsert_satellite(sat_data)
                processed_satellites.append(satellite)
            except Exception as e:
                current_app.logger.error(
                    f"Error processing satellite {sat_data.get('NORAD_CAT_ID')}: {str(e)}")
                continue

        current_app.logger.info(
            f"Successfully processed {len(processed_satellites)} satellites")
        return processed_satellites

    except requests.RequestException as e:
        error_msg = f"Error fetching data from CelesTrak: {str(e)}"
        current_app.logger.error(error_msg)
        raise CelesTrakError(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error in CelesTrak service: {str(e)}"
        current_app.logger.error(error_msg)
        raise CelesTrakError(error_msg)


def _parse_tle_epoch(epoch_str):
    """Parse TLE epoch into ISO format datetime string"""
    try:
        year = int('20' + epoch_str[:2])  # Assuming years 2000-2099
        day = float(epoch_str[2:])

        # Convert day of year to datetime
        from datetime import datetime, timedelta
        date = datetime(year, 1, 1) + timedelta(days=day - 1)

        # Format with microseconds
        return date.strftime('%Y-%m-%dT%H:%M:%S.%f')
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid TLE epoch format: {epoch_str}") from e
