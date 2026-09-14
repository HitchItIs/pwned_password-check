const EARTH_RADIUS_KM = 6371;

export class TelemetryEngine {
  constructor(earthRadius = 100) {
    this.earthRadius = earthRadius;
    this.items = [];
    this.filteredIndexes = [];
    this.selectedIndex = -1;
  }

  ingest(rawByGroup) {
    const sat = window.satellite;
    this.items = [];

    Object.entries(rawByGroup).forEach(([group, rows]) => {
      rows.forEach((row) => {
        try {
          const satrec = sat.twoline2satrec(row.tle1, row.tle2);
          this.items.push({
            ...row,
            group,
            satrec,
            position: { x: 0, y: 0, z: 0 },
            latitude: 0,
            longitude: 0,
            altitudeKm: 0,
            velocityKmh: 0,
            orbitalPeriodMin: satrec.no > 0 ? ((2 * Math.PI) / satrec.no) : 0,
            inclinationDeg: satrec.inclo * (180 / Math.PI)
          });
        } catch (_) {
          // skip malformed rows
        }
      });
    });

    this.filteredIndexes = this.items.map((_, i) => i);
    if (this.items.length && this.selectedIndex < 0) this.selectedIndex = 0;
  }

  update(now = new Date()) {
    const sat = window.satellite;
    const gmst = sat.gstime(now);

    this.items.forEach((item) => {
      const pv = sat.propagate(item.satrec, now);
      if (!pv.position || !pv.velocity) return;

      const geo = sat.eciToGeodetic(pv.position, gmst);
      item.latitude = sat.degreesLat(geo.latitude);
      item.longitude = sat.degreesLong(geo.longitude);
      item.altitudeKm = geo.height;
      item.velocityKmh = Math.sqrt(pv.velocity.x ** 2 + pv.velocity.y ** 2 + pv.velocity.z ** 2) * 3600;
      item.position = this._toCartesian(item.latitude, item.longitude, item.altitudeKm);
    });
  }

  _toCartesian(latDeg, lonDeg, altKm) {
    const lat = latDeg * (Math.PI / 180);
    const lon = lonDeg * (Math.PI / 180);
    const scale = this.earthRadius / EARTH_RADIUS_KM;
    const r = (EARTH_RADIUS_KM + altKm) * scale;

    return {
      x: r * Math.cos(lat) * Math.cos(lon),
      y: r * Math.sin(lat),
      z: -r * Math.cos(lat) * Math.sin(lon)
    };
  }

  applyFilters(filter, query) {
    const q = (query || '').trim().toLowerCase();
    this.filteredIndexes = this.items
      .map((item, idx) => ({ item, idx }))
      .filter(({ item }) => (filter === 'all' ? true : item.group === filter))
      .filter(({ item }) => (!q ? true : item.name.toLowerCase().includes(q) || String(item.norad_id).includes(q)))
      .map(({ idx }) => idx);

    if (!this.filteredIndexes.includes(this.selectedIndex)) {
      this.selectedIndex = this.filteredIndexes.length ? this.filteredIndexes[0] : -1;
    }
  }

  getVisibleItems() {
    return this.filteredIndexes.map((i) => this.items[i]);
  }

  selectVisible(visibleIndex) {
    this.selectedIndex = this.filteredIndexes[visibleIndex] ?? -1;
    return this.getSelected();
  }

  getSelected() {
    return this.items[this.selectedIndex] ?? null;
  }

  buildTrajectory(item, now = new Date()) {
    if (!item?.satrec) return [];
    const sat = window.satellite;
    const points = [];

    for (let m = -45; m <= 45; m += 2) {
      const dt = new Date(now.getTime() + m * 60000);
      const pv = sat.propagate(item.satrec, dt);
      if (!pv.position) continue;
      const geo = sat.eciToGeodetic(pv.position, sat.gstime(dt));
      points.push(this._toCartesian(sat.degreesLat(geo.latitude), sat.degreesLong(geo.longitude), geo.height));
    }

    return points;
  }
}
