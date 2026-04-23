import type { ThemeSpec, UiThemeId } from "@/lib/ui/theme-system/types";

function chartSeries(a: string, b: string, c: string, d: string): readonly [string, string, string, string] {
  return [a, b, c, d] as const;
}

type ThemeSections = Omit<ThemeSpec, "meta">;
type ThemeOverrides = {
  color?: Partial<ThemeSections["color"]>;
  material?: Partial<ThemeSections["material"]>;
  chrome?: Partial<ThemeSections["chrome"]>;
  motion?: Partial<ThemeSections["motion"]> & {
    backdropCadence?: Partial<ThemeSections["motion"]["backdropCadence"]>;
    reduced?: Partial<ThemeSections["motion"]["reduced"]>;
  };
  backdrop?: Partial<ThemeSections["backdrop"]>;
  widgets?: Partial<ThemeSections["widgets"]>;
  typography?: Partial<ThemeSections["typography"]>;
  dataViz?: Partial<ThemeSections["dataViz"]>;
};

function createTheme(meta: ThemeSpec["meta"], base: ThemeSections, overrides: ThemeOverrides = {}): ThemeSpec {
  return {
    meta,
    color: { ...base.color, ...overrides.color },
    material: { ...base.material, ...overrides.material },
    chrome: { ...base.chrome, ...overrides.chrome },
    motion: {
      ...base.motion,
      ...overrides.motion,
      backdropCadence: {
        ...base.motion.backdropCadence,
        ...overrides.motion?.backdropCadence
      },
      reduced: {
        ...base.motion.reduced,
        ...overrides.motion?.reduced
      }
    },
    backdrop: { ...base.backdrop, ...overrides.backdrop },
    widgets: { ...base.widgets, ...overrides.widgets },
    typography: { ...base.typography, ...overrides.typography },
    dataViz: {
      ...base.dataViz,
      ...overrides.dataViz,
      series: overrides.dataViz?.series ?? base.dataViz.series
    }
  };
}

const darkBase: ThemeSections = {
  color: {
    canvas: "6 10 20",
    surface: "12 18 34",
    panel: "17 25 45",
    elevated: "22 32 58",
    text: "206 222 245",
    heading: "236 246 255",
    muted: "142 162 192",
    subtle: "98 121 156",
    border: "70 98 140",
    borderStrong: "102 138 189",
    accent: "92 198 255",
    accentSoft: "152 141 255",
    accentContrast: "10 30 46",
    success: "94 209 171",
    warning: "237 193 113",
    danger: "244 130 181",
    selectionBg: "rgba(92, 198, 255, 0.34)",
    selectionText: "rgba(236, 246, 255, 1)",
    scrollbarThumb: "rgba(114, 153, 205, 0.56)"
  },
  material: {
    chromeBackground: "linear-gradient(142deg, rgba(16, 28, 54, 0.86), rgba(8, 13, 26, 0.72))",
    chromeBorder: "rgba(127, 183, 238, 0.26)",
    chromeShadow: "0 26px 58px rgba(1, 6, 20, 0.62), inset 0 1px 0 rgba(177, 226, 255, 0.16)",
    chromeBlur: "19px",
    surfacePrimary: "linear-gradient(152deg, rgba(13, 24, 47, 0.84), rgba(8, 14, 29, 0.74))",
    surfaceSecondary: "linear-gradient(160deg, rgba(18, 31, 58, 0.74), rgba(10, 18, 35, 0.66))",
    surfaceMuted: "rgba(15, 28, 52, 0.66)",
    surfaceElevated: "linear-gradient(152deg, rgba(20, 35, 65, 0.84), rgba(11, 19, 36, 0.76))",
    surfaceBorder: "rgba(105, 158, 215, 0.22)",
    surfaceEdge: "rgba(172, 225, 255, 0.15)",
    surfaceShadow: "0 20px 46px rgba(2, 8, 24, 0.48), inset 0 1px 0 rgba(168, 223, 255, 0.1)",
    inlineBackground: "rgba(20, 35, 65, 0.5)",
    inlineBorder: "rgba(110, 162, 219, 0.22)",
    overlayBackground: "linear-gradient(162deg, rgba(14, 27, 51, 0.95), rgba(7, 13, 24, 0.9))",
    overlayBorder: "rgba(122, 179, 238, 0.3)",
    overlayShadow: "0 36px 92px rgba(1, 4, 16, 0.7), inset 0 1px 0 rgba(170, 224, 255, 0.16)"
  },
  chrome: {
    shellHeight: "3.5rem",
    shellRadius: "28px",
    shellPaddingInline: "0.92rem",
    shellPaddingBlock: "0.58rem",
    navRadius: "14px",
    navGap: "0.3rem",
    navActiveBackground: "rgba(93, 200, 255, 0.16)",
    navActiveBorder: "rgba(157, 222, 255, 0.32)",
    navActiveShadow: "0 10px 22px rgba(71, 178, 238, 0.24), inset 0 1px 0 rgba(193, 235, 255, 0.18)",
    navIdleBackground: "rgba(17, 30, 56, 0.34)",
    navIdleHoverBackground: "rgba(24, 42, 76, 0.5)",
    clusterBackground: "rgba(18, 31, 56, 0.44)",
    clusterBorder: "rgba(109, 162, 219, 0.24)",
    clusterRadius: "14px",
    chipBackground: "rgba(20, 35, 66, 0.48)",
    chipBorder: "rgba(112, 166, 224, 0.2)",
    chipText: "rgba(211, 228, 248, 0.95)"
  },
  motion: {
    productiveDuration: "110ms",
    standardDuration: "180ms",
    expressiveDuration: "290ms",
    productiveEasing: "cubic-bezier(0.22, 0.74, 0.28, 1)",
    expressiveEasing: "cubic-bezier(0.24, 0.67, 0.28, 1)",
    hoverLift: "1px",
    backdropCadence: { drift3: "5.8s", drift5: "9.8s", drift10: "17.8s" },
    reduced: { ambient: "minimal", expressive: "fade" }
  },
  backdrop: {
    baseGradient:
      "radial-gradient(circle at 7% -10%, rgba(82, 167, 255, 0.36), transparent 44%), radial-gradient(circle at 90% 11%, rgba(143, 118, 255, 0.34), transparent 42%), radial-gradient(circle at 74% 54%, rgba(87, 137, 236, 0.24), transparent 48%), radial-gradient(circle at 48% 114%, rgba(66, 122, 215, 0.44), transparent 58%), linear-gradient(180deg, rgba(6, 10, 20, 1), rgba(4, 7, 14, 1))",
    mistGradient:
      "linear-gradient(112deg, rgba(88, 196, 255, 0.16), transparent 46%), linear-gradient(296deg, rgba(158, 128, 255, 0.14), transparent 52%), radial-gradient(circle at 34% 62%, rgba(122, 180, 255, 0.14), transparent 54%)",
    vignetteGradient: "linear-gradient(180deg, rgba(3, 6, 14, 0.1) 0%, rgba(3, 6, 14, 0.52) 100%)",
    particleNearColor: "rgba(128, 220, 255, 0.24)",
    particleFarColor: "rgba(137, 152, 255, 0.14)",
    sparkleColor: "rgba(193, 237, 255, 0.66)",
    noiseOpacity: "0.08",
    blendMode: "lighten"
  },
  widgets: {
    controlRadius: "14px",
    surfaceRadius: "22px",
    inlineRadius: "12px",
    buttonPrimaryBackground: "linear-gradient(124deg, rgba(97, 210, 255, 0.95), rgba(99, 154, 255, 0.92))",
    buttonPrimaryForeground: "rgba(7, 27, 42, 0.96)",
    buttonPrimaryBorder: "rgba(171, 234, 255, 0.36)",
    buttonPrimaryShadow: "0 14px 30px rgba(70, 181, 237, 0.24), inset 0 1px 0 rgba(196, 243, 255, 0.32)",
    buttonSecondaryBackground: "rgba(24, 42, 75, 0.6)",
    buttonSecondaryForeground: "rgba(214, 229, 247, 0.96)",
    buttonSecondaryBorder: "rgba(112, 166, 221, 0.3)",
    buttonSecondaryShadow: "0 10px 20px rgba(2, 9, 24, 0.34), inset 0 1px 0 rgba(165, 223, 255, 0.12)",
    buttonGhostBackground: "rgba(18, 33, 60, 0.28)",
    buttonGhostForeground: "rgba(178, 200, 227, 0.92)",
    buttonGhostBorder: "rgba(111, 164, 220, 0.16)",
    buttonDangerBackground: "rgba(244, 130, 181, 0.18)",
    buttonDangerForeground: "rgba(255, 226, 241, 0.96)",
    buttonDangerBorder: "rgba(248, 158, 200, 0.34)",
    fieldBackground: "rgba(12, 23, 42, 0.74)",
    fieldBorder: "rgba(110, 163, 219, 0.3)",
    fieldFocusRing: "rgba(99, 200, 255, 0.42)",
    pillBackground: "rgba(23, 40, 72, 0.46)",
    pillBorder: "rgba(111, 165, 222, 0.26)",
    pillActiveBackground: "rgba(93, 200, 255, 0.2)",
    pillActiveBorder: "rgba(158, 224, 255, 0.34)",
    pillActiveForeground: "rgba(224, 244, 255, 0.98)",
    tableRowBackground: "rgba(16, 30, 54, 0.38)",
    tableRowHover: "rgba(80, 175, 237, 0.17)",
    tableDivider: "rgba(106, 159, 216, 0.21)",
    modalBackground: "linear-gradient(164deg, rgba(13, 24, 46, 0.95), rgba(7, 12, 22, 0.92))",
    modalBorder: "rgba(119, 177, 237, 0.32)",
    modalShadow: "0 42px 96px rgba(1, 4, 14, 0.72), inset 0 1px 0 rgba(164, 223, 255, 0.15)",
    loaderTrack: "rgba(109, 164, 220, 0.24)",
    loaderBar: "linear-gradient(90deg, rgba(93, 206, 255, 1), rgba(147, 141, 255, 0.92))"
  },
  typography: {
    bodyFont: "var(--font-space-grotesk)",
    headingFont: "var(--font-space-grotesk)",
    monoFont: "var(--font-ibm-plex-mono)",
    bodyWeight: "440",
    headingWeight: "560",
    headingTracking: "-0.02em",
    displayTracking: "-0.03em"
  },
  dataViz: {
    series: chartSeries("#5FD1FF", "#8C8DFF", "#6DE9BD", "#F38AC8"),
    grid: "rgba(115, 174, 235, 0.24)",
    axis: "rgba(192, 220, 245, 0.84)",
    glow: "0 0 18px rgba(93, 206, 255, 0.28)",
    surface: "rgba(11, 20, 37, 0.74)"
  }
};

const lightBase: ThemeSections = {
  ...darkBase,
  color: {
    ...darkBase.color,
    canvas: "236 243 252",
    surface: "243 248 255",
    panel: "248 251 255",
    elevated: "252 254 255",
    text: "55 67 86",
    heading: "31 41 58",
    muted: "112 127 148",
    subtle: "145 159 178",
    border: "191 205 226",
    borderStrong: "166 182 204",
    accent: "86 142 218",
    accentSoft: "161 199 247",
    accentContrast: "21 39 72",
    selectionBg: "rgba(124, 172, 241, 0.34)",
    selectionText: "rgba(21, 39, 72, 1)",
    scrollbarThumb: "rgba(157, 177, 206, 0.56)"
  },
  material: {
    ...darkBase.material,
    chromeBackground: "linear-gradient(154deg, rgba(248, 252, 255, 0.9), rgba(236, 245, 255, 0.82))",
    chromeBorder: "rgba(168, 186, 211, 0.28)",
    chromeShadow: "0 24px 46px rgba(118, 140, 176, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.76)",
    chromeBlur: "16px",
    surfacePrimary: "linear-gradient(158deg, rgba(250, 253, 255, 0.9), rgba(240, 247, 255, 0.82))",
    surfaceSecondary: "linear-gradient(160deg, rgba(245, 251, 255, 0.88), rgba(236, 245, 255, 0.76))",
    surfaceMuted: "rgba(245, 250, 255, 0.84)",
    surfaceElevated: "linear-gradient(148deg, rgba(253, 255, 255, 0.95), rgba(242, 249, 255, 0.86))",
    surfaceBorder: "rgba(171, 189, 214, 0.24)",
    surfaceEdge: "rgba(255, 255, 255, 0.78)",
    surfaceShadow: "0 16px 32px rgba(125, 147, 181, 0.14), inset 0 1px 0 rgba(255, 255, 255, 0.72)",
    inlineBackground: "rgba(246, 251, 255, 0.86)",
    inlineBorder: "rgba(171, 189, 214, 0.24)",
    overlayBackground: "linear-gradient(162deg, rgba(252, 255, 255, 0.97), rgba(239, 248, 255, 0.92))",
    overlayBorder: "rgba(171, 189, 214, 0.28)",
    overlayShadow: "0 34px 68px rgba(115, 138, 173, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.82)"
  },
  chrome: {
    ...darkBase.chrome,
    shellRadius: "26px",
    navActiveBackground: "rgba(214, 231, 255, 0.86)",
    navActiveBorder: "rgba(158, 184, 218, 0.4)",
    navActiveShadow: "0 8px 16px rgba(124, 152, 189, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.84)",
    navIdleBackground: "rgba(241, 248, 255, 0.74)",
    navIdleHoverBackground: "rgba(232, 243, 255, 0.92)",
    clusterBackground: "rgba(243, 249, 255, 0.82)",
    clusterBorder: "rgba(171, 189, 214, 0.24)",
    chipBackground: "rgba(241, 248, 255, 0.86)",
    chipBorder: "rgba(170, 188, 214, 0.2)",
    chipText: "rgba(72, 87, 109, 0.92)"
  },
  motion: {
    ...darkBase.motion,
    productiveDuration: "120ms",
    standardDuration: "185ms",
    expressiveDuration: "280ms",
    backdropCadence: { drift3: "6.2s", drift5: "10.4s", drift10: "18.6s" }
  },
  backdrop: {
    ...darkBase.backdrop,
    baseGradient:
      "radial-gradient(circle at 10% -10%, rgba(179, 208, 245, 0.38), transparent 44%), radial-gradient(circle at 88% 11%, rgba(196, 222, 255, 0.36), transparent 42%), radial-gradient(circle at 74% 58%, rgba(175, 209, 247, 0.24), transparent 50%), radial-gradient(circle at 50% 114%, rgba(210, 231, 255, 0.46), transparent 56%), linear-gradient(180deg, rgba(235, 243, 253, 1), rgba(224, 236, 249, 1))",
    mistGradient:
      "linear-gradient(118deg, rgba(255, 255, 255, 0.72), transparent 40%), linear-gradient(302deg, rgba(189, 217, 250, 0.3), transparent 54%), radial-gradient(circle at 32% 62%, rgba(199, 224, 255, 0.2), transparent 58%)",
    vignetteGradient: "linear-gradient(180deg, rgba(221, 233, 248, 0.08) 0%, rgba(206, 220, 238, 0.26) 100%)",
    particleNearColor: "rgba(214, 234, 255, 0.24)",
    particleFarColor: "rgba(172, 204, 238, 0.14)",
    sparkleColor: "rgba(247, 252, 255, 0.7)",
    blendMode: "multiply"
  },
  widgets: {
    ...darkBase.widgets,
    buttonPrimaryBackground: "linear-gradient(124deg, rgba(130, 177, 240, 0.96), rgba(96, 145, 218, 0.94))",
    buttonPrimaryForeground: "rgba(20, 39, 69, 0.97)",
    buttonPrimaryBorder: "rgba(208, 226, 251, 0.44)",
    buttonPrimaryShadow: "0 12px 24px rgba(109, 146, 203, 0.22), inset 0 1px 0 rgba(237, 246, 255, 0.54)",
    buttonSecondaryBackground: "rgba(246, 251, 255, 0.88)",
    buttonSecondaryForeground: "rgba(73, 87, 107, 0.95)",
    buttonSecondaryBorder: "rgba(172, 190, 215, 0.32)",
    buttonSecondaryShadow: "0 8px 16px rgba(122, 142, 174, 0.14), inset 0 1px 0 rgba(255, 255, 255, 0.78)",
    buttonGhostBackground: "rgba(241, 248, 255, 0.68)",
    buttonGhostForeground: "rgba(92, 109, 131, 0.92)",
    buttonGhostBorder: "rgba(170, 189, 214, 0.2)",
    buttonDangerBackground: "rgba(206, 107, 132, 0.14)",
    buttonDangerForeground: "rgba(141, 63, 83, 0.96)",
    buttonDangerBorder: "rgba(198, 122, 145, 0.32)",
    fieldBackground: "rgba(248, 252, 255, 0.92)",
    fieldBorder: "rgba(171, 189, 214, 0.3)",
    fieldFocusRing: "rgba(114, 165, 238, 0.32)",
    pillBackground: "rgba(241, 248, 255, 0.82)",
    pillBorder: "rgba(171, 189, 214, 0.24)",
    pillActiveBackground: "rgba(206, 228, 255, 0.74)",
    pillActiveBorder: "rgba(151, 181, 220, 0.36)",
    pillActiveForeground: "rgba(50, 70, 99, 0.96)",
    tableRowBackground: "rgba(247, 251, 255, 0.82)",
    tableRowHover: "rgba(218, 233, 252, 0.62)",
    tableDivider: "rgba(171, 189, 214, 0.2)",
    modalBackground: "linear-gradient(160deg, rgba(253, 255, 255, 0.97), rgba(238, 248, 255, 0.94))",
    modalBorder: "rgba(171, 189, 214, 0.3)",
    modalShadow: "0 34px 74px rgba(118, 139, 173, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.84)",
    loaderTrack: "rgba(168, 188, 213, 0.26)",
    loaderBar: "linear-gradient(90deg, rgba(130, 178, 240, 1), rgba(111, 153, 224, 0.95))"
  },
  typography: {
    ...darkBase.typography,
    bodyFont: "var(--font-manrope)",
    headingFont: "var(--font-fraunces)"
  },
  dataViz: {
    ...darkBase.dataViz,
    series: chartSeries("#7EAFEA", "#9BC3F5", "#89BFA9", "#CB97B8"),
    grid: "rgba(172, 189, 214, 0.24)",
    axis: "rgba(105, 120, 143, 0.86)",
    glow: "0 0 14px rgba(126, 175, 234, 0.24)",
    surface: "rgba(245, 250, 255, 0.9)"
  }
};

const liveThemeSpecs: Record<"aurora" | "solstice" | "neon", ThemeSpec> = {
  aurora: createTheme(
    {
      id: "aurora",
      labelKey: "shell.theme.option.aurora",
      premium: true,
      slot: "live",
      selectorVisible: true,
      colorScheme: "dark",
      personality: "nebula-midnight"
    },
    darkBase
  ),
  solstice: createTheme(
    {
      id: "solstice",
      labelKey: "shell.theme.option.solstice",
      premium: true,
      slot: "live",
      selectorVisible: true,
      colorScheme: "light",
      personality: "pearl-mist"
    },
    lightBase
  ),
  neon: createTheme(
    {
      id: "neon",
      labelKey: "shell.theme.option.neon",
      premium: true,
      slot: "live",
      selectorVisible: true,
      colorScheme: "dark",
      personality: "nova-rose"
    },
    darkBase,
    {
      color: {
        canvas: "13 8 18",
        surface: "24 14 31",
        panel: "31 18 39",
        elevated: "40 22 48",
        text: "238 225 240",
        heading: "253 244 252",
        muted: "183 160 188",
        subtle: "138 116 145",
        border: "107 82 119",
        borderStrong: "151 114 165",
        accent: "248 110 194",
        accentSoft: "255 188 227",
        accentContrast: "46 16 39",
        selectionBg: "rgba(248, 110, 194, 0.34)",
        selectionText: "rgba(255, 241, 250, 1)",
        scrollbarThumb: "rgba(226, 145, 198, 0.54)"
      },
      material: {
        chromeBackground: "linear-gradient(140deg, rgba(39, 22, 44, 0.9), rgba(16, 10, 20, 0.76))",
        chromeBorder: "rgba(251, 182, 222, 0.24)",
        chromeShadow: "0 26px 56px rgba(5, 2, 8, 0.62), inset 0 1px 0 rgba(255, 224, 242, 0.18)",
        surfacePrimary: "linear-gradient(150deg, rgba(33, 20, 39, 0.86), rgba(18, 11, 23, 0.76))",
        surfaceSecondary: "linear-gradient(158deg, rgba(40, 24, 47, 0.76), rgba(22, 14, 28, 0.66))",
        surfaceMuted: "rgba(34, 20, 41, 0.68)",
        surfaceElevated: "linear-gradient(152deg, rgba(47, 26, 52, 0.86), rgba(24, 15, 30, 0.78))",
        surfaceBorder: "rgba(244, 166, 214, 0.22)",
        surfaceEdge: "rgba(255, 226, 241, 0.17)",
        surfaceShadow: "0 20px 44px rgba(6, 2, 9, 0.5), inset 0 1px 0 rgba(255, 222, 240, 0.1)",
        inlineBackground: "rgba(42, 24, 49, 0.5)",
        inlineBorder: "rgba(244, 166, 214, 0.22)",
        overlayBackground: "linear-gradient(164deg, rgba(40, 23, 44, 0.95), rgba(15, 9, 19, 0.91))",
        overlayBorder: "rgba(247, 178, 220, 0.3)",
        overlayShadow: "0 38px 92px rgba(3, 1, 6, 0.7), inset 0 1px 0 rgba(255, 224, 242, 0.16)"
      },
      chrome: {
        shellRadius: "27px",
        navActiveBackground: "rgba(248, 121, 199, 0.18)",
        navActiveBorder: "rgba(253, 193, 228, 0.34)",
        navActiveShadow: "0 10px 22px rgba(236, 112, 192, 0.24), inset 0 1px 0 rgba(255, 226, 241, 0.2)",
        navIdleBackground: "rgba(44, 26, 50, 0.4)",
        navIdleHoverBackground: "rgba(59, 33, 66, 0.54)",
        clusterBackground: "rgba(45, 25, 50, 0.46)",
        clusterBorder: "rgba(244, 166, 214, 0.22)",
        chipBackground: "rgba(46, 26, 51, 0.5)",
        chipBorder: "rgba(243, 165, 213, 0.2)",
        chipText: "rgba(240, 226, 241, 0.95)"
      },
      motion: {
        productiveDuration: "115ms",
        standardDuration: "190ms",
        expressiveDuration: "300ms",
        backdropCadence: { drift3: "6.05s", drift5: "10.25s", drift10: "18.2s" }
      },
      backdrop: {
        baseGradient:
          "radial-gradient(circle at 9% -10%, rgba(247, 123, 198, 0.34), transparent 44%), radial-gradient(circle at 88% 10%, rgba(201, 117, 245, 0.3), transparent 42%), radial-gradient(circle at 72% 56%, rgba(234, 126, 200, 0.22), transparent 48%), radial-gradient(circle at 50% 114%, rgba(136, 69, 166, 0.42), transparent 58%), linear-gradient(180deg, rgba(14, 9, 19, 1), rgba(8, 6, 13, 1))",
        mistGradient:
          "linear-gradient(114deg, rgba(255, 188, 227, 0.15), transparent 46%), linear-gradient(304deg, rgba(223, 141, 255, 0.14), transparent 52%), radial-gradient(circle at 30% 62%, rgba(255, 166, 222, 0.14), transparent 56%)",
        vignetteGradient: "linear-gradient(180deg, rgba(8, 6, 13, 0.1) 0%, rgba(8, 6, 13, 0.56) 100%)",
        particleNearColor: "rgba(255, 197, 230, 0.24)",
        particleFarColor: "rgba(221, 148, 240, 0.14)",
        sparkleColor: "rgba(255, 230, 245, 0.66)",
        blendMode: "screen"
      },
      widgets: {
        buttonPrimaryBackground: "linear-gradient(124deg, rgba(249, 128, 203, 0.95), rgba(232, 106, 176, 0.93))",
        buttonPrimaryForeground: "rgba(52, 16, 43, 0.96)",
        buttonPrimaryBorder: "rgba(255, 213, 236, 0.36)",
        buttonPrimaryShadow: "0 14px 32px rgba(229, 108, 181, 0.28), inset 0 1px 0 rgba(255, 237, 248, 0.34)",
        buttonSecondaryBackground: "rgba(60, 34, 67, 0.58)",
        buttonSecondaryForeground: "rgba(243, 228, 243, 0.96)",
        buttonSecondaryBorder: "rgba(244, 166, 214, 0.28)",
        buttonSecondaryShadow: "0 10px 20px rgba(7, 3, 11, 0.34), inset 0 1px 0 rgba(255, 221, 240, 0.12)",
        buttonGhostBackground: "rgba(50, 30, 57, 0.28)",
        buttonGhostForeground: "rgba(211, 187, 216, 0.92)",
        buttonGhostBorder: "rgba(244, 166, 214, 0.16)",
        buttonDangerBackground: "rgba(255, 127, 154, 0.22)",
        buttonDangerForeground: "rgba(255, 226, 235, 0.97)",
        buttonDangerBorder: "rgba(255, 152, 177, 0.34)",
        fieldBackground: "rgba(28, 17, 35, 0.78)",
        fieldBorder: "rgba(244, 166, 214, 0.28)",
        fieldFocusRing: "rgba(249, 130, 203, 0.4)",
        pillBackground: "rgba(48, 28, 55, 0.48)",
        pillBorder: "rgba(244, 166, 214, 0.24)",
        pillActiveBackground: "rgba(249, 130, 203, 0.2)",
        pillActiveBorder: "rgba(255, 208, 234, 0.34)",
        pillActiveForeground: "rgba(255, 236, 247, 0.98)",
        tableRowBackground: "rgba(36, 20, 43, 0.4)",
        tableRowHover: "rgba(232, 112, 189, 0.16)",
        tableDivider: "rgba(244, 166, 214, 0.2)",
        modalBackground: "linear-gradient(164deg, rgba(39, 23, 43, 0.95), rgba(15, 9, 19, 0.92))",
        modalBorder: "rgba(246, 176, 220, 0.32)",
        modalShadow: "0 42px 98px rgba(4, 1, 6, 0.72), inset 0 1px 0 rgba(255, 225, 242, 0.15)",
        loaderTrack: "rgba(244, 166, 214, 0.22)",
        loaderBar: "linear-gradient(90deg, rgba(249, 128, 203, 1), rgba(223, 141, 255, 0.9))"
      },
      typography: {
        bodyFont: "var(--font-manrope)",
        headingFont: "var(--font-fraunces)",
        bodyWeight: "445",
        headingTracking: "-0.024em",
        displayTracking: "-0.034em"
      },
      dataViz: {
        series: chartSeries("#F67AC3", "#E18BFF", "#83D9B1", "#FFC39A"),
        grid: "rgba(245, 167, 214, 0.22)",
        axis: "rgba(232, 212, 234, 0.84)",
        glow: "0 0 18px rgba(248, 128, 203, 0.3)",
        surface: "rgba(30, 18, 36, 0.76)"
      }
    }
  )
};

function createReservedTheme(id: "slot_01" | "slot_02", colorScheme: "light" | "dark"): ThemeSpec {
  const base = colorScheme === "light" ? lightBase : darkBase;
  return createTheme(
    {
      id,
      labelKey: `shell.theme.option.${id}`,
      premium: false,
      slot: "reserved",
      selectorVisible: false,
      colorScheme,
      personality: colorScheme === "light" ? "reserved-neutral-light" : "reserved-neutral-dark"
    },
    base
  );
}

const reservedThemeSpecs: Record<"slot_01" | "slot_02", ThemeSpec> = {
  slot_01: createReservedTheme("slot_01", "light"),
  slot_02: createReservedTheme("slot_02", "dark")
};

export const UI_THEME_IDS = ["aurora", "solstice", "neon", "slot_01", "slot_02"] as const;

export const UI_THEME_SPECS: Record<UiThemeId, ThemeSpec> = {
  ...liveThemeSpecs,
  ...reservedThemeSpecs
};
