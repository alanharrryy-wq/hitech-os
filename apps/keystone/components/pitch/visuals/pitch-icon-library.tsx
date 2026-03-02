import { cn } from "@hitech/ui-kit";

export interface PitchIconProps {
  readonly className?: string;
  readonly strokeWidth?: number;
}

function BaseIcon({ className, strokeWidth = 1.8, children }: PitchIconProps & { readonly children: React.ReactNode }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={cn("h-5 w-5", className)}
      aria-hidden
    >
      {children}
    </svg>
  );
}

export function PitchIconEngine(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M4 4 L20 20" />
      <circle cx="8" cy="8" r="2" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconBolt(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M5 6 L19 17" />
      <circle cx="9" cy="10" r="3" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconChip(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M6 8 L18 19" />
      <circle cx="10" cy="12" r="4" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconShield(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M7 4 L17 16" />
      <circle cx="11" cy="14" r="5" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconTrace(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M8 6 L16 18" />
      <circle cx="12" cy="8" r="2" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconHistory(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M9 8 L20 20" />
      <circle cx="13" cy="10" r="3" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconControl(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M4 4 L19 17" />
      <circle cx="14" cy="12" r="4" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconNetwork(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M5 6 L18 19" />
      <circle cx="15" cy="14" r="5" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconGauge(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M6 8 L17 16" />
      <circle cx="8" cy="8" r="2" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconFlow(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M7 4 L16 18" />
      <circle cx="9" cy="10" r="3" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconCycle(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M8 6 L20 20" />
      <circle cx="10" cy="12" r="4" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconFactory(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M9 8 L19 17" />
      <circle cx="11" cy="14" r="5" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconModule(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M4 4 L18 19" />
      <circle cx="12" cy="8" r="2" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconSignal(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M5 6 L17 16" />
      <circle cx="13" cy="10" r="3" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconTimeline(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M6 8 L16 18" />
      <circle cx="14" cy="12" r="4" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconRisk(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M7 4 L20 20" />
      <circle cx="15" cy="14" r="5" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconValue(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M8 6 L19 17" />
      <circle cx="8" cy="8" r="2" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconCapital(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M9 8 L18 19" />
      <circle cx="9" cy="10" r="3" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconScale(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M4 4 L17 16" />
      <circle cx="10" cy="12" r="4" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconCheck(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M5 6 L16 18" />
      <circle cx="11" cy="14" r="5" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconAlert(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M6 8 L20 20" />
      <circle cx="12" cy="8" r="2" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconPackage(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M7 4 L19 17" />
      <circle cx="13" cy="10" r="3" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconTruck(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M8 6 L18 19" />
      <circle cx="14" cy="12" r="4" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconBeaker(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M9 8 L17 16" />
      <circle cx="15" cy="14" r="5" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconPill(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M4 4 L16 18" />
      <circle cx="8" cy="8" r="2" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconLab(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M5 6 L20 20" />
      <circle cx="9" cy="10" r="3" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconVault(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M6 8 L19 17" />
      <circle cx="10" cy="12" r="4" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconBarcode(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M7 4 L18 19" />
      <circle cx="11" cy="14" r="5" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconScan(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M8 6 L17 16" />
      <circle cx="12" cy="8" r="2" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconCloud(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M9 8 L16 18" />
      <circle cx="13" cy="10" r="3" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconLock(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M4 4 L20 20" />
      <circle cx="14" cy="12" r="4" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconKey(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M5 6 L19 17" />
      <circle cx="15" cy="14" r="5" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconRole(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M6 8 L18 19" />
      <circle cx="8" cy="8" r="2" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconUser(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M7 4 L17 16" />
      <circle cx="9" cy="10" r="3" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconChart(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M8 6 L16 18" />
      <circle cx="10" cy="12" r="4" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconSpark(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M9 8 L20 20" />
      <circle cx="11" cy="14" r="5" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconLine(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M4 4 L19 17" />
      <circle cx="12" cy="8" r="2" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconArea(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M5 6 L18 19" />
      <circle cx="13" cy="10" r="3" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconBar(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M6 8 L17 16" />
      <circle cx="14" cy="12" r="4" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconRadar(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M7 4 L16 18" />
      <circle cx="15" cy="14" r="5" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconOrbit(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M8 6 L20 20" />
      <circle cx="8" cy="8" r="2" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconSatellite(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M9 8 L19 17" />
      <circle cx="9" cy="10" r="3" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconPlatform(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M4 4 L18 19" />
      <circle cx="10" cy="12" r="4" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconHub(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M5 6 L17 16" />
      <circle cx="11" cy="14" r="5" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconLink(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M6 8 L16 18" />
      <circle cx="12" cy="8" r="2" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconBridge(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M7 4 L20 20" />
      <circle cx="13" cy="10" r="3" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconNode(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M8 6 L19 17" />
      <circle cx="14" cy="12" r="4" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconCircuit(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M9 8 L18 19" />
      <circle cx="15" cy="14" r="5" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconMemory(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M4 4 L17 16" />
      <circle cx="8" cy="8" r="2" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconCpu(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M5 6 L16 18" />
      <circle cx="9" cy="10" r="3" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconPower(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M6 8 L20 20" />
      <circle cx="10" cy="12" r="4" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconWater(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M7 4 L19 17" />
      <circle cx="11" cy="14" r="5" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconThermal(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M8 6 L18 19" />
      <circle cx="12" cy="8" r="2" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconPressure(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M9 8 L17 16" />
      <circle cx="13" cy="10" r="3" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconQuality(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M4 4 L16 18" />
      <circle cx="14" cy="12" r="4" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconCertificate(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M5 6 L20 20" />
      <circle cx="15" cy="14" r="5" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconDocument(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M6 8 L19 17" />
      <circle cx="8" cy="8" r="2" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconRoute(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M7 4 L18 19" />
      <circle cx="9" cy="10" r="3" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconArrow(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M8 6 L17 16" />
      <circle cx="10" cy="12" r="4" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconCompass(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M9 8 L16 18" />
      <circle cx="11" cy="14" r="5" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconAnchor(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M4 4 L20 20" />
      <circle cx="12" cy="8" r="2" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconTarget(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M5 6 L19 17" />
      <circle cx="13" cy="10" r="3" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconLayer(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M6 8 L18 19" />
      <circle cx="14" cy="12" r="4" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconStack(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M7 4 L17 16" />
      <circle cx="15" cy="14" r="5" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconPanel(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M8 6 L16 18" />
      <circle cx="8" cy="8" r="2" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconCard(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M9 8 L20 20" />
      <circle cx="9" cy="10" r="3" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconGlass(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M4 4 L19 17" />
      <circle cx="10" cy="12" r="4" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconHalo(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M5 6 L18 19" />
      <circle cx="11" cy="14" r="5" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconCrown(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M6 8 L17 16" />
      <circle cx="12" cy="8" r="2" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconGem(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M7 4 L16 18" />
      <circle cx="13" cy="10" r="3" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconClock(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M8 6 L20 20" />
      <circle cx="14" cy="12" r="4" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconTimer(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M9 8 L19 17" />
      <circle cx="15" cy="14" r="5" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconCalendar(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M4 4 L18 19" />
      <circle cx="8" cy="8" r="2" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconMap(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M5 6 L17 16" />
      <circle cx="9" cy="10" r="3" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconFlag(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M6 8 L16 18" />
      <circle cx="10" cy="12" r="4" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconGlobe(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M7 4 L20 20" />
      <circle cx="11" cy="14" r="5" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconPhone(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M8 6 L19 17" />
      <circle cx="12" cy="8" r="2" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconMessage(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M9 8 L18 19" />
      <circle cx="13" cy="10" r="3" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconBell(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M4 4 L17 16" />
      <circle cx="14" cy="12" r="4" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconEye(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M5 6 L16 18" />
      <circle cx="15" cy="14" r="5" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconSearch(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M6 8 L20 20" />
      <circle cx="8" cy="8" r="2" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconFilter(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M7 4 L19 17" />
      <circle cx="9" cy="10" r="3" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconSettings(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M8 6 L18 19" />
      <circle cx="10" cy="12" r="4" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconPlay(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M9 8 L17 16" />
      <circle cx="11" cy="14" r="5" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconPause(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M4 4 L16 18" />
      <circle cx="12" cy="8" r="2" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconStop(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M5 6 L20 20" />
      <circle cx="13" cy="10" r="3" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconForward(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M6 8 L19 17" />
      <circle cx="14" cy="12" r="4" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconBackward(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M7 4 L18 19" />
      <circle cx="15" cy="14" r="5" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconRefresh(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M8 6 L17 16" />
      <circle cx="8" cy="8" r="2" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconUpload(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M9 8 L16 18" />
      <circle cx="9" cy="10" r="3" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconDownload(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M4 4 L20 20" />
      <circle cx="10" cy="12" r="4" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconExpand(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M5 6 L19 17" />
      <circle cx="11" cy="14" r="5" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconCollapse(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M6 8 L18 19" />
      <circle cx="12" cy="8" r="2" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconPlus(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M7 4 L17 16" />
      <circle cx="13" cy="10" r="3" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconMinus(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M8 6 L16 18" />
      <circle cx="14" cy="12" r="4" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconEqual(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M9 8 L20 20" />
      <circle cx="15" cy="14" r="5" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconDivide(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M4 4 L19 17" />
      <circle cx="8" cy="8" r="2" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconMultiply(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M5 6 L18 19" />
      <circle cx="9" cy="10" r="3" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconPercent(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M6 8 L17 16" />
      <circle cx="10" cy="12" r="4" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconDollar(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M7 4 L16 18" />
      <circle cx="11" cy="14" r="5" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconTrendUp(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M8 6 L20 20" />
      <circle cx="12" cy="8" r="2" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconTrendDown(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M9 8 L19 17" />
      <circle cx="13" cy="10" r="3" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconBalance(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M4 4 L18 19" />
      <circle cx="14" cy="12" r="4" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconCube(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M5 6 L17 16" />
      <circle cx="15" cy="14" r="5" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconHex(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M6 8 L16 18" />
      <circle cx="8" cy="8" r="2" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconPrism(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M7 4 L20 20" />
      <circle cx="9" cy="10" r="3" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconWave(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M8 6 L19 17" />
      <circle cx="10" cy="12" r="4" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconPulse(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M9 8 L18 19" />
      <circle cx="11" cy="14" r="5" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconAtom(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M4 4 L17 16" />
      <circle cx="12" cy="8" r="2" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconStar(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M5 6 L16 18" />
      <circle cx="13" cy="10" r="3" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconMoon(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M6 8 L20 20" />
      <circle cx="14" cy="12" r="4" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconSun(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M7 4 L19 17" />
      <circle cx="15" cy="14" r="5" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconLeaf(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M8 6 L18 19" />
      <circle cx="8" cy="8" r="2" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconFire(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M9 8 L17 16" />
      <circle cx="9" cy="10" r="3" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconSnow(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M4 4 L16 18" />
      <circle cx="10" cy="12" r="4" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconRain(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M5 6 L20 20" />
      <circle cx="11" cy="14" r="5" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconWind(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M6 8 L19 17" />
      <circle cx="12" cy="8" r="2" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconSeed(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M7 4 L18 19" />
      <circle cx="13" cy="10" r="3" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconTree(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M8 6 L17 16" />
      <circle cx="14" cy="12" r="4" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export function PitchIconMountain(props: PitchIconProps) {
  return (
    <BaseIcon {...props}>
      <path d="M9 8 L16 18" />
      <circle cx="15" cy="14" r="5" />
      <path d="M4 12 H20" />
    </BaseIcon>
  );
}

export const PITCH_ICON_LIBRARY = {
  Engine: PitchIconEngine,
  Bolt: PitchIconBolt,
  Chip: PitchIconChip,
  Shield: PitchIconShield,
  Trace: PitchIconTrace,
  History: PitchIconHistory,
  Control: PitchIconControl,
  Network: PitchIconNetwork,
  Gauge: PitchIconGauge,
  Flow: PitchIconFlow,
  Cycle: PitchIconCycle,
  Factory: PitchIconFactory,
  Module: PitchIconModule,
  Signal: PitchIconSignal,
  Timeline: PitchIconTimeline,
  Risk: PitchIconRisk,
  Value: PitchIconValue,
  Capital: PitchIconCapital,
  Scale: PitchIconScale,
  Check: PitchIconCheck,
  Alert: PitchIconAlert,
  Package: PitchIconPackage,
  Truck: PitchIconTruck,
  Beaker: PitchIconBeaker,
  Pill: PitchIconPill,
  Lab: PitchIconLab,
  Vault: PitchIconVault,
  Barcode: PitchIconBarcode,
  Scan: PitchIconScan,
  Cloud: PitchIconCloud,
  Lock: PitchIconLock,
  Key: PitchIconKey,
  Role: PitchIconRole,
  User: PitchIconUser,
  Chart: PitchIconChart,
  Spark: PitchIconSpark,
  Line: PitchIconLine,
  Area: PitchIconArea,
  Bar: PitchIconBar,
  Radar: PitchIconRadar,
  Orbit: PitchIconOrbit,
  Satellite: PitchIconSatellite,
  Platform: PitchIconPlatform,
  Hub: PitchIconHub,
  Link: PitchIconLink,
  Bridge: PitchIconBridge,
  Node: PitchIconNode,
  Circuit: PitchIconCircuit,
  Memory: PitchIconMemory,
  Cpu: PitchIconCpu,
  Power: PitchIconPower,
  Water: PitchIconWater,
  Thermal: PitchIconThermal,
  Pressure: PitchIconPressure,
  Quality: PitchIconQuality,
  Certificate: PitchIconCertificate,
  Document: PitchIconDocument,
  Route: PitchIconRoute,
  Arrow: PitchIconArrow,
  Compass: PitchIconCompass,
  Anchor: PitchIconAnchor,
  Target: PitchIconTarget,
  Layer: PitchIconLayer,
  Stack: PitchIconStack,
  Panel: PitchIconPanel,
  Card: PitchIconCard,
  Glass: PitchIconGlass,
  Halo: PitchIconHalo,
  Crown: PitchIconCrown,
  Gem: PitchIconGem,
  Clock: PitchIconClock,
  Timer: PitchIconTimer,
  Calendar: PitchIconCalendar,
  Map: PitchIconMap,
  Flag: PitchIconFlag,
  Globe: PitchIconGlobe,
  Phone: PitchIconPhone,
  Message: PitchIconMessage,
  Bell: PitchIconBell,
  Eye: PitchIconEye,
  Search: PitchIconSearch,
  Filter: PitchIconFilter,
  Settings: PitchIconSettings,
  Play: PitchIconPlay,
  Pause: PitchIconPause,
  Stop: PitchIconStop,
  Forward: PitchIconForward,
  Backward: PitchIconBackward,
  Refresh: PitchIconRefresh,
  Upload: PitchIconUpload,
  Download: PitchIconDownload,
  Expand: PitchIconExpand,
  Collapse: PitchIconCollapse,
  Plus: PitchIconPlus,
  Minus: PitchIconMinus,
  Equal: PitchIconEqual,
  Divide: PitchIconDivide,
  Multiply: PitchIconMultiply,
  Percent: PitchIconPercent,
  Dollar: PitchIconDollar,
  TrendUp: PitchIconTrendUp,
  TrendDown: PitchIconTrendDown,
  Balance: PitchIconBalance,
  Cube: PitchIconCube,
  Hex: PitchIconHex,
  Prism: PitchIconPrism,
  Wave: PitchIconWave,
  Pulse: PitchIconPulse,
  Atom: PitchIconAtom,
  Star: PitchIconStar,
  Moon: PitchIconMoon,
  Sun: PitchIconSun,
  Leaf: PitchIconLeaf,
  Fire: PitchIconFire,
  Snow: PitchIconSnow,
  Rain: PitchIconRain,
  Wind: PitchIconWind,
  Seed: PitchIconSeed,
  Tree: PitchIconTree,
  Mountain: PitchIconMountain,
} as const;

export type PitchIconName = keyof typeof PITCH_ICON_LIBRARY;

export function PitchIconByName({ name, ...props }: PitchIconProps & { readonly name: PitchIconName }) {
  const Component = PITCH_ICON_LIBRARY[name];
  return <Component {...props} />;
}
