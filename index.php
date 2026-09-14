<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>NORAD Space Surveillance & Satellite Tracking Terminal</title>
    <link rel="stylesheet" href="/assets/css/hud-theme.css">
    <script defer src="https://unpkg.com/lucide@latest"></script>
    <script async src="https://unpkg.com/satellite.js@5.0.0/dist/satellite.min.js"></script>
</head>
<body>
    <div class="crt-overlay" id="crtOverlay"></div>
    <div class="app-grid">
        <header class="top-bar panel">
            <div class="title-wrap">
                <h1>NORAD Space Surveillance & Satellite Tracking Terminal</h1>
                <span class="status-pill" id="systemStatus">SYSTEM: ONLINE</span>
            </div>
            <div class="clock-wrap">
                <div><span>UTC</span><strong id="utcClock">--:--:--</strong></div>
                <div><span>LOCAL</span><strong id="localClock">--:--:--</strong></div>
                <button class="hud-btn" id="toggleRotate">Auto Rotate</button>
                <button class="hud-btn" id="toggleCrt">CRT Overlay</button>
            </div>
        </header>

        <aside class="left-sidebar panel">
            <h2><i data-lucide="filter"></i> Tracking Filters</h2>
            <div class="btn-group" id="groupFilters">
                <button class="hud-btn active" data-filter="all">All</button>
                <button class="hud-btn" data-filter="stations">ISS & Stations</button>
                <button class="hud-btn" data-filter="starlink">Starlink</button>
                <button class="hud-btn" data-filter="debris">Space Debris</button>
            </div>

            <label for="searchInput">Search (Name / NORAD ID)</label>
            <input id="searchInput" class="hud-input" type="search" placeholder="ISS, STARLINK, 25544...">

            <h3><i data-lucide="satellite"></i> Pass Predictor</h3>
            <div class="predictor-grid">
                <input id="observerLat" class="hud-input" type="number" step="0.0001" placeholder="Latitude">
                <input id="observerLon" class="hud-input" type="number" step="0.0001" placeholder="Longitude">
            </div>
            <button class="hud-btn" id="predictPassBtn">Estimate Next Pass Window</button>
            <p class="small-text" id="passPrediction">Awaiting coordinates...</p>
        </aside>

        <main class="globe-panel panel">
            <canvas id="globeCanvas" aria-label="NORAD satellite globe"></canvas>
        </main>

        <aside class="right-sidebar panel telemetry">
            <h2><i data-lucide="radar"></i> Telemetry Inspector</h2>
            <dl>
                <div><dt>Name</dt><dd id="tmName">-</dd></div>
                <div><dt>NORAD ID</dt><dd id="tmNorad">-</dd></div>
                <div><dt>Latitude</dt><dd id="tmLat">-</dd></div>
                <div><dt>Longitude</dt><dd id="tmLon">-</dd></div>
                <div><dt>Altitude</dt><dd id="tmAlt">-</dd></div>
                <div><dt>Velocity</dt><dd id="tmVel">-</dd></div>
                <div><dt>Orbital Period</dt><dd id="tmPeriod">-</dd></div>
                <div><dt>Inclination</dt><dd id="tmInc">-</dd></div>
            </dl>
            <label>Line 1</label>
            <textarea id="tmTle1" readonly></textarea>
            <label>Line 2</label>
            <textarea id="tmTle2" readonly></textarea>
        </aside>

        <footer class="bottom-bar panel">
            <span id="cacheStatus">TLE Cache: initializing...</span>
            <span id="trackedCount">Tracked Objects: 0</span>
            <span id="alertTicker">Conjunction Watch: nominal</span>
        </footer>
    </div>

    <script type="module" src="/assets/js/app.js"></script>
</body>
</html>
