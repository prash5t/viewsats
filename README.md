# ViewSats

A real-time satellite tracking visualization web application built with Flask and D3.js.

## Features

- Real-time satellite tracking with 3D Earth visualization
- Data from CelesTrak API, updated every 5 minutes
- Interactive satellite search and filtering
- Detailed satellite information pages
- RESTful API endpoints

## Local Development

1. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python run.py
```

Visit http://localhost:5000 to view the application.

## Deployment

### Deploy to Render (Recommended)

1. Fork this repository to your GitHub account

2. Visit [render.com](https://render.com) and create a new Web Service

3. Connect your GitHub repository

4. Configure the service:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn run:app`
   - Environment Variables:
     - `FLASK_APP`: run.py
     - `FLASK_ENV`: production

### Alternative Deployment Options

- **Fly.io**: Follow the [Python deployment guide](https://fly.io/docs/languages-and-frameworks/python/)
- **Railway.app**: Connect your GitHub repository and deploy
- **PythonAnywhere**: Upload files and set up a WSGI configuration

## API Documentation

### Endpoints

- `GET /api/health`: Health check
- `GET /api/satellites`: List all satellites
- `GET /api/satellites/<norad_id>`: Get single satellite
- `GET /api/satellites/positions`: Get current positions
- `POST /api/refresh`: Trigger data refresh

## License

MIT License
