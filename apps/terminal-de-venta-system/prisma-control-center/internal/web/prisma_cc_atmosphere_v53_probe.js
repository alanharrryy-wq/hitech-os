(function () {
  "use strict";

  var STATE = {
    version: "v5.3-probe",
    started: false,
    pixi: false,
    gsap: false,
    fallbackCanvas: true,
    error: null
  };

  window.PRISMA_CC_ATMOSPHERE_V53 = STATE;

  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn, { once: true });
    } else {
      fn();
    }
  }

  function makeBadge(text) {
    var old = document.getElementById("prisma-atmosphere-v53-badge");
    if (old) old.remove();

    var badge = document.createElement("div");
    badge.id = "prisma-atmosphere-v53-badge";
    badge.textContent = text;
    document.body.appendChild(badge);

    setTimeout(function () {
      badge.style.opacity = "0.18";
      badge.style.transition = "opacity 900ms ease";
    }, 9000);
  }

  function startFallbackCanvas() {
    var old = document.getElementById("prisma-atmosphere-v53-root");
    if (old) old.remove();

    var root = document.createElement("div");
    root.id = "prisma-atmosphere-v53-root";

    var canvas = document.createElement("canvas");
    canvas.id = "prisma-atmosphere-v53-canvas";
    canvas.setAttribute("data-prisma-atmosphere", "v53-probe");
    root.appendChild(canvas);

    document.body.prepend(root);

    var ctx = canvas.getContext("2d", { alpha: true });
    var w = 0;
    var h = 0;
    var dpr = Math.min(window.devicePixelRatio || 1, 2);

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

    var reduced = false;
    try {
      reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    } catch (_) {}

    var particles = [];
    var count = reduced ? 10 : 34;

    for (var i = 0; i < count; i++) {
      particles.push({
        x: Math.random() * w,
        y: Math.random() * h,
        r: 60 + Math.random() * 190,
        vx: (-0.16 + Math.random() * 0.32),
        vy: (-0.08 + Math.random() * 0.16),
        a: 0.045 + Math.random() * 0.09,
        hue: Math.random() > 0.5 ? "blue" : "violet"
      });
    }

    var t0 = performance.now();

    function draw(now) {
      var t = (now - t0) / 1000;
      ctx.clearRect(0, 0, w, h);

      var bg = ctx.createRadialGradient(w * 0.5, h * 0.48, 0, w * 0.5, h * 0.48, Math.max(w, h) * 0.72);
      bg.addColorStop(0, "rgba(85, 173, 255, 0.045)");
      bg.addColorStop(0.54, "rgba(91, 84, 180, 0.035)");
      bg.addColorStop(1, "rgba(0, 0, 0, 0)");
      ctx.fillStyle = bg;
      ctx.fillRect(0, 0, w, h);

      for (var i = 0; i < particles.length; i++) {
        var p = particles[i];

        if (!reduced) {
          p.x += p.vx + Math.sin(t * 0.32 + i) * 0.035;
          p.y += p.vy + Math.cos(t * 0.27 + i) * 0.025;

          if (p.x < -p.r) p.x = w + p.r;
          if (p.x > w + p.r) p.x = -p.r;
          if (p.y < -p.r) p.y = h + p.r;
          if (p.y > h + p.r) p.y = -p.r;
        }

        var pulse = reduced ? 1 : (0.74 + Math.sin(t * 0.9 + i * 0.77) * 0.26);
        var alpha = p.a * pulse;

        var g = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r);
        if (p.hue === "blue") {
          g.addColorStop(0, "rgba(105, 219, 255, " + alpha + ")");
          g.addColorStop(0.34, "rgba(105, 169, 255, " + (alpha * 0.42) + ")");
          g.addColorStop(1, "rgba(105, 169, 255, 0)");
        } else {
          g.addColorStop(0, "rgba(190, 139, 255, " + alpha + ")");
          g.addColorStop(0.34, "rgba(132, 150, 255, " + (alpha * 0.36) + ")");
          g.addColorStop(1, "rgba(132, 150, 255, 0)");
        }

        ctx.fillStyle = g;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fill();
      }

      ctx.globalAlpha = reduced ? 0.10 : 0.18;
      ctx.strokeStyle = "rgba(154, 227, 255, .20)";
      ctx.lineWidth = 1;
      for (var j = 0; j < 3; j++) {
        var yy = h * (0.22 + j * 0.23) + Math.sin(t * 0.22 + j) * 18;
        ctx.beginPath();
        ctx.moveTo(-40, yy);
        for (var x = -40; x <= w + 40; x += 40) {
          ctx.lineTo(x, yy + Math.sin(x * 0.006 + t * 0.55 + j) * 18);
        }
        ctx.stroke();
      }
      ctx.globalAlpha = 1;

      if (!reduced) requestAnimationFrame(draw);
    }

    requestAnimationFrame(draw);
    STATE.started = true;
    STATE.pixi = !!window.PIXI;
    STATE.gsap = !!window.gsap;

    makeBadge("ATMOS V5.3 ON · PIXI " + (STATE.pixi ? "YES" : "NO") + " · GSAP " + (STATE.gsap ? "YES" : "NO"));
  }

  ready(function () {
    try {
      startFallbackCanvas();

      if (window.gsap) {
        window.gsap.fromTo(
          "#prisma-atmosphere-v53-root",
          { opacity: 0 },
          { opacity: 1, duration: 1.2, ease: "power2.out" }
        );
      }
    } catch (err) {
      STATE.error = err && (err.stack || err.message) || String(err);
      makeBadge("ATMOS V5.3 ERROR");
      console.error("[PRISMA Atmosphere V5.3]", err);
    }
  });
})();
