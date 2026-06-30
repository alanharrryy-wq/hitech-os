"use client";

import { useEffect, useRef } from "react";

export function PrismaPcPremiumRuntime() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const root = document.documentElement;
    root.dataset.prismaPremiumVisualSystem = "pcvis-sys1";
    root.dataset.prismaPremiumReference = "pos-style-language";

    let frame = 0;
    let disposed = false;
    let cleanup = () => {};

    async function bootAmbient() {
      const canvas = canvasRef.current;
      if (!canvas || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

      try {
        const { Renderer, Triangle, Program, Mesh } = await import("ogl");
        if (disposed) return;

        const renderer = new Renderer({
          canvas,
          alpha: true,
          antialias: true,
          dpr: Math.min(window.devicePixelRatio || 1, 1.6)
        });

        const gl = renderer.gl;
        gl.clearColor(0, 0, 0, 0);

        const geometry = new Triangle(gl);
        const program = new Program(gl, {
          vertex: `
            attribute vec2 position;
            varying vec2 vUv;
            void main() {
              vUv = position * 0.5 + 0.5;
              gl_Position = vec4(position, 0.0, 1.0);
            }
          `,
          fragment: `
            precision highp float;
            varying vec2 vUv;
            uniform float uTime;
            uniform vec2 uResolution;

            float orb(vec2 p, vec2 c, float s) {
              float d = length(p - c);
              return exp(-d * s);
            }

            void main() {
              vec2 uv = vUv;
              vec2 drift = vec2(sin(uTime * 0.18) * 0.03, cos(uTime * 0.15) * 0.025);
              float a = orb(uv, vec2(0.20, 0.18) + drift, 5.6);
              float b = orb(uv, vec2(0.82, 0.20) - drift, 6.2);
              float c = orb(uv, vec2(0.52, 0.92), 4.4);
              vec3 color = vec3(0.18, 0.50, 1.0) * a + vec3(0.58, 0.42, 1.0) * b + vec3(0.70, 0.94, 1.0) * c;
              gl_FragColor = vec4(color, 0.30);
            }
          `,
          uniforms: {
            uTime: { value: 0 },
            uResolution: { value: [window.innerWidth, window.innerHeight] }
          }
        });

        const mesh = new Mesh(gl, { geometry, program });

        function resize() {
          renderer.setSize(window.innerWidth, window.innerHeight);
          program.uniforms.uResolution.value = [window.innerWidth, window.innerHeight];
        }

        function update(time: number) {
          program.uniforms.uTime.value = time * 0.001;
          renderer.render({ scene: mesh });
          frame = requestAnimationFrame(update);
        }

        resize();
        window.addEventListener("resize", resize);
        frame = requestAnimationFrame(update);

        cleanup = () => {
          window.removeEventListener("resize", resize);
          cancelAnimationFrame(frame);
          const loseContext = gl.getExtension("WEBGL_lose_context");
          loseContext?.loseContext();
        };
      } catch {
        root.dataset.prismaPremiumAmbient = "css-fallback";
      }
    }

    bootAmbient();

    return () => {
      disposed = true;
      cleanup();
    };
  }, []);

  return (
    <>
      <canvas
        ref={canvasRef}
        className="prisma-pc-premium-ambient"
        data-prisma-component="PrismaPcPremiumRuntime"
        data-library="ogl"
        aria-hidden="true"
      />
      <span
        className="prisma-pc-premium-runtime-contract"
        data-radix-ready="dialog dropdown-menu scroll-area select tabs tooltip slot"
        data-vanilla-extract-ready="premium-token-layer"
        aria-hidden="true"
      />
    </>
  );
}
