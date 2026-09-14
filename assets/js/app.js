import { GlobeEngine } from '/assets/js/globe.js';
import { TelemetryEngine } from '/assets/js/telemetry.js';
import { UIController } from '/assets/js/ui.js';

const waitForSatelliteJs = async () => {
  const started = performance.now();
  while (!window.satellite) {
    if (performance.now() - started > 10000) throw new Error('satellite.js not available');
    await new Promise((resolve) => setTimeout(resolve, 50));
  }
};

const fetchGroup = async (group) => {
  const response = await fetch(`/api/tle.php?group=${encodeURIComponent(group)}`, { cache: 'no-store' });
  if (!response.ok) throw new Error(`${group} request failed`);
  return {
    rows: await response.json(),
    cacheSource: response.headers.get('X-Cache-Source') || 'unknown'
  };
};

const fetchCrew = async () => {
  try {
    const response = await fetch('/api/iss_crew.php', { cache: 'no-store' });
    if (!response.ok) return null;
    return response.json();
  } catch (_) {
    return null;
  }
};

const app = async () => {
  await waitForSatelliteJs();
  const ui = new UIController();
  ui.initClock();
  ui.bindCrtToggle();

  const canvas = document.getElementById('globeCanvas');
  const telemetry = new TelemetryEngine(100);
  const globe = new GlobeEngine(canvas, (visibleIndex) => {
    const selected = telemetry.selectVisible(visibleIndex);
    if (!selected) return;
    ui.setTelemetry(selected);
    globe.focusOn(selected.position);
    globe.setTrajectory(telemetry.buildTrajectory(selected));
  });

  const [stations, starlink, debris, crew] = await Promise.all([
    fetchGroup('stations'),
    fetchGroup('starlink'),
    fetchGroup('debris'),
    fetchCrew()
  ]);

  telemetry.ingest({
    stations: stations.rows,
    starlink: starlink.rows,
    debris: debris.rows
  });

  ui.setCacheStatus(`stations:${stations.cacheSource} | starlink:${starlink.cacheSource} | debris:${debris.cacheSource}`);
  if (crew?.people) {
    const aboardIss = crew.people.filter((p) => p.craft === 'ISS').length;
    ui.setAlertText(`ISS crew onboard: ${aboardIss}`);
  }

  ui.bindFilters((filter, query) => {
    telemetry.applyFilters(filter, query);
    ui.setTrackedCount(telemetry.getVisibleItems().length);
  });

  ui.bindPredictor((lat, lon) => {
    if (!Number.isFinite(lat) || !Number.isFinite(lon)) {
      ui.setPassPrediction('Invalid coordinates. Enter numeric latitude/longitude.');
      return;
    }
    const item = telemetry.getSelected();
    if (!item) {
      ui.setPassPrediction('No target selected.');
      return;
    }

    const distance = Math.hypot(item.latitude - lat, item.longitude - lon);
    const minutes = Math.max(1, Math.round(distance * 0.75));
    ui.setPassPrediction(`Estimated ${item.name} pass visibility in ~${minutes} minutes.`);
  });

  telemetry.applyFilters('all', '');
  ui.setTrackedCount(telemetry.getVisibleItems().length);

  const animate = () => {
    requestAnimationFrame(animate);
    telemetry.update(new Date());
    const visible = telemetry.getVisibleItems();
    globe.updateSatellites(visible, visible.findIndex((x) => x === telemetry.getSelected()));

    const selected = telemetry.getSelected();
    if (selected) {
      ui.setTelemetry(selected);
      globe.setTrajectory(telemetry.buildTrajectory(selected));
    }

    globe.render();
  };

  animate();
  if (window.lucide) window.lucide.createIcons();
};

app().catch((error) => {
  console.error(error);
  const status = document.getElementById('systemStatus');
  if (status) status.textContent = 'SYSTEM: DEGRADED';
});
