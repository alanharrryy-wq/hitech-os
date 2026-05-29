(function(){
  'use strict';
  var PATCH='PRISMA_FROST_TACTICAL_V4_BACKGROUND_PANEL_SYSTEM';
  function ready(fn){ if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',fn,{once:true}); else fn(); }
  function safeGet(key){ try{return localStorage.getItem(key);}catch(_e){return null;} }
  function safeSet(key,value){ try{localStorage.setItem(key,value);}catch(_e){} }
  function applyText(){
    var select=document.getElementById('themeSelect');
    if(select){
      Array.prototype.forEach.call(select.options,function(opt){
        if(opt.value==='tactical') opt.textContent='Tactical Frost V4';
      });
    }
    var mat=document.getElementById('materialText');
    if(document.body.dataset.theme==='tactical' && mat){
      mat.textContent='fondo limpio sin selector lateral, doble glass premium, borde óptico hero, shadow executive y glow insight-violet controlado.';
    }
    var status=document.getElementById('v40StatusText');
    if(status && document.body.dataset.theme==='tactical'){
      status.textContent=status.textContent.replace(/tactical( frost)?/i,'tactical frost v3');
    }
    document.body.dataset.frostTacticalVersion='v4-background-panel-system';
  }

  function removeThemeRail(){
    Array.prototype.forEach.call(document.querySelectorAll('.v40QuickRail,[aria-label="PRISMA quick controls"]'),function(el){
      if(el && el.parentNode) el.parentNode.removeChild(el);
    });
  }
  function buildThemeCombo(){
    var select=document.getElementById('themeSelect');
    if(!select || select.dataset.frostCombo==='1') return;
    select.dataset.frostCombo='1';
    var wrap=select.parentElement;
    if(!wrap) return;
    wrap.classList.add('frostSelectWrap');
    var combo=document.createElement('div');
    combo.className='prisma-theme-combo';
    combo.setAttribute('data-open','0');
    var trigger=document.createElement('button');
    trigger.type='button';
    trigger.className='prisma-theme-trigger';
    trigger.setAttribute('aria-haspopup','listbox');
    trigger.setAttribute('aria-expanded','false');
    var list=document.createElement('div');
    list.className='prisma-theme-list';
    list.setAttribute('role','listbox');
    function labelFor(opt){ return opt ? opt.textContent : 'Elegir material'; }
    function render(){
      trigger.textContent=labelFor(select.options[select.selectedIndex]);
      list.innerHTML='';
      Array.prototype.forEach.call(select.options,function(opt){
        var b=document.createElement('button');
        b.type='button';
        b.className='prisma-theme-option';
        b.setAttribute('role','option');
        b.setAttribute('aria-selected', opt.value===select.value ? 'true' : 'false');
        b.dataset.value=opt.value;
        b.innerHTML='<span></span><small></small>';
        b.querySelector('span').textContent=opt.textContent;
        b.querySelector('small').textContent=opt.value==='tactical'?'actual':'tema';
        b.addEventListener('click',function(){
          select.value=opt.value;
          select.dispatchEvent(new Event('change',{bubbles:true}));
          combo.setAttribute('data-open','0');
          trigger.setAttribute('aria-expanded','false');
          setTimeout(function(){ applyText(); render(); },0);
        });
        list.appendChild(b);
      });
    }
    trigger.addEventListener('click',function(){
      var open=combo.getAttribute('data-open')==='1';
      combo.setAttribute('data-open',open?'0':'1');
      trigger.setAttribute('aria-expanded',open?'false':'true');
    });
    document.addEventListener('click',function(e){
      if(!combo.contains(e.target)){
        combo.setAttribute('data-open','0');
        trigger.setAttribute('aria-expanded','false');
      }
    });
    select.addEventListener('change',render);
    combo.appendChild(trigger);
    combo.appendChild(list);
    wrap.appendChild(combo);
    render();
  }

  function ensureInitialTheme(){
    var stored=safeGet('prisma-v28-theme');
    if(!stored){ safeSet('prisma-v28-theme','tactical'); }
    applyText();
  }
  ready(function(){
    document.body.dataset.frostTactical='ready';
    document.body.dataset.frostTacticalV4='background-panel-system';
    removeThemeRail();
    ensureInitialTheme();
    buildThemeCombo();
    var select=document.getElementById('themeSelect');
    if(select){ select.addEventListener('change',function(){ setTimeout(applyText,0); }); }
    var obs=new MutationObserver(function(muts){
      for(var i=0;i<muts.length;i++){
        if(muts[i].attributeName==='data-theme'){ applyText(); break; }
      }
    });
    obs.observe(document.body,{attributes:true,attributeFilter:['data-theme']});
    var railObs=new MutationObserver(function(){ removeThemeRail(); });
    railObs.observe(document.body,{childList:true,subtree:true});
    setTimeout(removeThemeRail,0); setTimeout(removeThemeRail,500); setTimeout(removeThemeRail,1600);
    window.PRISMA_FROST_TACTICAL={patch:PATCH, asset:'/assets/simon-spring-zmMrlEHsFQY-unsplash.jpg', applyText:applyText};
  });
})();
