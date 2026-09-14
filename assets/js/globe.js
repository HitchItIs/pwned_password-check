import * as THREE from 'https://unpkg.com/three@0.164.1/build/three.module.js';
import { OrbitControls } from 'https://unpkg.com/three@0.164.1/examples/jsm/controls/OrbitControls.js';

export class GlobeEngine {
  constructor(canvas, onPick) {
    this.canvas = canvas;
    this.onPick = onPick;
    this.earthRadius = 100;
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(50, 1, 0.1, 2000);
    this.camera.position.set(0, 155, 230);
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.minDistance = 130;
    this.controls.maxDistance = 520;
    this.controls.autoRotate = false;

    this.points = null;
    this.raycaster = new THREE.Raycaster();
    this.pointer = new THREE.Vector2();
    this.selectedRing = new THREE.Mesh(
      new THREE.RingGeometry(2.4, 3.1, 48),
      new THREE.MeshBasicMaterial({ color: 0x00f3ff, transparent: true, opacity: 0.9, side: THREE.DoubleSide })
    );
    this.selectedRing.visible = false;

    this.trajectoryLine = new THREE.Line(
      new THREE.BufferGeometry(),
      new THREE.LineBasicMaterial({ color: 0x00f3ff, transparent: true, opacity: 0.75 })
    );
    this.trajectoryLine.visible = false;

    this._initScene();
    this._bind();
    this.resize();
  }

  _initScene() {
    const earth = new THREE.Mesh(
      new THREE.SphereGeometry(this.earthRadius, 64, 64),
      new THREE.MeshPhongMaterial({ color: 0x0d2448, emissive: 0x02101f, shininess: 20, specular: 0x286ca4 })
    );
    const atmosphere = new THREE.Mesh(
      new THREE.SphereGeometry(this.earthRadius * 1.03, 64, 64),
      new THREE.MeshBasicMaterial({ color: 0x00a6ff, transparent: true, opacity: 0.09, side: THREE.BackSide })
    );

    const ambient = new THREE.AmbientLight(0x7db7ff, 0.7);
    const sun = new THREE.DirectionalLight(0xffffff, 1.1);
    sun.position.set(180, 100, 90);

    this.scene.add(earth, atmosphere, ambient, sun, this.selectedRing, this.trajectoryLine);
  }

  _bind() {
    window.addEventListener('resize', () => this.resize());
    this.canvas.addEventListener('pointerdown', (event) => this._onPointerDown(event));
  }

  _onPointerDown(event) {
    if (!this.points) return;
    const rect = this.canvas.getBoundingClientRect();
    this.pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    this.pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    this.raycaster.params.Points.threshold = 2.5;
    this.raycaster.setFromCamera(this.pointer, this.camera);
    const hits = this.raycaster.intersectObject(this.points);
    if (hits.length && typeof this.onPick === 'function') {
      this.onPick(hits[0].index);
    }
  }

  setSatellites(count) {
    if (this.points) this.scene.remove(this.points);
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(new Float32Array(count * 3), 3));
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(new Float32Array(count * 3), 3));
    const material = new THREE.PointsMaterial({ size: 1.45, vertexColors: true, sizeAttenuation: true, transparent: true, opacity: 0.92 });
    this.points = new THREE.Points(geometry, material);
    this.scene.add(this.points);
  }

  updateSatellites(items, selectedIndex = -1) {
    if (!this.points) this.setSatellites(items.length);
    const pos = this.points.geometry.attributes.position.array;
    const col = this.points.geometry.attributes.color.array;

    items.forEach((item, i) => {
      const p = i * 3;
      pos[p] = item.position.x;
      pos[p + 1] = item.position.y;
      pos[p + 2] = item.position.z;

      const color = item.group === 'starlink' ? [0, 1, 0.4] : item.group === 'debris' ? [1, 0.67, 0] : [0, 0.95, 1];
      col[p] = color[0]; col[p + 1] = color[1]; col[p + 2] = color[2];
    });

    this.points.geometry.attributes.position.needsUpdate = true;
    this.points.geometry.attributes.color.needsUpdate = true;

    if (selectedIndex >= 0 && items[selectedIndex]) {
      const t = items[selectedIndex].position;
      this.selectedRing.visible = true;
      this.selectedRing.position.set(t.x, t.y, t.z);
      this.selectedRing.lookAt(this.camera.position);
    } else {
      this.selectedRing.visible = false;
    }
  }

  setTrajectory(points) {
    if (!points?.length) {
      this.trajectoryLine.visible = false;
      return;
    }
    const vertices = points.flatMap((p) => [p.x, p.y, p.z]);
    this.trajectoryLine.geometry.dispose();
    this.trajectoryLine.geometry = new THREE.BufferGeometry();
    this.trajectoryLine.geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
    this.trajectoryLine.visible = true;
  }

  focusOn(vector3) {
    this.controls.target.lerp(vector3, 0.25);
  }

  resize() {
    const { clientWidth, clientHeight } = this.canvas;
    if (!clientWidth || !clientHeight) return;
    this.camera.aspect = clientWidth / clientHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(clientWidth, clientHeight, false);
  }

  render() {
    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  }
}
