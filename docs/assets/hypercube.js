/* A 4D tesseract, projected in 3D and rendered with WebGL.
   Native WebGL keeps this entrance independent from third-party CDNs. */
(() => {
  'use strict';
  const stage = document.getElementById('hypercube-stage');
  if (!stage) return;
  const entries = JSON.parse(document.getElementById('hypercube-entries').textContent);
  const title = document.getElementById('entry-title');
  const description = document.getElementById('entry-description');
  const tag = document.getElementById('entry-tag');
  const link = document.getElementById('entry-link');
  const card = document.getElementById('entry-card');
  const pause = document.getElementById('scene-pause');
  const reset = document.getElementById('scene-reset');
  const mode = document.getElementById('scene-mode');
  const help = document.getElementById('scene-help-text');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let selected = 0, hover = -1, paused = reduced.matches;
  let angle = .35, dragX = 0, dragY = 0, animationId = 0, lastTime = 0;
  let gl, program, buffer, canvas, available = false, projected = [];
  const vertices = Array.from({length: 16}, (_, i) => [0, 1, 2, 3].map(bit => (i & (1 << bit)) ? 1 : -1));
  const edges = [];
  for (let i = 0; i < 16; i++) for (let bit = 0; bit < 4; bit++) { const j = i ^ (1 << bit); if (i < j) edges.push([i, j]); }
  const activeEdges = [0, 2, 5, 7, 9, 11, 14, 17, 20, 23, 26, 30].slice(0, entries.length);
  const lang = () => document.documentElement.lang === 'en' ? 'en' : 'fr';
  const chooseText = (fr, en) => lang() === 'fr' ? fr : en;
  const rgb = hex => [1, 3, 5].map(i => parseInt(hex.slice(i, i + 2), 16) / 255);
  function showEntry(index) {
    selected = index;
    const entry = entries[index];
    title.textContent = entry.title[lang()];
    description.textContent = entry.description[lang()];
    tag.textContent = entry.tag[lang()];
    link.href = entry.href;
    link.textContent = entry.action?.[lang()] || chooseText('Explorer cette rubrique', 'Explore this section');
    card.style.setProperty('--entry-color', entry.color);
    document.querySelectorAll('[data-entry-index]').forEach(el => el.classList.toggle('is-selected', Number(el.dataset.entryIndex) === index));
    if (available) draw();
  }
  document.querySelectorAll('[data-entry-index]').forEach(el => {
    el.addEventListener('focus', () => { if (el.matches(':focus-visible')) showEntry(Number(el.dataset.entryIndex)); });
    // Keep link geometry stable while the pointer moves through the list.
    el.addEventListener('mouseenter', () => { hover = Number(el.dataset.entryIndex); if (available) draw(); });
    el.addEventListener('mouseleave', () => { hover = -1; if (available) draw(); });
  });
  function updateState() {
    pause.disabled = !available;
    reset.disabled = !available;
    pause.setAttribute('aria-pressed', String(paused));
    pause.textContent = paused ? chooseText('Reprendre l’animation', 'Resume animation') : chooseText('Mettre en pause', 'Pause animation');
    mode.textContent = available ? chooseText('WebGL · projection 4D', 'WebGL · 4D projection') : chooseText('Vue statique · mêmes rubriques', 'Static view · same sections');
    if (help) help.textContent = available ? chooseText('Survolez ou touchez une arête pour découvrir une rubrique. Faites glisser pour orienter le tesseract. La liste voisine donne accès aux mêmes contenus, à la souris comme au clavier.', 'Hover or tap an edge to discover a section. Drag to orient the tesseract. The adjacent list provides access to the same content using a mouse or keyboard.') : chooseText('Choisissez une rubrique dans la liste pour explorer le projet. Chaque entrée ouvre une page de lecture.', 'Choose a section from the list to explore the project. Each entry opens a reading page.');
  }
  document.addEventListener('hyperion:language', () => { showEntry(selected); updateState(); });
  document.addEventListener('hyperion:theme', () => { if (available) draw(); });
  pause.addEventListener('click', () => { paused = !paused; updateState(); start(); });
  reset.addEventListener('click', () => { angle = .35; dragX = dragY = 0; if (available) draw(); });
  reduced.addEventListener('change', event => { if (event.matches) { paused = true; updateState(); start(); } });
  function fallback() {
    available = false;
    cancelAnimationFrame(animationId);
    stage.classList.remove('is-webgl');
    if (canvas) canvas.hidden = true;
    updateState();
  }
  function shader(type, source) {
    const value = gl.createShader(type);
    gl.shaderSource(value, source); gl.compileShader(value);
    if (!gl.getShaderParameter(value, gl.COMPILE_STATUS)) throw new Error('WebGL shader compilation failed');
    return value;
  }
  function initialize() {
    const vertexShader = shader(gl.VERTEX_SHADER, 'attribute vec3 a_position; attribute vec4 a_color; uniform float u_size; varying vec4 v_color; void main(){gl_Position=vec4(a_position,1.0);gl_PointSize=u_size;v_color=a_color;}');
    const fragmentShader = shader(gl.FRAGMENT_SHADER, 'precision mediump float; varying vec4 v_color; uniform bool u_point; void main(){float a=v_color.a; if(u_point){float d=length(gl_PointCoord-vec2(0.5));a*=1.0-smoothstep(0.12,0.5,d);if(a<0.01)discard;} gl_FragColor=vec4(v_color.rgb,a);}');
    program = gl.createProgram(); gl.attachShader(program, vertexShader); gl.attachShader(program, fragmentShader); gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) throw new Error('WebGL shader link failed');
    gl.deleteShader(vertexShader); gl.deleteShader(fragmentShader);
    buffer = gl.createBuffer();
    gl.enable(gl.BLEND); gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
    available = true; canvas.hidden = false; stage.classList.add('is-webgl');
    updateState(); start();
  }
  function rotate(p, a, b, value) {
    const x = p[a], y = p[b];
    p[a] = x * Math.cos(value) - y * Math.sin(value);
    p[b] = x * Math.sin(value) + y * Math.cos(value);
  }
  function project() {
    const aspect = stage.clientWidth / stage.clientHeight;
    return vertices.map(vertex => {
      const p = vertex.slice();
      rotate(p, 0, 3, angle * .46); rotate(p, 1, 3, angle * .31); rotate(p, 2, 3, angle * .17);
      const w = 3 / (4 - p[3]);
      const q = p.slice(0, 3).map(n => n * w);
      rotate(q, 0, 2, .6 + dragX + angle * .09); rotate(q, 1, 2, -.35 + dragY);
      const perspective = 2.6 / (4.6 - q[2]);
      return [q[0] * perspective / aspect, q[1] * perspective, -q[2] / 10];
    });
  }
  function draw() {
    if (!available || !stage.clientWidth) return;
    const dpr = Math.min(devicePixelRatio || 1, 2);
    const width = Math.round(stage.clientWidth * dpr), height = Math.round(stage.clientHeight * dpr);
    if (canvas.width !== width || canvas.height !== height) { canvas.width = width; canvas.height = height; }
    gl.viewport(0, 0, width, height); gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT);
    projected = project();
    const light = document.documentElement.dataset.theme === 'light';
    const neutral = light ? [.17, .33, .46] : [.50, .64, .76];
    const lineData = [];
    edges.forEach(([a, b], index) => {
      const entryIndex = activeEdges.indexOf(index);
      const active = entryIndex >= 0;
      const emphasized = entryIndex === selected || entryIndex === hover;
      const color = active ? rgb(entries[entryIndex].color) : neutral;
      const alpha = emphasized ? 1 : active ? .66 : .25;
      for (const vertex of [a, b]) lineData.push(...projected[vertex], ...color, alpha);
    });
    gl.useProgram(program); gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    const position = gl.getAttribLocation(program, 'a_position'), color = gl.getAttribLocation(program, 'a_color');
    gl.enableVertexAttribArray(position); gl.enableVertexAttribArray(color);
    gl.vertexAttribPointer(position, 3, gl.FLOAT, false, 28, 0); gl.vertexAttribPointer(color, 4, gl.FLOAT, false, 28, 12);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(lineData), gl.DYNAMIC_DRAW);
    gl.uniform1i(gl.getUniformLocation(program, 'u_point'), 0); gl.uniform1f(gl.getUniformLocation(program, 'u_size'), 1);
    gl.drawArrays(gl.LINES, 0, edges.length * 2);
    const endpoints = edges[activeEdges[hover >= 0 ? hover : selected]] || [];
    const pointData = [];
    projected.forEach((point, index) => {
      const color = endpoints.includes(index) ? rgb(entries[hover >= 0 ? hover : selected].color) : light ? [.10, .39, .44] : [.72, .95, .96];
      pointData.push(...point, ...color, .95);
    });
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(pointData), gl.DYNAMIC_DRAW);
    gl.uniform1i(gl.getUniformLocation(program, 'u_point'), 1); gl.uniform1f(gl.getUniformLocation(program, 'u_size'), 11 * dpr);
    gl.drawArrays(gl.POINTS, 0, vertices.length);
  }
  function frame(time) {
    const delta = lastTime ? Math.min(time - lastTime, 50) : 0;
    lastTime = time;
    if (!paused && hover < 0) angle += delta * .00016;
    draw();
    if (!paused && !document.hidden && available) animationId = requestAnimationFrame(frame);
  }
  function start() {
    cancelAnimationFrame(animationId); lastTime = 0;
    if (available) { draw(); if (!paused && !document.hidden) animationId = requestAnimationFrame(frame); }
  }
  document.addEventListener('visibilitychange', start);
  const observer = typeof ResizeObserver !== 'undefined' ? new ResizeObserver(() => { if (available) draw(); }) : null;
  observer?.observe(stage);
  window.addEventListener('resize', () => { if (available) draw(); });
  function hitTest(event) {
    const bounds = canvas.getBoundingClientRect();
    const x = event.clientX - bounds.left, y = event.clientY - bounds.top;
    const pixels = projected.map(p => [(p[0] + 1) * bounds.width / 2, (1 - p[1]) * bounds.height / 2]);
    let nearest = -1, distance = event.pointerType === 'touch' ? 26 : 18;
    activeEdges.forEach((edgeIndex, entryIndex) => {
      const [a, b] = edges[edgeIndex].map(index => pixels[index]);
      if (!a || !b) return;
      const dx = b[0] - a[0], dy = b[1] - a[1];
      const t = Math.max(0, Math.min(1, ((x - a[0]) * dx + (y - a[1]) * dy) / (dx * dx + dy * dy || 1)));
      const d = Math.hypot(x - a[0] - t * dx, y - a[1] - t * dy);
      if (d < distance) { distance = d; nearest = entryIndex; }
    });
    return nearest;
  }
  try {
    canvas = document.createElement('canvas');
    canvas.setAttribute('aria-hidden', 'true');
    gl = canvas.getContext('webgl', {alpha: true, antialias: true, powerPreference: 'low-power'});
    if (!gl) { fallback(); return; }
    stage.appendChild(canvas);
    let pointer = null;
    canvas.addEventListener('pointerdown', event => { pointer = {x: event.clientX, y: event.clientY, moved: false}; });
    canvas.addEventListener('pointermove', event => {
      if (pointer && event.buttons) {
        const dx = event.clientX - pointer.x, dy = event.clientY - pointer.y;
        if (Math.abs(dx) + Math.abs(dy) > 4) pointer.moved = true;
        if (event.pointerType !== 'touch' || Math.abs(dx) > Math.abs(dy)) {
          dragX += dx * .006; dragY += dy * .006;
          pointer.x = event.clientX; pointer.y = event.clientY; draw();
        }
      } else {
        hover = hitTest(event);
        canvas.style.cursor = hover >= 0 ? 'pointer' : 'grab';
        if (hover >= 0) showEntry(hover);
        else if (available) draw();
      }
    });
    canvas.addEventListener('pointerup', event => { if (pointer && !pointer.moved) { const entry = hitTest(event); if (entry >= 0) showEntry(entry); } pointer = null; });
    canvas.addEventListener('pointercancel', () => { pointer = null; });
    canvas.addEventListener('pointerleave', () => { pointer = null; hover = -1; if (available) draw(); });
    canvas.addEventListener('webglcontextlost', event => { event.preventDefault(); fallback(); });
    canvas.addEventListener('webglcontextrestored', () => { try { initialize(); } catch { fallback(); } });
    initialize();
  } catch { fallback(); }
  showEntry(0);
})();
