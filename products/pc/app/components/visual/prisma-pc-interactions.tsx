
"use client";

import { useEffect, useMemo, useState } from "react";
import { Command } from "cmdk";
import { Toaster, toast } from "sonner";
import { AnimatePresence, motion } from "motion/react";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { Search, X, Sparkles, Activity, FileText, Settings, RefreshCw } from "lucide-react";

gsap.registerPlugin(useGSAP);

type CommandAction = {
  label: string;
  hint: string;
  href?: string;
  toast?: string;
  icon: "search" | "spark" | "activity" | "file" | "settings" | "sync";
};

const ICONS = {
  search: Search,
  spark: Sparkles,
  activity: Activity,
  file: FileText,
  settings: Settings,
  sync: RefreshCw
};

export function PrismaPcInteractionLayer({ currentPath, currentTitle }: { currentPath: string; currentTitle: string }) {
  const [open, setOpen] = useState(false);

  const actions = useMemo<CommandAction[]>(() => [
    { label: "Revisar ventas", hint: "Ir al control de ventas y caja", href: "/sales-control", icon: "activity" },
    { label: "Ver hoy", hint: "Abrir centro de decisiones", href: "/dashboard", icon: "spark" },
    { label: "Sincronización", hint: "Revisar estado de sincronización", href: "/sync", icon: "sync" },
    { label: "Evidencia técnica", hint: "Abrir detalles auditables de la pantalla", toast: "Evidencia lista para revisión", icon: "file" },
    { label: "Configurar vista", hint: "Ajustar densidad, foco y modo visual", href: "/settings", icon: "settings" }
  ], []);

  useGSAP(() => {
    if (typeof window === "undefined") return;
    if (window.matchMedia?.("(prefers-reduced-motion: reduce)").matches) return;

    gsap.fromTo(
      ".sidebar, .topbar, .hero, .card",
      { y: 18, opacity: 0, filter: "blur(10px)" },
      { y: 0, opacity: 1, filter: "blur(0px)", duration: 0.85, stagger: 0.045, ease: "power3.out", delay: 0.04 }
    );

    gsap.to(".shell", {
      "--prisma-bg-drift-x": "18px",
      "--prisma-bg-drift-y": "-10px",
      duration: 32,
      repeat: -1,
      yoyo: true,
      ease: "sine.inOut"
    });

    gsap.to(".brand-logo-img", {
      filter: "drop-shadow(0 18px 28px rgba(120,170,255,.38)) saturate(1.18)",
      duration: 3.4,
      repeat: -1,
      yoyo: true,
      ease: "sine.inOut"
    });
  }, []);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setOpen((value) => !value);
      }
      if (event.key === "Escape") setOpen(false);
    };

    const onClick = (event: MouseEvent) => {
      const target = event.target as HTMLElement | null;
      const primary = target?.closest?.(".btn-primary");
      if (primary) {
        toast.success("Acción registrada", {
          description: "PRISMA dejó la decisión lista para seguimiento operativo."
        });
      }
    };

    window.addEventListener("keydown", onKeyDown);
    document.addEventListener("click", onClick);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
      document.removeEventListener("click", onClick);
    };
  }, []);

  const runAction = (action: CommandAction) => {
    setOpen(false);
    if (action.toast) {
      toast(action.toast, { description: `Contexto: ${currentTitle}` });
      return;
    }
    if (action.href && action.href !== currentPath) {
      window.location.href = action.href;
    } else {
      toast("Ya estás en esta vista", { description: currentTitle });
    }
  };

  return (
    <>
      <Toaster position="bottom-right" richColors closeButton theme="dark" />
      <button className="prisma-command-orb" type="button" onClick={() => setOpen(true)} aria-label="Abrir comandos de PRISMA">
        <Search size={16} aria-hidden="true" />
        <span>Ctrl K</span>
      </button>

      <AnimatePresence>
        {open ? (
          <motion.div
            className="prisma-command-backdrop"
            role="presentation"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onMouseDown={(event) => {
              if (event.target === event.currentTarget) setOpen(false);
            }}
          >
            <motion.div
              className="prisma-command-panel"
              role="dialog"
              aria-modal="true"
              aria-label="Comandos de PRISMA"
              initial={{ opacity: 0, y: 18, scale: 0.97, filter: "blur(10px)" }}
              animate={{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)" }}
              exit={{ opacity: 0, y: 12, scale: 0.98, filter: "blur(8px)" }}
              transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
            >
              <div className="prisma-command-head">
                <div>
                  <span className="kicker">Command glass</span>
                  <strong>Acciones rápidas</strong>
                </div>
                <button type="button" onClick={() => setOpen(false)} aria-label="Cerrar comandos">
                  <X size={17} />
                </button>
              </div>
              <Command loop shouldFilter>
                <div className="prisma-command-input-row">
                  <Search size={16} aria-hidden="true" />
                  <Command.Input autoFocus placeholder="Buscar módulo, acción o evidencia…" />
                </div>
                <Command.List className="prisma-command-list">
                  <Command.Empty className="prisma-command-empty">No encontré ese comando, jefe.</Command.Empty>
                  <Command.Group heading="Operación">
                    {actions.map((action) => {
                      const Icon = ICONS[action.icon];
                      return (
                        <Command.Item key={action.label} value={`${action.label} ${action.hint}`} onSelect={() => runAction(action)}>
                          <span className="prisma-command-item-icon"><Icon size={16} /></span>
                          <span className="prisma-command-item-copy">
                            <strong>{action.label}</strong>
                            <small>{action.hint}</small>
                          </span>
                        </Command.Item>
                      );
                    })}
                  </Command.Group>
                </Command.List>
              </Command>
            </motion.div>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </>
  );
}
