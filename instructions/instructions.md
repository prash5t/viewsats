## 📘 Product Specification Requirements (PSR) — ViewSats (Flask + HTML/CSS)

### **Overview & Objectives**

Build a fully working **open-source satellite visualization web app** using:

- **Flask** as the backend API and server
- **HTML/CSS (with JavaScript)** for the frontend
- Real-time or near-real-time data from **CelesTrak**, updated **every 1 minute**
- Display satellite orbits around Earth, satellite details, and ownership metadata
- No user authentication, no Docker, no sockets

---

### 🚀 Data Sources & Formats

#### 1. CelesTrak GP API (TLE & Metadata)

- **Endpoint**: `https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=json`
- Fields include:

  - `OBJECT_NAME`, `NORAD_CAT_ID`, `OBJECT_ID`, `EPOCH`, `INCLINATION`, `ECCENTRICITY`, `MEAN_MOTION`, `BSTAR`, etc.

---

### 📂 Architecture Overview

```
[ Scheduler (APScheduler) ] --(1min)---> [ Flask API Server ] ---> [ SQLite DB ]
                                                        |
                                                        | REST Endpoints
                                                        V
                                               [ HTML/CSS/JS Frontend ]
```

---

### 🔁 Data Flow

1. APScheduler fetches TLE and metadata from CelesTrak every 1 minute
2. The fetched data is parsed and stored (upsert) in a SQLite DB
3. Flask API provides REST endpoints for:

   - Satellite list and metadata
   - Satellite position calculation
   - Manual refresh trigger

4. HTML/JS frontend uses `fetch` API to retrieve satellite data and visualize on a canvas or SVG map

---

### 🌐 REST API Endpoints

#### 1. Health Check

```
GET /health
```

Response:

```json
{ "status": "ok", "timestamp": "2025-07-16T12:00:00Z" }
```

#### 2. Trigger Data Refresh

```
POST /refresh
```

Response:

```json
{ "status": "started", "time": "2025-07-16T12:00:00Z" }
```

#### 3. Get Satellite List

```
GET /satellites
```

Query params:

- `limit`, `offset`, `updated_since`

Response:

```json
{
  "count": 10973,
  "updated": "2025-07-16T12:00:00Z",
  "satellites": [
    {
      "norad_id": 25544,
      "name": "ISS (ZARYA)",
      "object_id": "1998-067A",
      "launch_epoch": "2024-05-06T19:53:04Z",
      "inclination": 51.6393,
      "eccentricity": 0.000358,
      "mean_motion": 15.50957674,
      "bstar": 0.0002731,
      "last_updated": "2025-07-16T12:00:00Z"
    }
  ]
}
```

#### 4. Get Single Satellite

```
GET /satellites/<norad_id>
```

Returns metadata + orbital params

#### 5. Get Satellite Positions

```
GET /satellites/positions?norad_ids=25544,12345
```

Response:

```json
{
  "timestamp": "2025-07-16T12:15:00Z",
  "positions": [
    { "norad_id": 25544, "lat": 21.34, "lon": 88.23, "alt_km": 408.2 },
    { "norad_id": 12345, "lat": -11.12, "lon": 34.23, "alt_km": 760.1 }
  ]
}
```

---

### 🔺 Frontend UI (HTML/CSS/JavaScript)

- Use **vanilla JS** to call API endpoints
- **Main dashboard** (`/`) shows:

  - Earth-centered canvas/SVG
  - Satellites orbiting in real-time or near-real-time (projected positions)
  - A refresh button to trigger `POST /refresh`

- **Satellite detail page** (`/satellite/<norad_id>`) shows:

  - Object name, launch date, orbital elements
  - Current position (above which country, if feasible)
  - Nearby satellites via `GET /satellites/<norad_id>/nearby`

---

### 🗄️ SQLite Schema

```sql
CREATE TABLE satellites (
  norad_id INTEGER PRIMARY KEY,
  object_name TEXT,
  object_id TEXT,
  epoch TEXT,
  inclination REAL,
  eccentricity REAL,
  mean_motion REAL,
  bstar REAL,
  raw_json TEXT,
  last_updated TEXT
);
```

---

### 🔒 Error Handling

- Gracefully handle missing data
- Return 404 for unknown satellites
- Use UTC ISO timestamps

---

### 🧪 Tools

- Flask
- APScheduler (1-minute data fetcher)
- SQLite
- Requests + JSON parser
- Skyfield or SGP4 to calculate positions
- HTML + CSS + JS (no frontend framework)

---

### ✅ Summary

This updated PSR defines the full-stack ViewSats system:

- **Flask backend**: Fetches, stores, computes, and serves satellite data
- **HTML/CSS frontend**: Presents interactive dashboard for satellite viewing
- Fetch data from **CelesTrak every minute**
- No auth, Docker, or external frontend stack required

Next: You can start by generating Flask boilerplate and HTML/CSS templates for this project.
