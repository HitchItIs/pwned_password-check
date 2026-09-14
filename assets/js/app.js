import { GlobeEngine } from './globe.js';
import { TelemetryEngine } from './telemetry.js';
import { UIController } from './ui.js';

const API_BASE = new URL('../../api/', import.meta.url);
const apiUrl = (file, params = {}) => {
  const url = new URL(file, API_BASE);
  Object.entries(params).forEach(([key, value]) => url.searchParams.set(key, value));
  return url.toString();
};

const waitForSatelliteJs = async () => {
  const started = performance.now();
  while (!window.satellite) {
    if (performance.now() - started > 10000) throw new Error('satellite.js not available');
    await new Promise((resolve) => setTimeout(resolve, 50));
  }
};

const fetchGroup = async (group) => {
  const response = await fetch(apiUrl('tle.php', { group }), { cache: 'no-store' });
  if (!response.ok) throw new Error(`${group} request failed`);
  return {
    rows: await response.json(),
    cacheSource: response.headers.get('X-Cache-Source') || 'unknown'
  };
};

const fetchCrew = async () => {
  try {
    const response = await fetch(apiUrl('iss_crew.php'), { cache: 'no-store' });
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
  ui.bindRotateToggle(() => globe.toggleAutoRotate());

  const [stations, starlink, debris, crew] = await Promise.allSettled([
    fetchGroup('stations'),
    fetchGroup('starlink'),
    fetchGroup('debris'),
    fetchCrew()
  ]);

  telemetry.ingest({
    stations: stations.status === 'fulfilled' ? stations.value.rows : [],
    starlink: starlink.status === 'fulfilled' ? starlink.value.rows : [],
    debris: debris.status === 'fulfilled' ? debris.value.rows : []
  });

  ui.setCacheStatus(
    `stations:${stations.status === 'fulfilled' ? stations.value.cacheSource : 'error'} | `
    + `starlink:${starlink.status === 'fulfilled' ? starlink.value.cacheSource : 'error'} | `
    + `debris:${debris.status === 'fulfilled' ? debris.value.cacheSource : 'error'}`
  );

  if (crew.status === 'fulfilled' && crew.value?.people) {
    const aboardIss = crew.value.people.filter((p) => p.craft === 'ISS').length;
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
  if (telemetry.getVisibleItems().length === 0) {
    const status = document.getElementById('systemStatus');
    if (status) status.textContent = 'SYSTEM: DEGRADED';
    ui.setAlertText('No live telemetry sources reachable');
  }

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
