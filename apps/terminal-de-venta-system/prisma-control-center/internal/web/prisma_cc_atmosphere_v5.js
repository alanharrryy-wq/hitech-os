/* PRISMA Control Center V5 Atmosphere Runtime
   PixiJS = background atmosphere. GSAP = drift choreography. Motion adapter = UI microinteractions.
   The canvas is fixed behind the UI and pointer-events:none. */
(function(){
  'use strict';
  if (window.__PRISMA_CC_ATMOSPHERE_V5__) return;
  window.__PRISMA_CC_ATMOSPHERE_V5__ = true;

  var SELECTOR_UI = '.panel,.card,.glass,.opButton,.dockBtn,.node,.timelineCard,.picker button,button,a[href],textarea,input,select';
  var reducedQuery = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : { matches:false };
  var reduced = !!reducedQuery.matches;
  var state = { app:null, particles:[], blobs:[], started:false };

  function log(){
    if (window.PRISMA_DEBUG_ATMOSPHERE) console.log.apply(console, ['[PRISMA V5]'].concat([].slice.call(arguments)));
  }

  function ready(fn){
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn, { once:true });
    else fn();
  }

  function ensureCanvas(){
    var existing = document.getElementById('prisma-atmosphere-v5');
    if (existing) return existing;
    var canvas = document.createElement('canvas');
    canvas.id = 'prisma-atmosphere-v5';
    canvas.setAttribute('aria-hidden', 'true');
    canvas.dataset.prismaLayer = 'pixi-background-atmosphere';
    document.body.insertBefore(canvas, document.body.firstChild);
    return canvas;
  }

  function fallback(reason){
    log('fallback', reason || 'unknown');
    if (document.querySelector('.prisma-atmosphere-fallback')) return;
    var div = document.createElement('div');
    div.className = 'prisma-atmosphere-fallback';
    div.setAttribute('aria-hidden', 'true');
    div.dataset.reason = String(reason || 'fallback');
    document.body.insertBefore(div, document.body.firstChild);
  }

  function getViewport(){
    return { w: Math.max(window.innerWidth || 0, 1), h: Math.max(window.innerHeight || 0, 1) };
  }

  function getTickerDelta(tick){
    if (!tick) return 1;
    if (typeof tick === 'number') return tick;
    if (typeof tick.deltaTime === 'number') return tick.deltaTime;
    if (typeof tick.deltaMS === 'number') return tick.deltaMS / 16.6667;
    return 1;
  }

  function tryBlur(displayObject, strength){
    try{
      var PIXI = window.PIXI;
      var Blur = PIXI.BlurFilter || (PIXI.filters && PIXI.filters.BlurFilter);
      if (!Blur) return;
      var filter;
      try { filter = new Blur(strength, 2); }
      catch(_){ filter = new Blur({ strength: strength }); }
      displayObject.filters = [filter];
    } catch(_err) {}
  }

  function makeCircle(color, radius, alpha){
    var PIXI = window.PIXI;
    var g = new PIXI.Graphics();
    try{
      if (typeof g.beginFill === 'function'){
        g.beginFill(color, alpha);
        g.drawCircle(0, 0, radius);
        g.endFill();
      } else if (typeof g.circle === 'function' && typeof g.fill === 'function'){
        g.circle(0, 0, radius);
        g.fill({ color: color, alpha: alpha });
      } else {
        throw new Error('Graphics circle API unavailable');
      }
      return g;
    } catch(_err){
      var s = new PIXI.Sprite(PIXI.Texture.WHITE);
      s.tint = color;
      s.alpha = alpha;
      s.width = radius * 2;
      s.height = radius * 2;
      if (s.anchor && s.anchor.set) s.anchor.set(.5);
      return s;
    }
  }

  function placeRandom(obj, vp, radius){
    obj.x = Math.random() * vp.w;
    obj.y = Math.random() * vp.h;
    obj.__baseX = obj.x;
    obj.__baseY = obj.y;
    obj.__speed = .12 + Math.random() * .42;
    obj.__phase = Math.random() * Math.PI * 2;
    obj.__ampX = 8 + Math.random() * 34;
    obj.__ampY = 4 + Math.random() * 22;
    obj.__radius = radius || 10;
  }

  async function createPixi(canvas){
    var PIXI = window.PIXI;
    if (!PIXI || !PIXI.Application) throw new Error('PIXI.Application unavailable');
    var opts = {
      canvas: canvas,
      view: canvas,
      resizeTo: window,
      backgroundAlpha: 0,
      antialias: true,
      autoDensity: true,
      resolution: Math.min(window.devicePixelRatio || 1, 2),
      powerPreference: 'low-power'
    };
    var app;
    try{
      app = new PIXI.Application();
      if (typeof app.init === 'function') await app.init(opts);
      else app = new PIXI.Application(opts);
    } catch(_first){
      app = new PIXI.Application(opts);
    }
    return app;
  }

  async function initPixi(){
    if (state.started) return;
    state.started = true;
    var canvas = ensureCanvas();
    if (!window.PIXI){ fallback('pixi-not-loaded'); return; }
    try{
      var PIXI = window.PIXI;
      var app = await createPixi(canvas);
      state.app = app;
      document.body.classList.add('prisma-atmosphere-ready');

      var stage = app.stage;
      var mist = new PIXI.Container();
      var sparks = new PIXI.Container();
      stage.addChild(mist);
      stage.addChild(sparks);

      var vp = getViewport();
      var blobCount = Math.min(9, Math.max(5, Math.round(vp.w / 260)));
      for (var i=0; i<blobCount; i++){
        var r = 110 + Math.random() * 230;
        var color = i % 3 === 0 ? 0x72d8ff : (i % 3 === 1 ? 0xb58bff : 0x7ff5d8);
        var b = makeCircle(color, r, .045 + Math.random() * .045);
        placeRandom(b, vp, r);
        tryBlur(b, 18 + Math.random() * 18);
        mist.addChild(b);
        state.blobs.push(b);
      }

      var sparkCount = reduced ? 0 : Math.min(96, Math.max(42, Math.round(vp.w / 18)));
      for (var j=0; j<sparkCount; j++){
        var sr = 1.2 + Math.random() * 2.8;
        var sc = j % 4 === 0 ? 0xb58bff : (j % 3 === 0 ? 0x7ff5d8 : 0x72d8ff);
        var s = makeCircle(sc, sr, .14 + Math.random() * .22);
        placeRandom(s, vp, sr);
        sparks.addChild(s);
        state.particles.push(s);
      }

      if (window.gsap && !reduced){
        window.gsap.to(mist, { x: 18, y: -10, duration: 34, repeat: -1, yoyo: true, ease: 'sine.inOut' });
        window.gsap.to(sparks, { x: -10, y: 12, duration: 26, repeat: -1, yoyo: true, ease: 'sine.inOut' });
        window.gsap.fromTo(canvas, { opacity: 0 }, { opacity: 1, duration: 1.25, ease: 'power2.out' });
      }

      function resize(){
        vp = getViewport();
        state.blobs.concat(state.particles).forEach(function(o){
          if (o.__baseX > vp.w || o.__baseY > vp.h) placeRandom(o, vp, o.__radius || 10);
        });
      }
      window.addEventListener('resize', resize, { passive:true });

      if (!reduced){
        var t = 0;
        app.ticker.add(function(tick){
          var dt = getTickerDelta(tick);
          t += dt * .016;
          for (var k=0; k<state.blobs.length; k++){
            var o = state.blobs[k];
            o.x = o.__baseX + Math.sin(t * o.__speed + o.__phase) * o.__ampX;
            o.y = o.__baseY + Math.cos(t * (o.__speed * .82) + o.__phase) * o.__ampY;
          }
          for (var q=0; q<state.particles.length; q++){
            var p = state.particles[q];
            p.x = p.__baseX + Math.sin(t * (p.__speed * 1.8) + p.__phase) * p.__ampX;
            p.y = p.__baseY + Math.cos(t * (p.__speed * 1.45) + p.__phase) * p.__ampY;
            if (typeof p.alpha === 'number') p.alpha = .12 + (Math.sin(t * 1.7 + p.__phase) + 1) * .09;
          }
        });
      }
    } catch(err){
      console.warn('[PRISMA V5] Pixi atmosphere failed, using CSS fallback:', err);
      fallback('pixi-init-failed');
    }
  }

  function installMotionAdapter(){
    if (reduced) return;
    var seen = new WeakSet();
    function micro(el, enter){
      if (!el || !el.animate) return;
      var isButton = el.matches && el.matches('button,.opButton,.dockBtn,.picker button,a[href]');
      var lift = isButton ? -2 : -1;
      var frames = enter ? [
        { transform:'translateY(0) scale(1)', filter:'brightness(1)' },
        { transform:'translateY(' + lift + 'px) scale(1.006)', filter:'brightness(1.06) saturate(1.08)' }
      ] : [
        { transform:'translateY(' + lift + 'px) scale(1.006)', filter:'brightness(1.06) saturate(1.08)' },
        { transform:'translateY(0) scale(1)', filter:'brightness(1)' }
      ];
      try{
        el.animate(frames, { duration: enter ? 180 : 220, easing:'cubic-bezier(.2,.8,.2,1)', fill:'none' });
      } catch(_err){}
    }
    function attach(el){
      if (!el || seen.has(el)) return;
      seen.add(el);
      el.addEventListener('pointerenter', function(){ micro(el, true); }, { passive:true });
      el.addEventListener('pointerleave', function(){ micro(el, false); }, { passive:true });
      el.addEventListener('focus', function(){ micro(el, true); }, { passive:true });
      el.addEventListener('blur', function(){ micro(el, false); }, { passive:true });
    }
    function scan(root){
      (root || document).querySelectorAll(SELECTOR_UI).forEach(attach);
    }
    scan(document);
    if (window.MutationObserver){
      new MutationObserver(function(records){
        records.forEach(function(r){
          r.addedNodes && r.addedNodes.forEach(function(n){
            if (n.nodeType !== 1) return;
            if (n.matches && n.matches(SELECTOR_UI)) attach(n);
            if (n.querySelectorAll) scan(n);
          });
        });
      }).observe(document.documentElement, { childList:true, subtree:true });
    }
  }

  ready(function(){
    installMotionAdapter();
    initPixi();
  });
})();
