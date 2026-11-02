// Background of the contents page and lesson viewer: the earth turns in place while the stars of
// the universe orbit it, out past the edge of the screen (the endlessness of agentic AI).
// If three.js or WebGL is missing the page keeps its plain CSS sky (html.space-3d is never set).
(() => {
  if (!window.THREE) return;

  const canvas = document.createElement("canvas");
  canvas.id = "spaceBg";
  canvas.setAttribute("aria-hidden", "true");

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  } catch {
    return;
  }
  document.body.prepend(canvas);
  document.documentElement.classList.add("space-3d");

  const small = window.innerWidth < 760;
  const still = matchMedia("(prefers-reduced-motion: reduce)").matches;
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
  renderer.setClearColor(0x000000, 0);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(38, 1, .1, 1000);
  camera.position.set(0, 3.2, 15);
  camera.lookAt(0, 0, 0);

  const loader = new THREE.TextureLoader();
  const tex = name => loader.load(`assets/earth/${name}`);

  const earthGroup = new THREE.Group();
  earthGroup.rotation.z = .41;  // the real 23.5 degree axial tilt
  scene.add(earthGroup);

  const earth = new THREE.Mesh(
    new THREE.SphereGeometry(2, 64, 64),
    new THREE.MeshPhongMaterial({
      map: tex("earth_atmos_2048.jpg"),
      normalMap: tex("earth_normal_2048.jpg"),
      specularMap: tex("earth_specular_2048.jpg"),
      specular: new THREE.Color(0x1a2a3c),
      shininess: 18
    })
  );
  earthGroup.add(earth);

  const nightLights = new THREE.Mesh(
    new THREE.SphereGeometry(2.002, 64, 64),
    new THREE.MeshBasicMaterial({ map: tex("earth_lights_2048.png"), blending: THREE.AdditiveBlending, transparent: true, opacity: .55 })
  );
  earth.add(nightLights);

  const clouds = new THREE.Mesh(
    new THREE.SphereGeometry(2.025, 64, 64),
    new THREE.MeshLambertMaterial({ map: tex("earth_clouds_1024.png"), transparent: true, opacity: .7, depthWrite: false })
  );
  earthGroup.add(clouds);

  const atmosphere = new THREE.Mesh(
    new THREE.SphereGeometry(2.32, 48, 48),
    new THREE.ShaderMaterial({
      vertexShader: "varying vec3 vN; void main(){ vN = normalize(normalMatrix * normal); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }",
      // Fades to nothing at the outer edge so the glow has no hard ring.
      fragmentShader: "varying vec3 vN; void main(){ float i = smoothstep(0.0, 0.5, -vN.z) * 0.42; gl_FragColor = vec4(0.45,0.82,1.0,1.0) * i; }",
      blending: THREE.AdditiveBlending,
      side: THREE.BackSide,
      transparent: true,
      depthWrite: false
    })
  );
  scene.add(atmosphere);

  scene.add(new THREE.AmbientLight(0x6677aa, .42));
  const sun = new THREE.DirectionalLight(0xffffff, 1);
  sun.position.set(-6, 2.5, 5);
  scene.add(sun);

  // Orbiting stars. Each star keeps its own ring, and the vertex shader moves it along that ring, so
  // thousands of stars cost one draw call. Near stars circle fast and far ones slowly, as real orbits do.
  const count = small ? 3500 : 9000;
  const orbit = new Float32Array(count * 4);  // radius, start angle, ring tilt, speed
  const look = new Float32Array(count * 2);   // size, warmth
  for (let i = 0; i < count; i++) {
    // Most stars near the earth, thinning out to well beyond the frame.
    const radius = 3.1 + Math.pow(Math.random(), 2.4) * 150;
    orbit.set([radius, Math.random() * Math.PI * 2, (Math.random() - .5) * .9, 1.15 / Math.sqrt(radius)], i * 4);
    look.set([1 + Math.pow(Math.random(), 3) * 3, Math.random()], i * 2);
  }
  const starGeometry = new THREE.BufferGeometry();
  starGeometry.setAttribute("position", new THREE.BufferAttribute(new Float32Array(count * 3), 3));
  starGeometry.setAttribute("orbit", new THREE.BufferAttribute(orbit, 4));
  starGeometry.setAttribute("look", new THREE.BufferAttribute(look, 2));
  const starMaterial = new THREE.ShaderMaterial({
    uniforms: { time: { value: 0 }, pixel: { value: renderer.getPixelRatio() } },
    vertexShader: `
      attribute vec4 orbit;
      attribute vec2 look;
      uniform float time;
      uniform float pixel;
      varying vec3 vColor;
      void main() {
        float a = orbit.y + time * orbit.w;
        vec3 p = vec3(cos(a), 0.0, sin(a)) * orbit.x;
        p = vec3(p.x, p.z * sin(orbit.z), p.z * cos(orbit.z));
        vec4 view = modelViewMatrix * vec4(p, 1.0);
        gl_Position = projectionMatrix * view;
        gl_PointSize = pixel * look.x * clamp(26.0 / -view.z, 1.1, 5.0);
        vColor = mix(vec3(0.72, 0.88, 1.0), vec3(1.0, 0.9, 0.76), look.y);
      }`,
    fragmentShader: `
      varying vec3 vColor;
      void main() {
        float d = length(gl_PointCoord - 0.5) * 2.0;
        gl_FragColor = vec4(vColor, pow(max(0.0, 1.0 - d), 1.6));
      }`,
    blending: THREE.AdditiveBlending,
    transparent: true,
    depthWrite: false
  });
  const stars = new THREE.Points(starGeometry, starMaterial);
  stars.frustumCulled = false;
  stars.rotation.z = -.18;
  scene.add(stars);

  function layout() {
    const w = window.innerWidth, h = window.innerHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
  window.addEventListener("resize", layout);
  layout();

  // A fullscreen lesson shows only the viewer element, so the canvas moves in with it.
  document.addEventListener("fullscreenchange", () => {
    (document.fullscreenElement || document.body).prepend(canvas);
  });

  let last = performance.now();
  function frame(now) {
    const dt = Math.min(.05, (now - last) / 1000);
    last = now;
    earth.rotation.y += dt * .1;
    clouds.rotation.y += dt * .115;
    starMaterial.uniforms.time.value += dt;
    renderer.render(scene, camera);
    requestAnimationFrame(frame);
  }
  if (still) {
    // Reduced motion: one frame now and one once the textures have had time to arrive.
    renderer.render(scene, camera);
    setTimeout(() => renderer.render(scene, camera), 1500);
  } else {
    requestAnimationFrame(frame);
  }
})();
