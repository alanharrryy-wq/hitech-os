import type { PrismaIconName } from "./prisma-dark-pos-data";

type PrismaIconProps = {
  name: PrismaIconName;
  className?: string;
  size?: number;
  strokeWidth?: number;
};

export function PrismaIcon({ name, className, size = 20, strokeWidth = 1.9 }: PrismaIconProps) {
  return (
    <svg
      aria-hidden="true"
      className={className}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      stroke="currentColor"
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {getIconPath(name)}
    </svg>
  );
}

function getIconPath(name: PrismaIconName) {
  switch (name) {
    case "arrow-left":
      return <path d="M15 18l-6-6 6-6M20 12H9" />;
    case "arrow-right":
      return <path d="M9 18l6-6-6-6M4 12h11" />;
    case "bell":
      return (
        <>
          <path d="M18 8a6 6 0 1 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9" />
          <path d="M10 21h4" />
        </>
      );
    case "box":
      return (
        <>
          <path d="M21 8l-9-5-9 5 9 5 9-5Z" />
          <path d="M3 8v8l9 5 9-5V8" />
          <path d="M12 13v8" />
        </>
      );
    case "briefcase":
      return (
        <>
          <path d="M10 6V5a2 2 0 0 1 2-2h0a2 2 0 0 1 2 2v1" />
          <rect x="3" y="6" width="18" height="14" rx="3" />
          <path d="M3 12h18" />
        </>
      );
    case "broom":
      return (
        <>
          <path d="M19 3l-8 8" />
          <path d="M15 7l2 2" />
          <path d="M5 19c2.5 1.5 6.5 1.5 9 0l-3-8-6 6v2Z" />
        </>
      );
    case "cart":
      return (
        <>
          <circle cx="9" cy="20" r="1.5" />
          <circle cx="18" cy="20" r="1.5" />
          <path d="M3 4h2l2.1 10.2a2 2 0 0 0 2 1.6h8.7a2 2 0 0 0 2-1.6L21 8H6" />
        </>
      );
    case "chart":
      return (
        <>
          <path d="M4 19V5" />
          <path d="M4 19h16" />
          <path d="M8 15l3-4 3 2 5-7" />
        </>
      );
    case "chevron-down":
      return <path d="M6 9l6 6 6-6" />;
    case "credit-card":
      return (
        <>
          <rect x="3" y="5" width="18" height="14" rx="3" />
          <path d="M3 10h18" />
          <path d="M7 15h4" />
        </>
      );
    case "dashboard":
      return (
        <>
          <rect x="3" y="3" width="7" height="7" rx="2" />
          <rect x="14" y="3" width="7" height="7" rx="2" />
          <rect x="3" y="14" width="7" height="7" rx="2" />
          <rect x="14" y="14" width="7" height="7" rx="2" />
        </>
      );
    case "grid":
      return (
        <>
          <path d="M4 4h7v7H4z" />
          <path d="M13 4h7v7h-7z" />
          <path d="M4 13h7v7H4z" />
          <path d="M13 13h7v7h-7z" />
        </>
      );
    case "milk":
      return (
        <>
          <path d="M8 3h8l-1 5H9L8 3Z" />
          <path d="M9 8h6l2 3v8a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2v-8l2-3Z" />
          <path d="M8 13h8" />
        </>
      );
    case "minus":
      return <path d="M5 12h14" />;
    case "more":
      return (
        <>
          <circle cx="5" cy="12" r="1" fill="currentColor" stroke="none" />
          <circle cx="12" cy="12" r="1" fill="currentColor" stroke="none" />
          <circle cx="19" cy="12" r="1" fill="currentColor" stroke="none" />
        </>
      );
    case "package":
      return (
        <>
          <path d="M12 2l8 4v12l-8 4-8-4V6l8-4Z" />
          <path d="M4 6l8 4 8-4" />
          <path d="M12 10v12" />
        </>
      );
    case "plus":
      return <path d="M12 5v14M5 12h14" />;
    case "receipt":
      return (
        <>
          <path d="M6 3h12v18l-3-2-3 2-3-2-3 2V3Z" />
          <path d="M9 8h6M9 12h6M9 16h4" />
        </>
      );
    case "save":
      return (
        <>
          <path d="M5 3h12l2 2v16H5V3Z" />
          <path d="M8 3v6h8V3" />
          <path d="M8 21v-7h8v7" />
        </>
      );
    case "scan":
      return (
        <>
          <path d="M7 3H5a2 2 0 0 0-2 2v2M17 3h2a2 2 0 0 1 2 2v2M7 21H5a2 2 0 0 1-2-2v-2M17 21h2a2 2 0 0 0 2-2v-2" />
          <path d="M7 12h10" />
        </>
      );
    case "search":
      return (
        <>
          <circle cx="11" cy="11" r="7" />
          <path d="M20 20l-3.5-3.5" />
        </>
      );
    case "settings":
      return (
        <>
          <circle cx="12" cy="12" r="3" />
          <path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1-2 3.4-.2-.1a1.7 1.7 0 0 0-1.8-.1 1.7 1.7 0 0 0-1 1.5V22h-4v-.3a1.7 1.7 0 0 0-1-1.5 1.7 1.7 0 0 0-1.8.1l-.2.1-2-3.4.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.3-1.2H4v-4h.4a1.7 1.7 0 0 0 1.3-1.2 1.7 1.7 0 0 0-.3-1.8l-.1-.1 2-3.4.2.1a1.7 1.7 0 0 0 1.8.1 1.7 1.7 0 0 0 1-1.5V2h4v.3a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.1l.2-.1 2 3.4-.1.1a1.7 1.7 0 0 0-.3 1.8 1.7 1.7 0 0 0 1.3 1.2h.4v4h-.4A1.7 1.7 0 0 0 19.4 15Z" />
        </>
      );
    case "sparkle":
      return (
        <>
          <path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3Z" />
          <path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8L19 15Z" />
        </>
      );
    case "star":
      return <path d="M12 3.8l2.5 5.1 5.6.8-4 3.9.9 5.5-5-2.7-5 2.7.9-5.5-4-3.9 5.6-.8L12 3.8Z" />;
    case "sun":
      return (
        <>
          <circle cx="12" cy="12" r="4" />
          <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
        </>
      );
    case "tag":
      return (
        <>
          <path d="M20 13l-7 7-9-9V4h7l9 9Z" />
          <circle cx="8.5" cy="8.5" r="1.3" />
        </>
      );
    case "terminal":
      return (
        <>
          <rect x="4" y="3" width="16" height="18" rx="3" />
          <path d="M8 8h8M8 12h8M9 17h6" />
        </>
      );
    case "trash":
      return (
        <>
          <path d="M4 7h16" />
          <path d="M10 11v6M14 11v6" />
          <path d="M6 7l1 14h10l1-14" />
          <path d="M9 7V4h6v3" />
        </>
      );
    case "truck":
      return (
        <>
          <path d="M3 6h11v10H3z" />
          <path d="M14 9h4l3 3v4h-7V9Z" />
          <circle cx="7" cy="18" r="2" />
          <circle cx="17" cy="18" r="2" />
        </>
      );
    case "user":
      return (
        <>
          <circle cx="12" cy="8" r="4" />
          <path d="M5 21a7 7 0 0 1 14 0" />
        </>
      );
    case "users":
      return (
        <>
          <path d="M16 21a5 5 0 0 0-10 0" />
          <circle cx="11" cy="8" r="4" />
          <path d="M21 21a4 4 0 0 0-4-4" />
          <path d="M17 4a3 3 0 0 1 0 6" />
        </>
      );
    case "wallet":
      return (
        <>
          <path d="M4 7h15a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a3 3 0 0 1-3-3V7a3 3 0 0 1 3-3h12" />
          <path d="M16 13h5" />
        </>
      );
    case "x":
      return <path d="M6 6l12 12M18 6L6 18" />;
  }
}
