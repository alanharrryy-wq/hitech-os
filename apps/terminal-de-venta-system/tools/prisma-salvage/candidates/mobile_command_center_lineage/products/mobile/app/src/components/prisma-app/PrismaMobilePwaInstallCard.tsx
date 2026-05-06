"use client";

import { useCallback, useEffect, useState } from "react";
import type { PrismaMobilePwaInstallStatus } from "@/lib/prisma-app/prisma-mobile-pwa-contract";
import { prismaMobileErrorMessage } from "@/lib/prisma-app/prisma-mobile-error";
import {
  currentAppUrl,
  currentInstallUrl,
  isAndroidDevice,
  isChromiumInstallCapable,
  isIOSSafari,
  isIOSDevice,
  isSecurePwaContext,
  isStandaloneDisplay,
  isWhatsAppWebView,
  tryOpenAndroidChrome
} from "@/lib/prisma-app/prisma-mobile-pwa-client";
import styles from "./prisma-mobile-pwa.module.css";

type BeforeInstallPromptEvent = Event & {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed"; platform: string }>;
};

type PlatformChoice = "android" | "ios" | null;

function platformHint(status: PrismaMobilePwaInstallStatus, choice: PlatformChoice) {
  if (status === "installed") return "PRISMA ya está instalada. Abriendo tablero...";
  if (choice === "android") return "Abriendo instalador de Android...";
  if (choice === "ios") return "Abriendo flujo de iPhone...";
  return "Selecciona una plataforma";
}

export function PrismaMobilePwaInstallCard({ compact = false }: { compact?: boolean }) {
  const [promptEvent, setPromptEvent] = useState<BeforeInstallPromptEvent | null>(null);
  const [status, setStatus] = useState<PrismaMobilePwaInstallStatus>("checking");
  const [choice, setChoice] = useState<PlatformChoice>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [installUrl, setInstallUrl] = useState("/prisma-app/install?from=whatsapp");
  const [appUrl, setAppUrl] = useState("/prisma-app");
  const [androidDevice, setAndroidDevice] = useState(false);
  const [iosDevice, setIosDevice] = useState(false);
  const [iosSafari, setIosSafari] = useState(false);
  const [whatsapp, setWhatsapp] = useState(false);

  useEffect(() => {
    setInstallUrl(currentInstallUrl());
    setAppUrl(currentAppUrl());
    setAndroidDevice(isAndroidDevice());
    setIosDevice(isIOSDevice());
    setIosSafari(isIOSSafari());
    setWhatsapp(isWhatsAppWebView());

    if (isStandaloneDisplay()) setStatus("installed");
    else if (!isSecurePwaContext()) setStatus("unsupported");
    else setStatus("browser-menu");

    const onBeforeInstall = (event: Event) => {
      event.preventDefault();
      setPromptEvent(event as BeforeInstallPromptEvent);
      setStatus("installable");
    };
    const onInstalled = () => {
      setPromptEvent(null);
      setStatus("installed");
      setMessage("Listo. PRISMA quedó instalada en este dispositivo.");
      window.setTimeout(() => window.location.assign("/prisma-app"), 650);
    };

    window.addEventListener("beforeinstallprompt", onBeforeInstall);
    window.addEventListener("appinstalled", onInstalled);
    return () => {
      window.removeEventListener("beforeinstallprompt", onBeforeInstall);
      window.removeEventListener("appinstalled", onInstalled);
    };
  }, []);

  const installAndroid = useCallback(async () => {
    setChoice("android");
    setMessage(null);

    if (isStandaloneDisplay()) {
      setStatus("installed");
      window.location.assign("/prisma-app");
      return;
    }

    if (!isSecurePwaContext()) {
      setStatus("unsupported");
      setMessage("Necesita abrirse desde HTTPS para instalarse como app.");
      return;
    }

    if (promptEvent && isChromiumInstallCapable()) {
      try {
        await promptEvent.prompt();
        const result = await promptEvent.userChoice;
        setPromptEvent(null);
        if (result.outcome === "accepted") {
          setStatus("installed");
          setMessage("Instalación aceptada. Busca el ícono de PRISMA en tu pantalla principal.");
          window.setTimeout(() => window.location.assign("/prisma-app"), 700);
        } else {
          setStatus("browser-menu");
          setMessage("Instalación cancelada. Toca Android otra vez cuando quieras intentarlo de nuevo.");
        }
      } catch (error) {
        setPromptEvent(null);
        setStatus("browser-menu");
        setMessage(prismaMobileErrorMessage(error, "No se pudo abrir el instalador automático. Usa el menú del navegador para instalar PRISMA."));
      }
      return;
    }

    if (androidDevice || whatsapp) {
      setMessage("Abriendo Chrome para instalar PRISMA...");
      tryOpenAndroidChrome(installUrl);
      return;
    }

    setMessage("Abre este link en Chrome Android para completar la instalación.");
  }, [androidDevice, installUrl, promptEvent, whatsapp]);

  const installIos = useCallback(() => {
    setChoice("ios");
    setMessage(null);

    if (isStandaloneDisplay()) {
      setStatus("installed");
      window.location.assign("/prisma-app");
      return;
    }

    if (iosSafari) {
      setMessage("En Safari toca compartir y Agregar a pantalla de inicio. iOS no deja automatizar ese último toque.");
      return;
    }

    if (iosDevice || whatsapp) {
      setMessage("Abre este link en Safari para agregar PRISMA a inicio.");
      window.location.assign(installUrl);
      return;
    }

    setMessage("Abre este link en un iPhone con Safari para instalar PRISMA.");
  }, [installUrl, iosDevice, iosSafari, whatsapp]);

  return (
    <section
      className={compact ? styles.compactCard : styles.installCard}
      aria-label="Selector de instalación PRISMA App"
      data-prisma-pwa-status={status}
    >
      <div className={styles.selectorTopline}>
        <span>{platformHint(status, choice)}</span>
        <i aria-hidden="true" />
      </div>

      <div className={styles.platformChooserMinimal} aria-label="Elige Android o iPhone para instalar PRISMA App">
        <button type="button" className={styles.platformOrbCard} data-platform="android" data-selected={choice === "android"} onClick={() => void installAndroid()}>
          <span className={styles.orbIcon}>🤖</span>
          <span className={styles.orbLabel}>Android</span>
          <strong>Instalar</strong>
        </button>

        <button type="button" className={styles.platformOrbCard} data-platform="ios" data-selected={choice === "ios"} onClick={installIos}>
          <span className={styles.orbIcon}>🍏</span>
          <span className={styles.orbLabel}>iPhone</span>
          <strong>Instalar</strong>
        </button>
      </div>

      {message ? <p className={styles.minimalMessage}>{message}</p> : null}

      <a className={styles.hiddenDashboardLink} href={appUrl} aria-label="Abrir PRISMA App si ya está instalada o disponible">
        Abrir PRISMA
      </a>
    </section>
  );
}
