export class UIController {
  constructor() {
    this.els = {
      utcClock: document.getElementById('utcClock'),
      localClock: document.getElementById('localClock'),
      toggleCrt: document.getElementById('toggleCrt'),
      crtOverlay: document.getElementById('crtOverlay'),
      groupFilters: document.getElementById('groupFilters'),
      searchInput: document.getElementById('searchInput'),
      trackedCount: document.getElementById('trackedCount'),
      cacheStatus: document.getElementById('cacheStatus'),
      alertTicker: document.getElementById('alertTicker'),
      observerLat: document.getElementById('observerLat'),
      observerLon: document.getElementById('observerLon'),
      predictPassBtn: document.getElementById('predictPassBtn'),
      passPrediction: document.getElementById('passPrediction'),
      tmName: document.getElementById('tmName'), tmNorad: document.getElementById('tmNorad'),
      tmLat: document.getElementById('tmLat'), tmLon: document.getElementById('tmLon'), tmAlt: document.getElementById('tmAlt'),
      tmVel: document.getElementById('tmVel'), tmPeriod: document.getElementById('tmPeriod'), tmInc: document.getElementById('tmInc'),
      tmTle1: document.getElementById('tmTle1'), tmTle2: document.getElementById('tmTle2')
    };
    this.filter = 'all';
    this.query = '';
  }

  initClock() {
    const tick = () => {
      const now = new Date();
      this.els.utcClock.textContent = now.toISOString().substring(11, 19);
      this.els.localClock.textContent = now.toLocaleTimeString([], { hour12: false });
    };
    tick();
    setInterval(tick, 1000);
  }

  bindFilters(onChange) {
    this.els.groupFilters.addEventListener('click', (event) => {
      const btn = event.target.closest('button[data-filter]');
      if (!btn) return;
      this.filter = btn.dataset.filter;
      this.els.groupFilters.querySelectorAll('button').forEach((b) => b.classList.toggle('active', b === btn));
      onChange(this.filter, this.query);
    });

    this.els.searchInput.addEventListener('input', () => {
      this.query = this.els.searchInput.value;
      onChange(this.filter, this.query);
    });
  }

  bindCrtToggle() {
    this.els.toggleCrt.addEventListener('click', () => this.els.crtOverlay.classList.toggle('disabled'));
  }

  bindPredictor(onPredict) {
    this.els.predictPassBtn.addEventListener('click', () => {
      const lat = Number(this.els.observerLat.value);
      const lon = Number(this.els.observerLon.value);
      onPredict(lat, lon);
    });
  }

  setTelemetry(item) {
    if (!item) return;
    this.els.tmName.textContent = item.name;
    this.els.tmNorad.textContent = item.norad_id;
    this.els.tmLat.textContent = `${item.latitude.toFixed(4)}°`;
    this.els.tmLon.textContent = `${item.longitude.toFixed(4)}°`;
    this.els.tmAlt.textContent = `${item.altitudeKm.toFixed(2)} km`;
    this.els.tmVel.textContent = `${item.velocityKmh.toFixed(2)} km/h`;
    this.els.tmPeriod.textContent = `${item.orbitalPeriodMin.toFixed(2)} min`;
    this.els.tmInc.textContent = `${item.inclinationDeg.toFixed(2)}°`;
    this.els.tmTle1.value = item.tle1;
    this.els.tmTle2.value = item.tle2;
  }

  setTrackedCount(count) {
    this.els.trackedCount.textContent = `Tracked Objects: ${count}`;
  }

  setCacheStatus(status) {
    this.els.cacheStatus.textContent = `TLE Cache: ${status}`;
  }

  setAlertText(text) {
    this.els.alertTicker.textContent = `Conjunction Watch: ${text}`;
  }

  setPassPrediction(message) {
    this.els.passPrediction.textContent = message;
  }
}
