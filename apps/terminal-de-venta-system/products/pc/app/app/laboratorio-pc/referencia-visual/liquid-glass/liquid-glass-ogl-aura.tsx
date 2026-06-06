"use client";

import { useEffect, useRef } from "react";
import { Mesh, Program, Renderer, Triangle } from "ogl";

type LiquidGlassOglAuraProps = {
  accentRgb: string;
  ringRgb: string;
  className?: string;
};

function parseRgb(value: string): [number, number, number] {
  const parts = value.split(",").map((part) => Number(part.trim()) / 255);
  return [parts[0] || 1, parts[1] || 1, parts[2] || 1];
}

export function LiquidGlassOglAura({ accentRgb, ringRgb, className }: LiquidGlassOglAuraProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let animationFrame = 0;
    let renderer: Renderer | null = null;

    try {
      renderer = new Renderer({
        canvas,
        alpha: true,
        antialias: true,
        dpr: Math.min(window.devicePixelRatio || 1, 1.5),
      });

      const gl = renderer.gl;
      gl.clearColor(0, 0, 0, 0);

      const geometry = new Triangle(gl);
      const program = new Program(gl, {
        vertex: `
          attribute vec2 position;
          attribute vec2 uv;
          varying vec2 vUv;
          void main() {
            vUv = uv;
            gl_Position = vec4(position, 0.0, 1.0);
          }
        `,
        fragment: `
          precision highp float;
          uniform float uTime;
          uniform vec3 uAccent;
          uniform vec3 uRing;
          uniform vec2 uResolution;
          varying vec2 vUv;

          float orb(vec2 p, vec2 c, float r) {
            float d = distance(p, c);
            return smoothstep(r, 0.0, d);
          }

          void main() {
            vec2 uv = vUv;
            vec2 drift = vec2(sin(uTime * 0.16) * 0.035, cos(uTime * 0.11) * 0.028);
            float a = orb(uv, vec2(0.18, 0.18) + drift, 0.58);
            float b = orb(uv, vec2(0.86, 0.08) - drift * 0.7, 0.42);
            float c = orb(uv, vec2(0.56, 0.92) + drift * 0.45, 0.52);
            vec3 color = uAccent * a * 0.16 + uRing * b * 0.11 + mix(uAccent, uRing, 0.55) * c * 0.08;
            float alpha = clamp((a * 0.18 + b * 0.11 + c * 0.10), 0.0, 0.26);
            gl_FragColor = vec4(color, alpha);
          }
        `,
        uniforms: {
          uTime: { value: 0 },
          uAccent: { value: parseRgb(accentRgb) },
          uRing: { value: parseRgb(ringRgb) },
          uResolution: { value: [1, 1] },
        },
      });

      const mesh = new Mesh(gl, { geometry, program });

      const resize = () => {
        const width = Math.max(1, canvas.clientWidth || window.innerWidth);
        const height = Math.max(1, canvas.clientHeight || window.innerHeight);
        renderer?.setSize(width, height);
        program.uniforms.uResolution.value = [width, height];
      };

      const render = (time: number) => {
        program.uniforms.uTime.value = prefersReducedMotion ? 0 : time * 0.001;
        program.uniforms.uAccent.value = parseRgb(accentRgb);
        program.uniforms.uRing.value = parseRgb(ringRgb);
        renderer?.render({ scene: mesh });
        if (!prefersReducedMotion) {
          animationFrame = window.requestAnimationFrame(render);
        }
      };

      resize();
      window.addEventListener("resize", resize);
      animationFrame = window.requestAnimationFrame(render);

      return () => {
        window.removeEventListener("resize", resize);
        if (animationFrame) window.cancelAnimationFrame(animationFrame);
      };
    } catch (error) {
      console.warn("LiquidGlassOglAura disabled", error);
      return () => {
        if (animationFrame) window.cancelAnimationFrame(animationFrame);
      };
    }
  }, [accentRgb, ringRgb]);

  return <canvas ref={canvasRef} className={className} aria-hidden="true" />;
}
