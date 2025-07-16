from flask import current_app
from app.extensions import scheduler
from app.services.celestrak import fetch_active_satellites, CelesTrakError


def init_scheduler():
    """Initialize the scheduler jobs"""
    if not scheduler.running:
        scheduler.start()

    # Remove any existing jobs
    scheduler.remove_all_jobs()

    # Add the CelesTrak update job
    scheduler.add_job(
        id='update_satellites',
        func=update_satellites,
        trigger='interval',
        seconds=current_app.config['CELESTRAK_UPDATE_INTERVAL'],
        replace_existing=True
    )

    current_app.logger.info("Scheduler initialized with satellite update job")


def update_satellites():
    """Job function to update satellite data"""
    with scheduler.app.app_context():
        try:
            satellites = fetch_active_satellites()
            current_app.logger.info(
                f"Scheduled update completed. Processed {len(satellites)} satellites")
        except CelesTrakError as e:
            current_app.logger.error(f"Scheduled update failed: {str(e)}")
        except Exception as e:
            current_app.logger.error(
                f"Unexpected error in scheduled update: {str(e)}")


def manual_update():
    """Manually trigger a satellite data update"""
    with scheduler.app.app_context():
        return fetch_active_satellites()
