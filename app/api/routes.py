from datetime import datetime
from flask import jsonify, request, current_app
from app.api import bp
from app.utils import get_satellite, get_satellites
from app.services import manual_update, CelesTrakError
from app.services.position import calculate_positions


@bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })


@bp.route('/refresh', methods=['POST'])
def refresh():
    """Manually trigger data refresh"""
    try:
        satellites = manual_update()
        return jsonify({
            'status': 'completed',
            'count': len(satellites),
            'time': datetime.utcnow().isoformat() + 'Z'
        })
    except CelesTrakError as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'time': datetime.utcnow().isoformat() + 'Z'
        }), 500


@bp.route('/satellites')
def get_satellite_list():
    """Get list of satellites with optional filtering"""
    # Parse query parameters
    try:
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int, default=0)
        updated_since = request.args.get(
            'updated_since', type=datetime.fromisoformat)
    except ValueError:
        return jsonify({
            'error': 'Invalid query parameters'
        }), 400

    satellites = get_satellites(
        limit=limit, offset=offset, updated_since=updated_since)

    return jsonify({
        'count': len(satellites),
        'updated': datetime.utcnow().isoformat() + 'Z',
        'satellites': [sat.to_dict() for sat in satellites]
    })


@bp.route('/satellites/<int:norad_id>')
def get_satellite_details(norad_id):
    """Get details for a specific satellite"""
    satellite = get_satellite(norad_id)
    if not satellite:
        return jsonify({
            'error': 'Satellite not found'
        }), 404

    return jsonify(satellite.to_dict())


@bp.route('/satellites/positions')
def get_satellite_positions():
    """Get current positions for specified satellites"""
    try:
        norad_ids = [int(id) for id in request.args.get(
            'norad_ids', '').split(',') if id]
    except ValueError:
        return jsonify({
            'error': 'Invalid NORAD IDs'
        }), 400

    if not norad_ids:
        return jsonify({
            'error': 'No NORAD IDs provided'
        }), 400

    return jsonify(calculate_positions(norad_ids))
