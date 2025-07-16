from flask import render_template
from app.main import bp
from app.utils import get_satellite


@bp.route('/')
def index():
    """Render the main dashboard"""
    return render_template('index.html')


@bp.route('/satellite/<int:norad_id>')
def satellite_detail(norad_id):
    """Render the satellite detail page"""
    satellite = get_satellite(norad_id)
    if not satellite:
        return render_template('404.html'), 404
    return render_template('satellite.html', satellite=satellite)
