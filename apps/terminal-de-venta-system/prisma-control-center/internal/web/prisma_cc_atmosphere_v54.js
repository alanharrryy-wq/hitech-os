(function () {
  "use strict";

  var STATE = {
    version: "v5.4-true-mist-glacier-boost",
    started: false,
    pixi: !!window.PIXI,
    gsap: !!window.gsap,
    reduced: false,
    error: null
  };

  window.PRISMA_CC_ATMO_V54 = STATE;

  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn, { once: true });
    } else {
      fn();
    }
  }

  function killOldProbe() {
    ["prisma-atmosphere-v53-root","prisma-atmosphere-v53-badge"].forEach(function(id){
      var el = document.getElementById(id);
      if (el) el.remove();
    });
  }

  function makeBadge(text) {
    var old = document.getElementById("prisma-atmo-v54-badge");
    if (old) old.remove();
    var badge = document.createElement("div");
    badge.id = "prisma-atmo-v54-badge";
    badge.textContent = text;
    document.body.appendChild(badge);
    setTimeout(function () {
      badge.style.opacity = "0.22";
      badge.style.transition = "opacity 900ms ease";
    }, 10000);
  }

  function createRoot() {
    var old = document.getElementById("prisma-atmo-v54-root");
    if (old) old.remove();

    var root = document.createElement("div");
    root.id = "prisma-atmo-v54-root";

    var canvas = document.createElement("canvas");
    canvas.id = "prisma-atmo-v54-canvas";
    canvas.setAttribute("data-prisma-atmo", "v54");

    var scrim = document.createElement("div");
    scrim.id = "prisma-atmo-v54-scrim";

    root.appendChild(canvas);
    root.appendChild(scrim);
    document.body.prepend(root);

    return { root: root, canvas: canvas, scrim: scrim };
  }

  function startCanvasAtmosphere() {
    killOldProbe();
    var els = createRoot();
    var canvas = els.canvas;
    var ctx = canvas.getContext("2d", { alpha: true });
    var w = 0, h = 0, dpr = 1;

    try {
      STATE.reduced = !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
    } catch (_) {}

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

    // Stronger-than-normal presets for quick visibility
    var mistCount = STATE.reduced ? 10 : 20;
    var particleCount = STATE.reduced ? 18 : 52;
    var sweepCount = STATE.reduced ? 1 : 3;

    var mists = [];
    var particles = [];
    var sweeps = [];

    for (var i = 0; i < mistCount; i++) {
      mists.push({
        x: Math.random() * w,
        y: Math.random() * h,
        rx: 140 + Math.random() * 260,
        ry: 80 + Math.random() * 180,
        a: 0.04 + Math.random() * 0.085,
        vx: (-0.10 + Math.random() * 0.20),
        vy: (-0.05 + Math.random() * 0.10),
        hue: Math.random() > 0.55 ? "ice" : (Math.random() > 0.5 ? "blue" : "violet"),
        phase: Math.random() * Math.PI * 2
      });
    }

    for (var p = 0; p < particleCount; p++) {
      particles.push({
        x: Math.random() * w,
        y: Math.random() * h,
        r: 0.8 + Math.random() * 2.4,
        a: 0.10 + Math.random() * 0.28,
        vx: (-0.12 + Math.random() * 0.24),
        vy: (-0.08 + Math.random() * 0.16),
        drift: Math.random() * Math.PI * 2
      });
    }

    for (var s = 0; s < sweepCount; s++) {
      sweeps.push({
        x: -w * (0.3 + Math.random() * 0.5),
        y: h * (0.16 + s * 0.23),
        width: 280 + Math.random() * 360,
        height: 120 + Math.random() * 90,
        angle: -0.24 + Math.random() * 0.18,
        speed: 0.16 + Math.random() * 0.18,
        a: 0.05 + Math.random() * 0.08
      });
    }

    var start = performance.now();
    var master = { opacity: 0.0 };

    if (window.gsap) {
      window.gsap.to(master, { opacity: 1, duration: 1.3, ease: "power2.out" });
    } else {
      master.opacity = 1;
    }

    function drawMist(now) {
      var t = (now - start) / 1000;
      ctx.clearRect(0, 0, w, h);

      // broad cold veil
      ctx.save();
      ctx.globalAlpha = 0.16 * master.opacity;
      var veil = ctx.createLinearGradient(0, 0, 0, h);
      veil.addColorStop(0, "rgba(225,239,255,.22)");
      veil.addColorStop(.45, "rgba(142,188,224,.12)");
      veil.addColorStop(1, "rgba(88,120,162,.08)");
      ctx.fillStyle = veil;
      ctx.fillRect(0, 0, w, h);
      ctx.restore();

      // glacier sweeps
      for (var j = 0; j < sweeps.length; j++) {
        var sw = sweeps[j];
        if (!STATE.reduced) sw.x += sw.speed;
        if (sw.x > w + sw.width * 1.4) sw.x = -sw.width * 1.4;

        ctx.save();
        ctx.translate(sw.x, sw.y + Math.sin(t * 0.18 + j) * 16);
        ctx.rotate(sw.angle);
        ctx.globalAlpha = sw.a * master.opacity;
        ctx.filter = "blur(26px)";
        var lg = ctx.createLinearGradient(-sw.width * 0.5, 0, sw.width * 0.5, 0);
        lg.addColorStop(0, "rgba(80,160,255,0)");
        lg.addColorStop(.38, "rgba(168,228,255,.22)");
        lg.addColorStop(.52, "rgba(220,242,255,.34)");
        lg.addColorStop(.66, "rgba(188,168,255,.16)");
        lg.addColorStop(1, "rgba(80,160,255,0)");
        ctx.fillStyle = lg;
        ctx.fillRect(-sw.width * 0.5, -sw.height * 0.5, sw.width, sw.height);
        ctx.restore();
      }

      // mist bodies
      for (var i = 0; i < mists.length; i++) {
        var m = mists[i];
        if (!STATE.reduced) {
          m.x += m.vx + Math.sin(t * 0.13 + m.phase) * 0.08;
          m.y += m.vy + Math.cos(t * 0.11 + m.phase) * 0.05;
          if (m.x < -m.rx) m.x = w + m.rx;
          if (m.x > w + m.rx) m.x = -m.rx;
          if (m.y < -m.ry) m.y = h + m.ry;
          if (m.y > h + m.ry) m.y = -m.ry;
        }

        ctx.save();
        ctx.translate(m.x, m.y);
        ctx.scale(1.25, 0.82);
        ctx.globalAlpha = m.a * (0.72 + Math.sin(t * 0.36 + m.phase) * 0.20) * master.opacity;
        ctx.filter = "blur(42px)";
        var rg = ctx.createRadialGradient(0, 0, 0, 0, 0, m.rx);
        if (m.hue === "ice") {
          rg.addColorStop(0, "rgba(235,245,255,.66)");
          rg.addColorStop(.34, "rgba(205,232,255,.28)");
          rg.addColorStop(1, "rgba(205,232,255,0)");
        } else if (m.hue === "blue") {
          rg.addColorStop(0, "rgba(152,219,255,.56)");
          rg.addColorStop(.36, "rgba(122,180,255,.22)");
          rg.addColorStop(1, "rgba(122,180,255,0)");
        } else {
          rg.addColorStop(0, "rgba(194,162,255,.42)");
          rg.addColorStop(.32, "rgba(132,162,255,.16)");
          rg.addColorStop(1, "rgba(132,162,255,0)");
        }
        ctx.fillStyle = rg;
        ctx.beginPath();
        ctx.ellipse(0, 0, m.rx, m.ry, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      }

      // frost drift ribbons
      ctx.save();
      ctx.globalAlpha = 0.11 * master.opacity;
      ctx.filter = "blur(18px)";
      for (var r = 0; r < 4; r++) {
        var yy = h * (0.15 + r * 0.18) + Math.sin(t * 0.24 + r) * 18;
        ctx.beginPath();
        ctx.lineWidth = 22 + r * 3;
        ctx.strokeStyle = r % 2 === 0 ? "rgba(206,236,255,.22)" : "rgba(152,198,255,.14)";
        ctx.moveTo(-80, yy);
        for (var x = -80; x <= w + 80; x += 42) {
          ctx.lineTo(x, yy + Math.sin(x * 0.006 + t * 0.42 + r) * (16 + r * 2));
        }
        ctx.stroke();
      }
      ctx.restore();

      // mineral dust
      ctx.save();
      for (var k = 0; k < particles.length; k++) {
        var pt = particles[k];
        if (!STATE.reduced) {
          pt.x += pt.vx + Math.sin(t * 0.6 + pt.drift) * 0.04;
          pt.y += pt.vy + Math.cos(t * 0.45 + pt.drift) * 0.03;
          if (pt.x < -5) pt.x = w + 5;
          if (pt.x > w + 5) pt.x = -5;
          if (pt.y < -5) pt.y = h + 5;
          if (pt.y > h + 5) pt.y = -5;
        }
        ctx.globalAlpha = pt.a * master.opacity;
        ctx.fillStyle = k % 6 === 0 ? "rgba(196,156,255,.52)" : "rgba(186,234,255,.56)";
        ctx.shadowBlur = 10;
        ctx.shadowColor = "rgba(176,228,255,.30)";
        ctx.beginPath();
        ctx.arc(pt.x, pt.y, pt.r, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.restore();

      // subtle center cold bloom
      ctx.save();
      ctx.globalAlpha = 0.14 * master.opacity;
      var bloom = ctx.createRadialGradient(w * 0.50, h * 0.46, 0, w * 0.50, h * 0.46, Math.max(w, h) * 0.42);
      bloom.addColorStop(0, "rgba(188,235,255,.18)");
      bloom.addColorStop(.4, "rgba(108,162,255,.09)");
      bloom.addColorStop(1, "rgba(0,0,0,0)");
      ctx.fillStyle = bloom;
      ctx.fillRect(0, 0, w, h);
      ctx.restore();

      if (!STATE.reduced) requestAnimationFrame(drawMist);
    }

    requestAnimationFrame(drawMist);
    STATE.started = true;
    makeBadge("ATMOS V5.4 · MIST+GLACIER · PIXI " + (STATE.pixi ? "YES" : "NO") + " · GSAP " + (STATE.gsap ? "YES" : "NO"));
  }

  ready(function () {
    try {
      startCanvasAtmosphere();
    } catch (err) {
      STATE.error = err && (err.stack || err.message) || String(err);
      console.error("[PRISMA CC V5.4]", err);
      makeBadge("ATMOS V5.4 ERROR");
    }
  });
})();
