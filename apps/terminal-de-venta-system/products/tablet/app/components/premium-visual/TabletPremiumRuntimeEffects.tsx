
"use client";

import { useEffect, useRef } from "react";
import * as Tooltip from "@radix-ui/react-tooltip";
import { motion, useReducedMotion } from "motion/react";
import styles from "./tablet-premium-effects.module.css";

export function TabletPremiumRuntimeEffects() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const reduceMotion = useReducedMotion();

  useEffect(() => {
    document.body.dataset.prismaPremiumRuntime = "library-effects";
    document.body.dataset.prismaPremiumWeight = "effect-assets-over-3mb";
    document.documentElement.dataset.prismaLibraryMotion = reduceMotion ? "reduced" : "motion-ogl-radix";
    return () => {
      delete document.body.dataset.prismaPremiumRuntime;
      delete document.body.dataset.prismaPremiumWeight;
      delete document.documentElement.dataset.prismaLibraryMotion;
    };
  }, [reduceMotion]);

  useEffect(() => {
    if (reduceMotion || !canvasRef.current) return;
    let raf = 0;
    let renderer: any;
    let gl: WebGLRenderingContext | undefined;
    let mesh: any;
    let program: any;
    let disposed = false;

    import("ogl").then(({ Renderer, Program, Mesh, Triangle }) => {
      if (disposed || !canvasRef.current) return;
      const canvas = canvasRef.current;
      renderer = new Renderer({ canvas, alpha: true, dpr: Math.min(window.devicePixelRatio || 1, 1.5) });
      gl = renderer.gl;
      gl.clearColor(0, 0, 0, 0);
      const geometry = new Triangle(gl);
      program = new Program(gl, {
        vertex: `attribute vec2 uv; attribute vec2 position; varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position, 0.0, 1.0); }`,
        fragment: `precision highp float; varying vec2 vUv; uniform float uTime; void main(){ vec2 p=vUv; float a=sin((p.x*3.2+uTime*.22))*0.5+0.5; float b=sin((p.y*4.1-uTime*.17))*0.5+0.5; float edge=smoothstep(.0,.75,1.0-distance(p,vec2(.78,.18))); vec3 c=mix(vec3(.45,.78,1.0),vec3(1.0,.98,.90),a*b); gl_FragColor=vec4(c, .105*edge + .035*a*b); }`,
        uniforms: { uTime: { value: 0 } },
      });
      mesh = new Mesh(gl, { geometry, program });
      const resize = () => renderer.setSize(window.innerWidth, window.innerHeight);
      const render = (t: number) => {
        if (disposed) return;
        program.uniforms.uTime.value = t * 0.001;
        renderer.render({ scene: mesh });
        raf = requestAnimationFrame(render);
      };
      resize();
      window.addEventListener("resize", resize);
      raf = requestAnimationFrame(render);
      return () => window.removeEventListener("resize", resize);
    }).catch(() => undefined);

    return () => {
      disposed = true;
      if (raf) cancelAnimationFrame(raf);
      try { gl?.getExtension("WEBGL_lose_context")?.loseContext(); } catch {}
    };
  }, [reduceMotion]);

  return (
    <Tooltip.Provider delayDuration={240} skipDelayDuration={120}>
      <div className={styles.effects} data-prisma-component="TabletPremiumRuntimeEffects" data-prisma-libraries="radix-tooltip motion ogl-runtime">
        <canvas ref={canvasRef} className={styles.oglCanvas} aria-hidden="true" />
        <motion.span className={styles.auroraOne} aria-hidden="true" animate={reduceMotion ? undefined : { x: [0, 10, -6, 0], y: [0, -8, 4, 0], opacity: [0.32, 0.46, 0.34] }} transition={{ duration: 9, repeat: Infinity, ease: "easeInOut" }} />
        <motion.span className={styles.auroraTwo} aria-hidden="true" animate={reduceMotion ? undefined : { x: [0, -8, 7, 0], y: [0, 6, -5, 0], opacity: [0.22, 0.38, 0.24] }} transition={{ duration: 11, repeat: Infinity, ease: "easeInOut" }} />
        <span className={styles.noise} aria-hidden="true" />
      </div>
      <Tooltip.Root>
        <Tooltip.Trigger asChild>
          <span className={styles.runtimeBadge} tabIndex={0} data-prisma-component="TabletPremiumLibraryBadge">
            Visual OS
          </span>
        </Tooltip.Trigger>
        <Tooltip.Portal>
          <Tooltip.Content className={styles.tooltip} side="left" sideOffset={8}>
            Tablet Cloudglass Light activo Â· Radix + Motion + OGL gobernados
            <Tooltip.Arrow className={styles.tooltipArrow} />
          </Tooltip.Content>
        </Tooltip.Portal>
      </Tooltip.Root>
    </Tooltip.Provider>
  );
}
