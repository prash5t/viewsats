import requests
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
        'FORMAT': 'json'
    }

    try:
        response = requests.get(
            current_app.config['CELESTRAK_API_URL'],
            params=params,
            timeout=30  # 30 seconds timeout
        )
        response.raise_for_status()

        satellites = response.json()
        if not isinstance(satellites, list):
            raise CelesTrakError("Invalid response format from CelesTrak API")

        processed_satellites = []
        for sat_data in satellites:
            try:
                satellite = upsert_satellite(sat_data)
                processed_satellites.append(satellite)
            except Exception as e:
                current_app.logger.error(
                    f"Error processing satellite data: {str(e)}")
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
