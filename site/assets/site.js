(()=>{
  'use strict';
  const root=document.documentElement;
  const systemMotion=window.matchMedia('(prefers-reduced-motion: reduce)');
  const reduceMotion=()=>root.dataset.motion==='reduce'||systemMotion.matches;

  // Keep the same lightweight fade in standalone browsers and embedded previews.
  root.dataset.navigation='fade';
  let departureTimer;
  const resetNavigation=()=>{clearTimeout(departureTimer);root.classList.remove('is-leaving');};
  // A cached page must remain visible when the browser restores it with Back.
  window.addEventListener('pagehide',resetNavigation);

document.addEventListener('DOMContentLoaded',()=>{
  const motion=document.getElementById('motion-toggle');
  let manualReduced=false;
  try{manualReduced=localStorage.getItem('atlas-reduce-motion')==='1';}catch(e){}
  const setMotion=()=>{
    const reduced=manualReduced||systemMotion.matches;
    root.dataset.motion=reduced?'reduce':'default';
    motion?.setAttribute('aria-pressed',String(!reduced));
    if(motion){
      motion.disabled=systemMotion.matches;
      motion.textContent=reduced?'动态效果：已关闭':'动态效果：已开启';
      motion.setAttribute('aria-label',systemMotion.matches?'动态效果已关闭，遵循系统设置':
        reduced?'动态效果已关闭，点击开启':'动态效果已开启，点击关闭');
      motion.title=systemMotion.matches?'已遵循系统的减少动态效果设置':
        reduced?'点击开启背景流动和平滑滚动':'点击关闭背景流动和平滑滚动';
    }
  };
  setMotion();
  window.addEventListener('pageshow',()=>{
    resetNavigation();
    try{manualReduced=localStorage.getItem('atlas-reduce-motion')==='1';}catch(e){}
    setMotion();
  });
  systemMotion.addEventListener('change',setMotion);
  motion?.addEventListener('click',()=>{
    manualReduced=!manualReduced;setMotion();
    try{localStorage.setItem('atlas-reduce-motion',manualReduced?'1':'0');}catch(e){}
  });

  // Smooth anchors and short page fades without capturing full-page snapshots.
  document.addEventListener('click',event=>{
    if(event.defaultPrevented||event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;
    const link=event.target instanceof Element?event.target.closest('a[href]'):null;
    if(!link||link.hasAttribute('download')||(link.target&&link.target!=='_self'))return;
    const url=new URL(link.href,location.href);
    if(url.origin!==location.origin||!/^https?:$/.test(url.protocol))return;
    if(url.pathname===location.pathname&&url.search===location.search&&url.hash){
      let id;try{id=decodeURIComponent(url.hash.slice(1));}catch(e){return;}
      const target=document.getElementById(id);if(!target)return;
      event.preventDefault();
      if(location.hash!==url.hash)history.pushState(null,'',url.hash);
      if(!target.matches('a[href],button,input,select,textarea,[tabindex]')){
        target.setAttribute('tabindex','-1');
        target.addEventListener('blur',()=>target.removeAttribute('tabindex'),{once:true});
      }
      target.focus({preventScroll:true});
      target.scrollIntoView({behavior:reduceMotion()?'instant':'smooth',block:'start'});
      return;
    }
    if(reduceMotion()||!(url.pathname.endsWith('/')||url.pathname.endsWith('.html')))return;
    event.preventDefault();
    clearTimeout(departureTimer);root.classList.add('is-leaving');
    departureTimer=setTimeout(()=>location.assign(url.href),140);
  });

  const toggle=document.querySelector('.filter-more');
  if(toggle) toggle.addEventListener('click',()=>{
    const expanded=toggle.getAttribute('aria-expanded')==='true';
    toggle.setAttribute('aria-expanded',String(!expanded));
    document.getElementById('advanced-filters').hidden=expanded;
    toggle.querySelector('span').textContent=expanded?'＋':'−';
  });
});
})();
