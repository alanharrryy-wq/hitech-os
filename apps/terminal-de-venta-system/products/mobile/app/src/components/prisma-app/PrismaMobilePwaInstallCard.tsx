"use client";

import { useCallback, useEffect, useState } from "react";
import type { PrismaMobilePwaInstallStatus } from "@/lib/prisma-app/prisma-mobile-pwa-contract";
import { prismaMobileErrorMessage } from "@/lib/prisma-app/prisma-mobile-error";
import {
  copyText,
  currentAppUrl,
  currentInstallUrl,
  isAndroidDevice,
  isAndroidChrome,
  isChromiumInstallCapable,
  isIOSSafari,
  isIOSDevice,
  isSecurePwaContext,
  isStandaloneDisplay,
  isWhatsAppWebView
} from "@/lib/prisma-app/prisma-mobile-pwa-client";
import styles from "./prisma-mobile-pwa.module.css";

type BeforeInstallPromptEvent = Event & {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed"; platform: string }>;
};

type PlatformChoice = "android" | "ios" | null;

function platformHint(status: PrismaMobilePwaInstallStatus, choice: PlatformChoice) {
  if (status === "installed") return "PRISMA ya está instalada. Abriendo tablero...";
  if (choice === "android") return "Android listo para instalar PRISMA.";
  if (choice === "ios") return "iPhone listo: usa Safari y Agregar a pantalla de inicio.";
  if (status === "unsupported") return "Abre PRISMA desde un link seguro HTTPS para instalar.";
  return "Elige tu dispositivo para instalar supervisión móvil premium opcional. Tablet Solo vende sola.";
}

function androidGuideSteps(androidChrome: boolean, whatsapp: boolean) {
  if (androidChrome) {
    return [
      "Si aparece el cuadro de Chrome, toca Instalar.",
      "Si no aparece, abre el menu de Chrome y toca Instalar app.",
      "Cuando termine, abre PRISMA desde el icono en tu pantalla principal."
    ];
  }

  if (whatsapp) {
    return [
      "WhatsApp no instala PWAs directo.",
      "Abre el menu de WhatsApp y toca Abrir en navegador o Abrir en Chrome.",
      "Ya en Chrome, toca Android de nuevo o usa el menu de Chrome > Instalar app."
    ];
  }

  return [
    "Abre este enlace en Chrome Android.",
    "Cuando Chrome muestre el cuadro, toca Instalar.",
    "Si no aparece el cuadro, usa el menu de Chrome > Instalar app."
  ];
}

function iosGuideSteps(iosSafari: boolean, whatsapp: boolean) {
  if (iosSafari) {
    return [
      "Toca Compartir en la barra de Safari.",
      "Elige Agregar a pantalla de inicio.",
      "Confirma Agregar y abre PRISMA desde el icono nuevo."
    ];
  }

  if (whatsapp) {
    return [
      "WhatsApp no puede instalar PWAs en iPhone.",
      "Copia el enlace o usa Compartir para abrirlo en Safari.",
      "En Safari: Compartir > Agregar a pantalla de inicio."
    ];
  }

  return [
    "Abre este enlace en Safari en tu iPhone.",
    "Toca Compartir.",
    "Elige Agregar a pantalla de inicio."
  ];
}

export function PrismaMobilePwaInstallCard({ compact = false }: { compact?: boolean }) {
  const [promptEvent, setPromptEvent] = useState<BeforeInstallPromptEvent | null>(null);
  const [status, setStatus] = useState<PrismaMobilePwaInstallStatus>("checking");
  const [choice, setChoice] = useState<PlatformChoice>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [installUrl, setInstallUrl] = useState("/prisma-app/install?from=whatsapp");
  const [appUrl, setAppUrl] = useState("/prisma-app");
  const [androidDevice, setAndroidDevice] = useState(false);
  const [androidChrome, setAndroidChrome] = useState(false);
  const [iosDevice, setIosDevice] = useState(false);
  const [iosSafari, setIosSafari] = useState(false);
  const [whatsapp, setWhatsapp] = useState(false);

  useEffect(() => {
    setInstallUrl(currentInstallUrl());
    setAppUrl(currentAppUrl());
    setAndroidDevice(isAndroidDevice());
    setAndroidChrome(isAndroidChrome());
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
      setMessage("Listo. PRISMA quedó instalada para supervisar. Mobile no es requisito para vender.");
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
      setMessage("HTTPS ayuda a instalar la PWA, pero Cloudflare y soporte remoto son opcionales. Tablet Solo vende sola.");
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

    if (androidChrome) {
      setStatus("browser-menu");
      setMessage("Chrome todavia no entrego el instalador automatico. Usa el menu de Chrome y toca Instalar app.");
      return;
    }

    if (androidDevice || whatsapp) {
      setStatus("browser-menu");
      setMessage("Para instalar una PWA en Android, abre este enlace en Chrome. Evita el salto automatico que mandaba a una pagina rara.");
      return;
    }

    setMessage("Abre este link en Chrome Android para completar la instalación.");
  }, [androidChrome, androidDevice, promptEvent, whatsapp]);

  const installIos = useCallback(() => {
    setChoice("ios");
    setMessage(null);

    if (isStandaloneDisplay()) {
      setStatus("installed");
      window.location.assign("/prisma-app");
      return;
    }

    if (iosSafari) {
      setMessage("En Safari toca Compartir y luego Agregar a pantalla de inicio. iOS no deja automatizar ese último toque.");
      return;
    }

    if (iosDevice || whatsapp) {
      setMessage("iPhone solo instala PWAs desde Safari. Copia el enlace, abre Safari y usa Compartir > Agregar a pantalla de inicio.");
      return;
    }

    setMessage("Abre este link en un iPhone con Safari para instalar PRISMA.");
  }, [installUrl, iosDevice, iosSafari, whatsapp]);

  const copyInstallUrl = useCallback(async () => {
    const copied = await copyText(installUrl);
    setMessage(copied ? "Link copiado. Pégalo en Safari o Chrome para instalar PRISMA." : "No se pudo copiar el link. Mantén presionado y copia la dirección desde el navegador.");
  }, [installUrl]);

  return (
    <section
      className={compact ? styles.compactCard : styles.installCard}
      aria-label="Selector de instalación PRISMA App"
      data-prisma-pwa-status={status}
      data-prisma-zone="mobile-pwa-install"
    >
      <p className={styles.selectorTopline} aria-live="polite">
        <span>{platformHint(status, choice)}</span>
        <i aria-hidden="true" />
      </p>

      <div className={styles.platformChooserMinimal} aria-label="Elige Android o iPhone para instalar PRISMA App desde WhatsApp">
        <button type="button" className={styles.platformOrbCard} data-platform="android" data-selected={choice === "android"} onClick={() => void installAndroid()}>
          <span className={styles.orbIcon} aria-hidden="true">
            <span className={styles.androidGlyph}>●</span>
          </span>
          <span className={styles.platformText}>
            <span className={styles.orbLabel}>ANDROID</span>
            <strong>Instalar</strong>
          </span>
          <span className={styles.platformArrow} aria-hidden="true">→</span>
        </button>

        <button type="button" className={styles.platformOrbCard} data-platform="ios" data-selected={choice === "ios"} onClick={installIos}>
          <span className={styles.orbIcon} aria-hidden="true">
            <span className={styles.appleGlyph}>●</span>
          </span>
          <span className={styles.platformText}>
            <span className={styles.orbLabel}>IPHONE</span>
            <strong>Instalar</strong>
          </span>
          <span className={styles.platformArrow} aria-hidden="true">→</span>
        </button>
      </div>

      <p className={styles.installContextNote}>
        <span className={styles.whatsappGlyph} aria-hidden="true">☎</span>
        Ves ambas opciones porque abriste un enlace de PRISMA desde WhatsApp.
      </p>

      {message ? <p className={styles.minimalMessage}>{message}</p> : null}

      {choice ? (
        <div className={styles.installGuide} data-platform-guide={choice}>
          <strong>{choice === "android" ? "Instalacion Android PWA" : "Instalacion iPhone PWA"}</strong>
          <ol className={styles.guideSteps}>
            {(choice === "android" ? androidGuideSteps(androidChrome, whatsapp) : iosGuideSteps(iosSafari, whatsapp)).map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ol>
        </div>
      ) : null}

      <div className={styles.secondaryInstallActions} aria-label="Acciones alternativas de instalación">
        <button type="button" className={styles.copyLinkButton} onClick={() => void copyInstallUrl()}>
          Copiar enlace
        </button>
      </div>

      <a className={styles.hiddenDashboardLink} href={appUrl} aria-label="Abrir PRISMA App si ya está instalada o disponible">
        <span aria-hidden="true">↪</span>
        <strong>Abrir PRISMA</strong>
        <small>Si ya la tienes instalada</small>
      </a>
    </section>
  );
}
