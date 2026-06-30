import { createTheme, style } from "@vanilla-extract/css";

export const [premiumThemeClass, premiumVars] = createTheme({
  color: {
    ink: "#142039",
    inkStrong: "#071226",
    muted: "#66748c",
    blue: "#246bff",
    cyan: "#49d4ff",
    violet: "#a78bfa",
    line: "rgba(92, 115, 150, 0.16)",
    surface: "rgba(255, 255, 255, 0.74)"
  },
  radius: {
    xl: "34px",
    lg: "26px",
    md: "18px",
    pill: "999px"
  },
  shadow: {
    float: "0 18px 42px rgba(37, 57, 91, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.82)"
  }
});

export const premiumSurface = style({
  border: `1px solid ${premiumVars.color.line}`,
  borderRadius: premiumVars.radius.lg,
  background: premiumVars.color.surface,
  boxShadow: premiumVars.shadow.float,
  color: premiumVars.color.ink
});
