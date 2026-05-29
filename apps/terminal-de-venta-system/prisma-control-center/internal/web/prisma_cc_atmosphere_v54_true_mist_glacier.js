(function () {
  "use strict";

  var CONFIG = {
    version: "v5.4-true-mist-glacier",
    visiblePreset: "high-noticeable",
    rootId: "prisma-atmosphere-v54-root",
    scrimId: "prisma-atmosphere-v54-scrim",
    canvasId: "prisma-atmosphere-v54-canvas",
    // intentionally higher than normal so the user sees it in chinga
    mistCount: 32,
    particleCount: 125,
    glacierSweepCount: 5,
    parallaxPx: 12,
    fallback: false,
    pixi: false,
    gsap: false,
    error: null
  };

  window.PRISMA_CC_ATMOSPHERE_V54 = CONFIG;

  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn, { once: true });
    } else {
      fn();
    }
  }

  function reducedMotion() {
    try { return !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches); }
    catch (_) { return false; }
  }

  function removeOld() {
    [
      "prisma-atmosphere-v53-root",
      "prisma-atmosphere-v53-badge",
      "prisma-atmosphere-v54-root",
      "prisma-atmosphere-v54-scrim"
    ].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) el.remove();
    });
  }

  function createShell() {
    removeOld();
    var root = document.createElement("div");
    root.id = CONFIG.rootId;
    root.setAttribute("aria-hidden", "true");

    var scrim = document.createElement("div");
    scrim.id = CONFIG.scrimId;
    scrim.setAttribute("aria-hidden", "true");

    document.body.prepend(scrim);
    document.body.prepend(root);
    return root;
  }

  function makeMistCanvas(size, inner, middle, outer) {
    var c = document.createElement("canvas");
    c.width = size;
    c.height = size;
    var ctx = c.getContext("2d");
    var g = ctx.createRadialGradient(size * .50, size * .50, 0, size * .50, size * .50, size * .50);
    g.addColorStop(0, inner);
    g.addColorStop(.36, middle);
    g.addColorStop(1, outer);
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, size, size);
    return c;
  }

  function makeSweepCanvas(w, h) {
    var c = document.createElement("canvas");
    c.width = w;
    c.height = h;
    var ctx = c.getContext("2d");
    ctx.clearRect(0, 0, w, h);
    var g = ctx.createLinearGradient(0, h * .5, w, h * .5);
    g.addColorStop(0, "rgba(255,255,255,0)");
    g.addColorStop(.22, "rgba(150,218,255,.00)");
    g.addColorStop(.42, "rgba(175,232,255,.30)");
    g.addColorStop(.50, "rgba(238,248,255,.52)");
    g.addColorStop(.58, "rgba(160,220,255,.28)");
    g.addColorStop(.78, "rgba(170,145,255,.08)");
    g.addColorStop(1, "rgba(255,255,255,0)");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, w, h);
    return c;
  }

  async function startPixi(root) {
    if (!window.PIXI) return false;
    var PIXI = window.PIXI;
    var app;

    // Pixi v8 async init vs v7 constructor.
    if (typeof PIXI.Application === "function") {
      app = new PIXI.Application();
      if (typeof app.init === "function") {
        await app.init({ resizeTo: window, backgroundAlpha: 0, antialias: true, autoDensity: true, resolution: Math.min(window.devicePixelRatio || 1, 2) });
      } else {
        app = new PIXI.Application({ resizeTo: window, transparent: true, antialias: true, autoDensity: true, resolution: Math.min(window.devicePixelRatio || 1, 2) });
      }
    }

    var view = app && (app.canvas || app.view);
    if (!view) return false;
    view.id = CONFIG.canvasId;
    view.setAttribute("data-prisma-atmosphere", "v54-pixi-true-mist-glacier");
    root.appendChild(view);

    CONFIG.pixi = true;
    CONFIG.gsap = !!window.gsap;

    var reduce = reducedMotion();
    var w = window.innerWidth || 1280;
    var h = window.innerHeight || 720;
    var stage = app.stage;
    var mist = new PIXI.Container();
    var sweeps = new PIXI.Container();
    var dust = new PIXI.Container();
    stage.addChild(mist);
    stage.addChild(sweeps);
    stage.addChild(dust);

    function blendScreen(sprite) {
      try {
        if (PIXI.BLEND_MODES && PIXI.BLEND_MODES.SCREEN !== undefined) sprite.blendMode = PIXI.BLEND_MODES.SCREEN;
        else sprite.blendMode = "screen";
      } catch (_) {}
    }

    var textures = [
      PIXI.Texture.from(makeMistCanvas(512, "rgba(218,241,255,.34)", "rgba(126,207,255,.15)", "rgba(126,207,255,0)")),
      PIXI.Texture.from(makeMistCanvas(512, "rgba(235,247,255,.24)", "rgba(180,205,255,.11)", "rgba(180,205,255,0)")),
      PIXI.Texture.from(makeMistCanvas(512, "rgba(195,232,255,.20)", "rgba(142,184,255,.10)", "rgba(142,184,255,0)"))
    ];
    var mistSprites = [];
    var count = reduce ? 12 : CONFIG.mistCount;
    for (var i = 0; i < count; i++) {
      var s = new PIXI.Sprite(textures[i % textures.length]);
      s.anchor.set(.5);
      s.x = Math.random() * w;
      s.y = Math.random() * h;
      var scale = 1.0 + Math.random() * 2.6;
      s.scale.set(scale * (1.2 + Math.random() * .9), scale * (.46 + Math.random() * .65));
      s.rotation = (Math.random() - .5) * .55;
      s.alpha = .13 + Math.random() * .20;
      s._vx = (-.065 + Math.random() * .13) * (i % 3 === 0 ? 2.1 : 1);
      s._vy = (-.025 + Math.random() * .05);
      s._phase = Math.random() * Math.PI * 2;
      s._baseAlpha = s.alpha;
      blendScreen(s);
      mist.addChild(s);
      mistSprites.push(s);
    }

    var sweepTex = PIXI.Texture.from(makeSweepCanvas(1400, 220));
    var sweepSprites = [];
    for (var j = 0; j < CONFIG.glacierSweepCount; j++) {
      var sw = new PIXI.Sprite(sweepTex);
      sw.anchor.set(.5);
      sw.x = w * (.06 + Math.random() * .92);
      sw.y = h * (.12 + Math.random() * .80);
      sw.scale.set(1.05 + Math.random() * .65, .30 + Math.random() * .28);
      sw.rotation = (-15 + Math.random() * 28) * Math.PI / 180;
      sw.alpha = .15 + Math.random() * .18;
      sw._vx = .035 + Math.random() * .05;
      sw._phase = Math.random() * Math.PI * 2;
      blendScreen(sw);
      sweeps.addChild(sw);
      sweepSprites.push(sw);
    }

    var particleTexture = PIXI.Texture.from(makeMistCanvas(64, "rgba(220,250,255,.78)", "rgba(120,229,255,.25)", "rgba(120,229,255,0)"));
    var particleSprites = [];
    var pCount = reduce ? 36 : CONFIG.particleCount;
    for (var k = 0; k < pCount; k++) {
      var p = new PIXI.Sprite(particleTexture);
      p.anchor.set(.5);
      p.x = Math.random() * w;
      p.y = Math.random() * h;
      var ps = .025 + Math.random() * .075;
      p.scale.set(ps);
      p.alpha = .18 + Math.random() * .42;
      p._vx = -.018 + Math.random() * .036;
      p._vy = -.035 - Math.random() * .075;
      p._phase = Math.random() * Math.PI * 2;
      blendScreen(p);
      dust.addChild(p);
      particleSprites.push(p);
    }

    function resize() {
      w = window.innerWidth || 1280;
      h = window.innerHeight || 720;
    }
    window.addEventListener("resize", resize, { passive: true });

    var t0 = performance.now();
    function tick() {
      var t = (performance.now() - t0) / 1000;
      if (!reduce) {
        for (var a = 0; a < mistSprites.length; a++) {
          var ms = mistSprites[a];
          ms.x += ms._vx + Math.sin(t * .21 + ms._phase) * .035;
          ms.y += ms._vy + Math.cos(t * .18 + ms._phase) * .022;
          ms.alpha = ms._baseAlpha * (.74 + Math.sin(t * .42 + ms._phase) * .26);
          if (ms.x < -520) ms.x = w + 520;
          if (ms.x > w + 520) ms.x = -520;
          if (ms.y < -360) ms.y = h + 360;
          if (ms.y > h + 360) ms.y = -360;
        }
        for (var b = 0; b < sweepSprites.length; b++) {
          var gs = sweepSprites[b];
          gs.x += gs._vx;
          gs.y += Math.sin(t * .18 + gs._phase) * .025;
          gs.alpha = (.13 + b * .018) + Math.sin(t * .35 + gs._phase) * .055;
          if (gs.x > w + 820) gs.x = -820;
        }
        for (var c = 0; c < particleSprites.length; c++) {
          var dp = particleSprites[c];
          dp.x += dp._vx + Math.sin(t * .55 + dp._phase) * .012;
          dp.y += dp._vy;
          dp.alpha = (.15 + (c % 5) * .055) * (.75 + Math.sin(t * .9 + dp._phase) * .25);
          if (dp.y < -40) { dp.y = h + 40; dp.x = Math.random() * w; }
          if (dp.x < -40) dp.x = w + 40;
          if (dp.x > w + 40) dp.x = -40;
        }
      }
    }
    app.ticker.add(tick);

    if (window.gsap) {
      window.gsap.fromTo(root, { opacity: 0 }, { opacity: 1, duration: 1.15, ease: "power2.out" });
      window.gsap.to(mist, { alpha: .92, duration: 8, yoyo: true, repeat: -1, ease: "sine.inOut" });
      window.gsap.to(sweeps, { alpha: .78, duration: 5.5, yoyo: true, repeat: -1, ease: "sine.inOut" });
    }

    addParallax(root, stage);
    return true;
  }

  function addParallax(root, stage) {
    var reduce = reducedMotion();
    if (reduce) return;
    var tx = 0, ty = 0, cx = 0, cy = 0;
    window.addEventListener("pointermove", function (ev) {
      var w = window.innerWidth || 1;
      var h = window.innerHeight || 1;
      tx = ((ev.clientX / w) - .5) * CONFIG.parallaxPx;
      ty = ((ev.clientY / h) - .5) * CONFIG.parallaxPx;
    }, { passive: true });
    function loop() {
      cx += (tx - cx) * .035;
      cy += (ty - cy) * .035;
      if (stage) {
        stage.x = cx;
        stage.y = cy;
      } else if (root) {
        root.style.transform = "translate3d(" + cx.toFixed(2) + "px," + cy.toFixed(2) + "px,0)";
      }
      requestAnimationFrame(loop);
    }
    requestAnimationFrame(loop);
  }

  function startFallback(root) {
    CONFIG.fallback = true;
    CONFIG.gsap = !!window.gsap;

    var canvas = document.createElement("canvas");
    canvas.id = CONFIG.canvasId;
    canvas.setAttribute("data-prisma-atmosphere", "v54-canvas-true-mist-glacier");
    root.appendChild(canvas);

    var ctx = canvas.getContext("2d", { alpha: true });
    var w = 0, h = 0, dpr = 1;
    var reduce = reducedMotion();

    function resize() {
      w = window.innerWidth || document.documentElement.clientWidth || 1280;
      h = window.innerHeight || document.documentElement.clientHeight || 720;
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.max(1, Math.floor(w * dpr));
      canvas.height = Math.max(1, Math.floor(h * dpr));
      canvas.style.width = w + "px";
      canvas.style.height = h + "px";
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    resize();
    window.addEventListener("resize", resize, { passive: true });

    var mist = [];
    var count = reduce ? 12 : CONFIG.mistCount;
    for (var i = 0; i < count; i++) {
      mist.push({
        x: Math.random() * w,
        y: Math.random() * h,
        rx: 180 + Math.random() * 520,
        ry: 70 + Math.random() * 230,
        vx: -.12 + Math.random() * .24,
        vy: -.045 + Math.random() * .09,
        a: .10 + Math.random() * .17,
        phase: Math.random() * Math.PI * 2,
        kind: i % 3
      });
    }

    var dust = [];
    var pCount = reduce ? 40 : CONFIG.particleCount;
    for (var j = 0; j < pCount; j++) {
      dust.push({
        x: Math.random() * w,
        y: Math.random() * h,
        r: .6 + Math.random() * 2.2,
        vx: -.035 + Math.random() * .07,
        vy: -.08 - Math.random() * .16,
        a: .16 + Math.random() * .40,
        phase: Math.random() * Math.PI * 2
      });
    }

    var sweeps = [];
    for (var k = 0; k < CONFIG.glacierSweepCount; k++) {
      sweeps.push({
        x: Math.random() * w,
        y: h * (.12 + Math.random() * .72),
        width: 620 + Math.random() * 880,
        angle: (-18 + Math.random() * 32) * Math.PI / 180,
        vx: .11 + Math.random() * .09,
        a: .10 + Math.random() * .18,
        phase: Math.random() * Math.PI * 2
      });
    }

    var t0 = performance.now();
    function draw(now) {
      var t = (now - t0) / 1000;
      ctx.clearRect(0, 0, w, h);
      ctx.save();
      ctx.globalCompositeOperation = "screen";

      // true cold mist: broad horizontal vapor banks
      for (var i = 0; i < mist.length; i++) {
        var m = mist[i];
        if (!reduce) {
          m.x += m.vx + Math.sin(t * .22 + m.phase) * .055;
          m.y += m.vy + Math.cos(t * .18 + m.phase) * .035;
          if (m.x < -m.rx) m.x = w + m.rx;
          if (m.x > w + m.rx) m.x = -m.rx;
          if (m.y < -m.ry) m.y = h + m.ry;
          if (m.y > h + m.ry) m.y = -m.ry;
        }
        var pulse = reduce ? 1 : (.78 + Math.sin(t * .46 + m.phase) * .22);
        var alpha = m.a * pulse;
        ctx.save();
        ctx.translate(m.x, m.y);
        ctx.rotate(Math.sin(t * .08 + m.phase) * .10);
        ctx.scale(m.rx / 220, m.ry / 220);
        var g = ctx.createRadialGradient(0, 0, 0, 0, 0, 220);
        if (m.kind === 0) {
          g.addColorStop(0, "rgba(229,246,255," + alpha + ")");
          g.addColorStop(.42, "rgba(133,211,255," + (alpha * .44) + ")");
        } else if (m.kind === 1) {
          g.addColorStop(0, "rgba(210,234,255," + (alpha * .82) + ")");
          g.addColorStop(.42, "rgba(178,157,255," + (alpha * .28) + ")");
        } else {
          g.addColorStop(0, "rgba(240,250,255," + (alpha * .76) + ")");
          g.addColorStop(.42, "rgba(170,223,255," + (alpha * .34) + ")");
        }
        g.addColorStop(1, "rgba(130,190,255,0)");
        ctx.fillStyle = g;
        ctx.beginPath();
        ctx.arc(0, 0, 220, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      }

      // glacier light sweeps: slow angled cold specular passes
      for (var s = 0; s < sweeps.length; s++) {
        var sw = sweeps[s];
        if (!reduce) {
          sw.x += sw.vx;
          sw.y += Math.sin(t * .18 + sw.phase) * .045;
          if (sw.x > w + sw.width) sw.x = -sw.width;
        }
        ctx.save();
        ctx.translate(sw.x, sw.y);
        ctx.rotate(sw.angle);
        var grad = ctx.createLinearGradient(-sw.width * .5, 0, sw.width * .5, 0);
        var a = sw.a * (reduce ? .8 : (.75 + Math.sin(t * .42 + sw.phase) * .25));
        grad.addColorStop(0, "rgba(255,255,255,0)");
        grad.addColorStop(.36, "rgba(133,221,255,0)");
        grad.addColorStop(.48, "rgba(170,232,255," + (a * .72) + ")");
        grad.addColorStop(.50, "rgba(242,251,255," + a + ")");
        grad.addColorStop(.54, "rgba(180,151,255," + (a * .28) + ")");
        grad.addColorStop(.68, "rgba(133,221,255,0)");
        grad.addColorStop(1, "rgba(255,255,255,0)");
        ctx.fillStyle = grad;
        ctx.fillRect(-sw.width * .5, -58, sw.width, 116);
        ctx.restore();
      }

      // mineral/snow dust
      for (var d = 0; d < dust.length; d++) {
        var p = dust[d];
        if (!reduce) {
          p.x += p.vx + Math.sin(t * .5 + p.phase) * .018;
          p.y += p.vy;
          if (p.y < -8) { p.y = h + 8; p.x = Math.random() * w; }
          if (p.x < -8) p.x = w + 8;
          if (p.x > w + 8) p.x = -8;
        }
        var pa = p.a * (reduce ? .65 : (.65 + Math.sin(t * .88 + p.phase) * .35));
        var pg = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r * 8);
        pg.addColorStop(0, "rgba(218,249,255," + pa + ")");
        pg.addColorStop(.28, "rgba(119,232,255," + (pa * .32) + ")");
        pg.addColorStop(1, "rgba(119,232,255,0)");
        ctx.fillStyle = pg;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r * 8, 0, Math.PI * 2);
        ctx.fill();
      }

      ctx.restore();
      if (!reduce) requestAnimationFrame(draw);
    }

    requestAnimationFrame(draw);

    if (window.gsap) {
      window.gsap.fromTo(root, { opacity: 0 }, { opacity: 1, duration: 1.1, ease: "power2.out" });
    }
    addParallax(root, null);
  }

  ready(function () {
    try {
      var root = createShell();
      Promise.resolve(startPixi(root)).then(function (usedPixi) {
        if (!usedPixi) startFallback(root);
        document.documentElement.setAttribute("data-prisma-atmosphere", CONFIG.version);
        console.info("[PRISMA CC Atmosphere]", CONFIG);
      }).catch(function (err) {
        CONFIG.error = err && (err.stack || err.message) || String(err);
        console.warn("[PRISMA CC Atmosphere] Pixi failed, falling back to Canvas2D", err);
        startFallback(root);
      });
    } catch (err) {
      CONFIG.error = err && (err.stack || err.message) || String(err);
      console.error("[PRISMA CC Atmosphere V5.4]", err);
    }
  });
})();
