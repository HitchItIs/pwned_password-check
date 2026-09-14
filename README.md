# NORAD Space Surveillance & Satellite Tracking Terminal

Professional, non-game, dark-theme satellite telemetry terminal built with:

- **Backend:** Native **PHP 8.x** API proxy + caching
- **Frontend:** **HTML5 / CSS3 / Vanilla JS**
- **3D/Orbital:** **Three.js** + **satellite.js**
- **Live data:** **CelesTrak TLE** + **Open Notify ISS crew**

## Features

- NORAD-style HUD layout with glassmorphism panels and CRT overlay
- Real-time 3D Earth scene with satellite tracks and target highlighting
- Group filters: stations, starlink, debris
- Search by satellite name or NORAD ID
- Telemetry inspector (lat/lon/altitude/velocity/period/inclination + raw TLE)
- Backend cache layer with remote-failure fallback

## Project Structure

- `/index.php`
- `/api/tle.php`
- `/api/iss_crew.php`
- `/assets/css/hud-theme.css`
- `/assets/js/app.js`
- `/assets/js/globe.js`
- `/assets/js/telemetry.js`
- `/assets/js/ui.js`
- `/cache/` (auto-created and used for cached JSON payloads)

## Run Locally

### 1) Requirements

- PHP 8.x with cURL enabled
- Internet access for CDN and telemetry sources

### 2) Start the built-in PHP server

From repository root:

```bash
php -S 127.0.0.1:8000
```

### 3) Open in browser

Visit:

```text
http://127.0.0.1:8000/index.php
```

## Private Hosting (Subdirectory Safe)

This app now uses relative asset paths and module-based API URL resolution, so it can be hosted:

- at domain root (example: `https://intranet.example.com/`)
- or in a private subdirectory (example: `https://intranet.example.com/norad-terminal/`)

### Deployment checklist

- Keep the project directory structure unchanged.
- Serve `index.php` through PHP 8.x.
- Ensure outbound server access to:
  - `https://celestrak.org`
  - `http://api.open-notify.org`
- Ensure `cache/` is writable by the web server user.

## API Endpoints

- `GET /api/tle.php?group=stations`
- `GET /api/tle.php?group=starlink`
- `GET /api/tle.php?group=debris`
- `GET /api/iss_crew.php`

`api/tle.php` caches each group response for 6 hours in `cache/tle_{group}.json` and falls back to stale cache on remote failure.

## Notes

- Ensure the `cache/` directory is writable by PHP.
- If external APIs are unavailable and no cache exists yet, API endpoints return `502`.
