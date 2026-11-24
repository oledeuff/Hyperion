(() => {
  const root=document.documentElement;
  const button=document.getElementById('atelier-theme');
  let theme='light';
  try { if(localStorage.getItem('hyperion-theme-v2')==='dark')theme='dark'; } catch {}
  function update(){
    root.dataset.theme=theme;
    button.textContent=theme==='light'?'Thème clair':'Thème sombre';
    button.setAttribute('aria-pressed',String(theme==='light'));
  }
  button.addEventListener('click',()=>{
    theme=theme==='light'?'dark':'light';update();
    try { localStorage.setItem('hyperion-theme-v2',theme); } catch {}
  });
  update();
  const pause=document.getElementById('atelier-pause');
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');
  function setPaused(value){
    root.dataset.motion=value?'paused':'running';
    pause.textContent=value?'Reprendre l’animation':'Mettre en pause';
    pause.setAttribute('aria-pressed',String(value));
  }
  pause.addEventListener('click',()=>setPaused(root.dataset.motion!=='paused'));
  reduced.addEventListener('change',event=>{if(event.matches)setPaused(true);});
  setPaused(reduced.matches);
})();
