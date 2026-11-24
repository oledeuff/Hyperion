import {vertices4D,edges,primaryNodes,projectVertices,hitNode,edgeTriangles} from './hypercube-geometry.js';

(() => {
  'use strict';
  const stage=document.getElementById('hypercube-stage');
  if(!stage)return;
  const entries=JSON.parse(document.getElementById('hypercube-entries').textContent);
  const title=document.getElementById('entry-title'),description=document.getElementById('entry-description');
  const tag=document.getElementById('entry-tag'),link=document.getElementById('entry-link'),card=document.getElementById('entry-card');
  const pause=document.getElementById('scene-pause'),reset=document.getElementById('scene-reset');
  const mode=document.getElementById('scene-mode'),help=document.getElementById('scene-help-text'),fallbackSvg=stage.querySelector('svg');
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');
  let selected=0,hover=-1,paused=reduced.matches,phase=0,yaw=0,pitch=0,animationId=0,lastTime=0;
  let gl,program,buffer,canvas,available=false,projected=[];
  const lang=()=>document.documentElement.lang==='en'?'en':'fr';
  const text=(fr,en)=>lang()==='fr'?fr:en;
  const rgb=hex=>[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16)/255);
  function showEntry(index){
    selected=index;
    const entry=entries[index];
    title.textContent=entry.title[lang()];description.textContent=entry.description[lang()];
    tag.textContent=entry.tag[lang()];link.href=entry.href;
    link.textContent=text('Explorer cette rubrique','Explore this section');
    card.style.setProperty('--entry-color',entry.color);
    document.querySelectorAll('[data-entry-index]').forEach(el=>el.classList.toggle('is-selected',Number(el.dataset.entryIndex)===index));
    if(available)draw();
  }
  document.querySelectorAll('[data-entry-index]').forEach(el=>{
    el.addEventListener('focus',()=>{if(el.matches(':focus-visible'))showEntry(Number(el.dataset.entryIndex));});
    el.addEventListener('mouseenter',()=>{
      hover=Number(el.dataset.entryIndex);
      if(!el.closest('.entry-list'))showEntry(hover);
      if(available)draw();
    });
    el.addEventListener('mouseleave',()=>{hover=-1;if(available)draw();});
  });
  function updateState(){
    pause.hidden=reset.hidden=!available;pause.disabled=reset.disabled=!available;
    pause.setAttribute('aria-pressed',String(paused));
    pause.textContent=paused?text('Reprendre l’animation','Resume animation'):text('Mettre en pause','Pause animation');
    mode.textContent=available?'Tesseract · WebGL':text('Tesseract · accès directs','Tesseract · direct links');
    help.textContent=available
      ?text('Survolez un point coloré pour découvrir une rubrique, puis cliquez pour l’ouvrir. Faites glisser le cube pour changer de point de vue. Les liens sous le cube et la liste voisine donnent les mêmes accès.','Hover a coloured point to discover a section, then click to open it. Drag the cube to change the view. Links below the cube and in the adjacent list provide the same access.')
      :text('Cliquez sur un point coloré ou choisissez un lien sous le cube pour ouvrir une rubrique.','Click a coloured point or choose a link below the cube to open a section.');
  }
  document.addEventListener('hyperion:language',()=>{showEntry(selected);updateState();});
  document.addEventListener('hyperion:theme',()=>{if(available)draw();});
  pause.addEventListener('click',()=>{paused=!paused;updateState();start();});
  reset.addEventListener('click',()=>{phase=yaw=pitch=0;if(available)draw();});
  reduced.addEventListener('change',event=>{if(event.matches){paused=true;updateState();start();}});
  function fallback(){
    available=false;cancelAnimationFrame(animationId);stage.classList.remove('is-webgl');
    fallbackSvg.removeAttribute('aria-hidden');if(canvas)canvas.hidden=true;updateState();
  }
  function shader(type,source){
    const value=gl.createShader(type);gl.shaderSource(value,source);gl.compileShader(value);
    if(!gl.getShaderParameter(value,gl.COMPILE_STATUS))throw new Error('WebGL shader compilation failed');
    return value;
  }
  function initialize(){
    const vs=shader(gl.VERTEX_SHADER,'attribute vec3 a_position;attribute vec4 a_color;uniform float u_size;varying vec4 v_color;void main(){gl_Position=vec4(a_position,1.0);gl_PointSize=u_size;v_color=a_color;}');
    const fs=shader(gl.FRAGMENT_SHADER,'precision mediump float;varying vec4 v_color;uniform bool u_point;void main(){float a=v_color.a;if(u_point){float d=length(gl_PointCoord-vec2(0.5));a*=1.0-smoothstep(0.25,0.5,d);if(a<0.01)discard;}gl_FragColor=vec4(v_color.rgb,a);}');
    program=gl.createProgram();gl.attachShader(program,vs);gl.attachShader(program,fs);gl.linkProgram(program);
    if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error('WebGL shader link failed');
    gl.deleteShader(vs);gl.deleteShader(fs);buffer=gl.createBuffer();
    gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);
    available=true;canvas.hidden=false;stage.classList.add('is-webgl');fallbackSvg.setAttribute('aria-hidden','true');
    updateState();start();
  }
  function draw(){
    if(!available||!stage.clientWidth)return;
    const dpr=Math.min(devicePixelRatio||1,2),width=stage.clientWidth,height=stage.clientHeight;
    if(canvas.width!==Math.round(width*dpr)||canvas.height!==Math.round(height*dpr)){canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);}
    gl.viewport(0,0,canvas.width,canvas.height);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);
    projected=projectVertices({phase,yaw,pitch,aspect:width/height});
    const light=document.documentElement.dataset.theme==='light';
    const outer=rgb(light?'#165d87':'#76cfe5'),inner=rgb(light?'#00818e':'#4ed4c7'),spoke=rgb(light?'#6493a8':'#7fadc3');
    const lineData=[];
    for(const [a,b] of edges){
      const isSpoke=(a<8)!==(b<8),color=isSpoke?spoke:a<8?outer:inner;
      const thickness=isSpoke?1.9:a<8?3.0:2.7,alpha=isSpoke?.72:.95;
      for(const p of edgeTriangles(projected[a],projected[b],width,height,thickness))lineData.push(...p,...color,alpha);
    }
    gl.useProgram(program);gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
    const position=gl.getAttribLocation(program,'a_position'),color=gl.getAttribLocation(program,'a_color');
    gl.enableVertexAttribArray(position);gl.enableVertexAttribArray(color);
    gl.vertexAttribPointer(position,3,gl.FLOAT,false,28,0);gl.vertexAttribPointer(color,4,gl.FLOAT,false,28,12);
    gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(lineData),gl.DYNAMIC_DRAW);
    gl.uniform1i(gl.getUniformLocation(program,'u_point'),0);gl.drawArrays(gl.TRIANGLES,0,lineData.length/7);
    const points=[];
    projected.forEach((p,index)=>{
      const node=primaryNodes.find(n=>n.vertex===index),c=node?rgb(light?'#086b7d':'#a1ede8'):inner;
      points.push(...p,...c,node?1:.65);
    });
    gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(points),gl.DYNAMIC_DRAW);
    gl.uniform1i(gl.getUniformLocation(program,'u_point'),1);gl.uniform1f(gl.getUniformLocation(program,'u_size'),8*dpr);
    gl.drawArrays(gl.POINTS,0,vertices4D.length);
    const highlighted=[];
    for(const node of primaryNodes){
      const active=node.entry===(hover>=0?hover:selected);
      highlighted.push(...projected[node.vertex],...rgb(active?(light?'#b95537':'#f7ac87'):(light?'#08788b':'#79ded9')),1);
    }
    gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(highlighted),gl.DYNAMIC_DRAW);
    gl.uniform1f(gl.getUniformLocation(program,'u_size'),16*dpr);gl.drawArrays(gl.POINTS,0,primaryNodes.length);
  }
  function frame(time){
    const delta=lastTime?Math.min(time-lastTime,50):0;lastTime=time;
    if(!paused&&hover<0)phase+=delta*.0003;
    draw();if(!paused&&!document.hidden&&available)animationId=requestAnimationFrame(frame);
  }
  function start(){cancelAnimationFrame(animationId);lastTime=0;if(available){draw();if(!paused&&!document.hidden)animationId=requestAnimationFrame(frame);}}
  document.addEventListener('visibilitychange',start);
  if(typeof ResizeObserver!=='undefined')new ResizeObserver(()=>{if(available)draw();}).observe(stage);
  window.addEventListener('resize',()=>{if(available)draw();});
  function target(event){
    const box=canvas.getBoundingClientRect();
    return hitNode(projected,event.clientX-box.left,event.clientY-box.top,box.width,box.height,event.pointerType==='touch'?34:26);
  }
  try{
    canvas=document.createElement('canvas');canvas.setAttribute('aria-hidden','true');
    gl=canvas.getContext('webgl',{alpha:true,antialias:true,powerPreference:'low-power'});
    if(!gl){fallback();return;}
    stage.appendChild(canvas);let pointer=null;
    canvas.addEventListener('pointerdown',event=>{pointer={x:event.clientX,y:event.clientY,ox:event.clientX,oy:event.clientY,moved:false};canvas.setPointerCapture(event.pointerId);});
    canvas.addEventListener('pointermove',event=>{
      if(pointer&&event.buttons){
        const dx=event.clientX-pointer.x,dy=event.clientY-pointer.y;
        if(Math.hypot(event.clientX-pointer.ox,event.clientY-pointer.oy)>7)pointer.moved=true;
        if(event.pointerType!=='touch'||Math.abs(dx)>Math.abs(dy)){yaw+=dx*.006;pitch=Math.max(-.55,Math.min(.55,pitch+dy*.006));pointer.x=event.clientX;pointer.y=event.clientY;hover=-1;draw();}
      }else{hover=target(event);canvas.style.cursor=hover>=0?'pointer':'grab';if(hover>=0)showEntry(hover);else draw();}
    });
    canvas.addEventListener('pointerup',event=>{
      const clicked=pointer&&!pointer.moved;pointer=null;
      if(canvas.hasPointerCapture(event.pointerId))canvas.releasePointerCapture(event.pointerId);
      if(clicked){const entry=target(event);if(entry>=0)location.assign(entries[entry].href);}
    });
    canvas.addEventListener('pointercancel',()=>{pointer=null;});
    canvas.addEventListener('pointerleave',()=>{if(!pointer){hover=-1;draw();}});
    canvas.addEventListener('webglcontextlost',event=>{event.preventDefault();fallback();});
    canvas.addEventListener('webglcontextrestored',()=>{try{initialize();}catch{fallback();}});
    initialize();
  }catch{fallback();}
  showEntry(0);
})();
