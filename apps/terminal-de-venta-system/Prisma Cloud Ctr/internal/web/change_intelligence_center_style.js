(function () {
  "use strict";
  const css = String.raw`
:root{
  --pci-text:var(--cc-text,#f4f8fc);
  --pci-muted:var(--cc-muted,#c4d1dc);
  --pci-soft:var(--cc-soft,rgba(229,244,255,.76));
  --pci-line:var(--cc-line,rgba(205,234,255,.13));
  --pci-line-soft:var(--cc-line-soft,rgba(236,250,255,.095));
  --pci-accent:var(--cc-accent,#a9eeff);
  --pci-accent-2:var(--cc-accent-2,#c4d6ff);
  --pci-accent-3:var(--cc-accent-3,#d7c6ff);
  --pci-ok:var(--cc-ok,#8ff7d1);
  --pci-warn:var(--cc-warn,#ffd38c);
  --pci-bad:var(--cc-bad,#ff9aa6);
  --pci-panel:var(--cc-panel,rgba(7,16,29,.16));
  --pci-card:var(--cc-card,rgba(7,16,29,.13));
  --pci-glass:var(--cc-glass-fill,rgba(18,34,51,.20));
  --pci-glass-soft:var(--cc-glass-fill-soft,rgba(18,34,51,.14));
  --pci-radius-xl:var(--cc-radius-xl,30px);
  --pci-radius-lg:var(--cc-radius-lg,24px);
  --pci-radius-md:var(--cc-radius-md,18px);
  --pci-radius-sm:var(--cc-radius-sm,14px);
  --pci-blur:var(--cc-blur,2px);
  --pci-shadow:var(--cc-shadow,0 14px 34px rgba(0,0,0,.11),0 0 18px rgba(120,235,255,.028),inset 0 1px 0 rgba(255,255,255,.070));
}
*{box-sizing:border-box}
html{min-height:100%;color-scheme:dark}
body.pci-surface{min-height:100%;margin:0;color:var(--pci-text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;position:relative;isolation:isolate;overflow-x:hidden}
.pci-surface a,.pci-surface button,.pci-surface input{font:inherit}
.pci-atmosphere,.pci-atmosphere::before,.pci-atmosphere::after{content:"";position:fixed;pointer-events:none}
.pci-atmosphere{inset:0;z-index:0;overflow:hidden}
.pci-atmosphere::before{inset:-8%;opacity:.24;mix-blend-mode:screen;background:radial-gradient(520px 280px at 18% 22%,rgba(116,210,255,.18),transparent 70%),radial-gradient(460px 250px at 78% 18%,rgba(188,144,255,.14),transparent 72%),radial-gradient(640px 360px at 56% 82%,rgba(104,255,214,.10),transparent 76%);animation:pci-atmosphere 56s cubic-bezier(.42,0,.22,1) infinite alternate}
.pci-atmosphere::after{inset:0;opacity:.52;mix-blend-mode:normal;background:radial-gradient(1050px 640px at 50% 30%,rgba(132,205,246,.08),transparent 60%),radial-gradient(980px 540px at 10% 60%,rgba(0,15,29,.22),transparent 72%),radial-gradient(920px 520px at 92% 62%,rgba(0,14,27,.23),transparent 74%),linear-gradient(180deg,rgba(7,16,27,.10),rgba(6,17,29,.20) 74%,rgba(2,9,18,.30))}
@keyframes pci-atmosphere{from{transform:translate3d(-1.5%,-.4%,0) scale(1.01)}to{transform:translate3d(1.6%,.8%,0) scale(1.035)}}
.pci-topbar,.pci-layout,.pci-noscript{position:relative;z-index:10}
.pci-topbar{width:min(1360px,calc(100% - 48px));margin:12px auto 0;display:grid;grid-template-columns:minmax(0,1fr);gap:10px;align-items:start;padding:15px 22px 14px;border:1px solid rgba(205,234,255,.12);border-radius:28px;background:radial-gradient(circle at 8% 48%,rgba(120,235,255,.080),transparent 30%),radial-gradient(circle at 76% 20%,rgba(174,122,255,.060),transparent 24%),linear-gradient(180deg,rgba(255,255,255,.042),rgba(255,255,255,.010) 48%,rgba(255,255,255,.014)),var(--pci-glass);box-shadow:0 18px 54px rgba(0,0,0,.16),0 0 28px rgba(120,235,255,.035),inset 0 1px 0 rgba(255,255,255,.075);backdrop-filter:blur(5px) saturate(126%) contrast(104%);-webkit-backdrop-filter:blur(5px) saturate(126%) contrast(104%)}
.pci-topbar::before,.pci-hero::before,.pci-card::before,.pci-loading-card::before{content:"";position:absolute;inset:0;z-index:0;pointer-events:none;opacity:.16;mix-blend-mode:screen;background:linear-gradient(180deg,rgba(255,255,255,.065),rgba(255,255,255,0) 32%),radial-gradient(240px 105px at 14% 0%,rgba(255,255,255,.060),transparent 62%);filter:blur(6px) saturate(120%)}
.pci-topbar::after,.pci-hero::after,.pci-card::after,.pci-loading-card::after{content:"";position:absolute;inset:1px;z-index:0;border:1px solid rgba(255,255,255,.045);border-radius:inherit;pointer-events:none;opacity:.18;mix-blend-mode:screen;background:linear-gradient(135deg,rgba(255,255,255,.055),transparent 25%,transparent 66%,rgba(169,238,255,.032)),linear-gradient(180deg,rgba(255,255,255,.025),rgba(0,0,0,.015));box-shadow:inset 0 0 42px rgba(255,255,255,.016),inset 0 0 28px rgba(169,238,255,.018)}
.pci-topbar>*,.pci-hero>*,.pci-card>*,.pci-loading-card>*{position:relative;z-index:1}
.pci-brand{display:flex;gap:14px;align-items:flex-start;min-width:0;color:inherit;text-decoration:none}
.pci-brand-mark{width:64px;height:64px;flex:none;display:grid;place-items:center;border:0;border-radius:0;background:transparent;box-shadow:none}
.pci-brand-mark img{width:100%;height:100%;object-fit:contain;filter:drop-shadow(0 10px 20px rgba(0,0,0,.24)) drop-shadow(0 0 14px rgba(123,205,255,.20))}
.pci-brand-copy{min-width:0;display:grid;gap:3px}
.pci-brand-line{display:flex;flex-wrap:wrap;gap:12px;align-items:center}
.pci-logo-word{color:rgba(246,252,255,.96);font-size:18px;font-weight:950;line-height:1;letter-spacing:.26em;text-transform:uppercase;text-shadow:0 1px 0 rgba(0,0,0,.38),0 0 14px rgba(120,235,255,.20)}
.pci-brand-kicker,.pci-eyebrow{color:var(--pci-accent);font-size:11px;font-weight:900;letter-spacing:.22em;text-transform:uppercase}
.pci-brand-copy strong{margin:0;font-size:clamp(28px,2.7vw,44px);line-height:.95;letter-spacing:0;text-shadow:0 1px 0 rgba(0,0,0,.34),0 0 5px rgba(255,255,255,.34),0 0 16px rgba(120,235,255,.22),0 0 28px rgba(174,122,255,.12)}
.pci-brand-copy small{margin:3px 0 0;color:var(--pci-soft);font-size:clamp(13px,1.2vw,15px);text-transform:none}
.pci-topbar-actions{display:flex;flex-wrap:wrap;gap:0;justify-content:flex-start;align-items:center;margin-left:78px;margin-top:0}
.pci-status-chip{min-height:auto;position:relative;display:inline-flex;align-items:center;justify-content:center;border:0;border-radius:0;padding:0 17px;color:rgba(238,247,255,.82);background:transparent;box-shadow:none;font-size:11px;font-weight:900;line-height:1.4;letter-spacing:.13em;text-transform:uppercase;white-space:nowrap;text-shadow:0 0 14px rgba(120,235,255,.10)}
.pci-status-chip:first-child{padding-left:0}
.pci-status-chip+.pci-status-chip::before{content:"";position:absolute;left:0;top:50%;width:1px;height:16px;transform:translateY(-50%);background:linear-gradient(180deg,transparent,rgba(232,247,255,.32),transparent)}
.pci-status-chip[data-tone="ok"]{color:var(--pci-ok)}.pci-status-chip[data-tone="warn"]{color:var(--pci-warn)}.pci-status-chip[data-tone="bad"]{color:var(--pci-bad)}
.pci-back-link,.pci-nav a,.pci-action-link,.pci-mini-chip{display:inline-flex;align-items:center;justify-content:center;border:1px solid rgba(232,247,255,.22);border-radius:999px;color:var(--pci-text);background:linear-gradient(180deg,rgba(255,255,255,.042),rgba(255,255,255,.008)),rgba(11,22,36,.18);box-shadow:0 0 12px rgba(120,235,255,.060),0 0 18px rgba(255,105,205,.030),inset 0 1px 0 rgba(255,255,255,.055);text-decoration:none}
.pci-back-link{min-height:34px;margin-left:17px;padding:0 13px;font-size:11px;font-weight:850;letter-spacing:.08em;text-transform:uppercase;transition:transform .18s ease,border-color .18s ease,background .18s ease,color .18s ease}
.pci-back-link:hover,.pci-back-link:focus-visible,.pci-action-link:hover,.pci-action-link:focus-visible{transform:translateY(-1px);border-color:rgba(169,238,255,.50);outline:none}
.pci-layout{width:min(1360px,calc(100% - 48px));margin:16px auto 28px;display:grid;grid-template-columns:minmax(0,1fr);gap:16px}
.pci-rail{min-width:0;display:grid;gap:0}
.pci-rail-heading,.pci-rail-foot{display:none}
.pci-nav{display:flex;flex-wrap:wrap;gap:8px;align-items:center;min-width:0}
.pci-nav a{min-height:42px;padding:0 13px;color:rgba(244,248,252,.78);font-size:11px;font-weight:850;letter-spacing:.08em;text-transform:uppercase;white-space:nowrap;transition:transform .18s ease,border-color .18s ease,background .18s ease,color .18s ease}
.pci-nav a span{margin-right:7px;color:rgba(196,209,220,.62);font-size:9px;letter-spacing:.08em}
.pci-nav a:hover,.pci-nav a:focus-visible{transform:translateY(-1px);color:var(--pci-text);border-color:rgba(169,238,255,.50);outline:none}
.pci-nav a.active{color:var(--pci-text);background:linear-gradient(180deg,rgba(255,255,255,.052),rgba(255,255,255,.010)),rgba(11,22,36,.24);border-color:rgba(139,238,255,.52);box-shadow:0 0 16px rgba(120,235,255,.24),0 0 22px rgba(174,122,255,.10),inset 0 1px 0 rgba(255,255,255,.16)}
.pci-nav a.active span{color:var(--pci-accent)}
.pci-main{min-width:0;display:grid;gap:16px}
.pci-hero,.pci-card,.pci-loading-card,.pci-alert{position:relative;overflow:hidden;min-width:0;border:1px solid var(--pci-line);border-radius:var(--pci-radius-lg);background:radial-gradient(circle at 12% 0%,rgba(143,225,255,.055),transparent 36%),linear-gradient(180deg,rgba(255,255,255,.052),rgba(255,255,255,.014)),rgba(15,31,50,.20);box-shadow:var(--pci-shadow);backdrop-filter:blur(2px) saturate(108%) contrast(102%);-webkit-backdrop-filter:blur(2px) saturate(108%) contrast(102%)}
.pci-hero{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:18px;align-items:end;padding:clamp(20px,3vw,30px)}
.pci-eyebrow{margin:0 0 6px}
.pci-hero h1{margin:0;max-width:980px;font-size:clamp(36px,5vw,78px);line-height:.92;letter-spacing:0;text-shadow:0 1px 0 rgba(0,0,0,.36),0 0 6px rgba(255,255,255,.20),0 0 18px rgba(120,235,255,.55)}
.pci-hero-copy{max-width:860px;margin:12px 0 0;color:var(--pci-soft);font-size:15px;line-height:1.6}
.pci-hero-seal{min-width:210px;display:grid;gap:5px;text-align:right}
.pci-hero-seal span,.pci-hero-seal small{color:var(--pci-muted);font-size:11px;font-weight:900;letter-spacing:.14em;text-transform:uppercase}
.pci-hero-seal strong{font-size:clamp(38px,4vw,62px);line-height:.95;overflow-wrap:anywhere;color:var(--pci-text);text-shadow:0 0 18px rgba(120,235,255,.32)}
.pci-alert{display:flex;align-items:center;gap:12px 18px;padding:14px 18px;background:linear-gradient(180deg,rgba(255,255,255,.038),rgba(255,255,255,.009)),var(--pci-glass-soft);border-radius:var(--pci-radius-md)}
.pci-alert strong{flex:0 0 auto;font-size:11px;font-weight:900;letter-spacing:.12em;text-transform:uppercase}.pci-alert span{color:var(--pci-soft);font-size:13px;line-height:1.5}
.pci-alert[data-tone="ok"]{border-color:rgba(143,247,209,.30)}.pci-alert[data-tone="warn"]{border-color:rgba(255,211,140,.34)}.pci-alert[data-tone="bad"]{border-color:rgba(255,154,166,.34)}
.pci-content,.pci-grid{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:14px;align-items:start}
.pci-card{grid-column:span 6;padding:18px}.pci-card[data-span="12"]{grid-column:span 12}.pci-card[data-span="8"]{grid-column:span 8}.pci-card[data-span="4"]{grid-column:span 4}
.pci-card[data-tone="accent"]{border-color:rgba(169,238,255,.28)}.pci-card[data-tone="blocked"]{border-color:rgba(255,211,140,.30)}
.pci-card-head{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;margin-bottom:14px}.pci-card-head h2,.pci-card-head h3{margin:0;font-size:18px;line-height:1.15}.pci-card-head p{margin:7px 0 0;color:var(--pci-soft);font-size:13px;line-height:1.5}
.pci-mini-chip{min-height:28px;flex:0 0 auto;padding:0 10px;font-size:9px;font-weight:900;letter-spacing:.08em;text-transform:uppercase;background:rgba(255,255,255,.022);box-shadow:none}
.pci-mini-chip[data-tone="ok"]{color:var(--pci-ok);border-color:rgba(143,247,209,.30)}.pci-mini-chip[data-tone="warn"]{color:var(--pci-warn);border-color:rgba(255,211,140,.34)}.pci-mini-chip[data-tone="bad"]{color:var(--pci-bad);border-color:rgba(255,154,166,.34)}
.pci-kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}
.pci-kpi{position:relative;min-width:0;padding:14px 15px;border:1px solid var(--pci-line-soft);border-radius:var(--pci-radius-md);background:linear-gradient(180deg,rgba(255,255,255,.034),rgba(255,255,255,.008)),var(--pci-glass-soft);box-shadow:inset 0 1px 0 rgba(255,255,255,.045);backdrop-filter:blur(2px) saturate(108%);-webkit-backdrop-filter:blur(2px) saturate(108%)}
.pci-kpi small,.pci-kpi span{display:block;color:var(--pci-muted);font-size:11px;font-weight:850;letter-spacing:.12em;text-transform:uppercase}.pci-kpi strong{display:block;margin-top:6px;color:var(--pci-text);overflow-wrap:anywhere;font-size:18px;line-height:1.1}.pci-kpi span{margin-top:6px;color:var(--pci-soft);font-size:11px;font-weight:500;letter-spacing:0;text-transform:none}
.pci-list,.pci-timeline{display:grid;gap:0}.pci-list-row,.pci-timeline-row{display:grid;grid-template-columns:minmax(0,.9fr) minmax(0,1.4fr);gap:14px;align-items:start;padding:11px 0;border-bottom:1px solid var(--pci-line-soft)}.pci-list-row:last-child,.pci-timeline-row:last-child{border-bottom:0}.pci-list-row span,.pci-timeline-row span{color:var(--pci-muted);font-size:12px}.pci-list-row strong,.pci-timeline-row strong{overflow-wrap:anywhere;font-size:12px;line-height:1.5;text-align:right}
.pci-flow{display:grid;grid-template-columns:repeat(9,minmax(0,1fr));gap:8px}.pci-flow-step{display:grid;min-height:78px;align-content:center;gap:5px;padding:10px;border:1px solid var(--pci-line-soft);border-radius:var(--pci-radius-sm);background:rgba(255,255,255,.022)}.pci-flow-step strong{color:var(--pci-accent);font-size:11px;font-weight:900;letter-spacing:.08em;text-transform:uppercase}.pci-flow-step span{color:var(--pci-soft);font-size:10px;line-height:1.35}
.pci-empty{position:relative;display:grid;min-height:140px;place-items:center;padding:20px;border:1px dashed rgba(205,234,255,.20);border-radius:var(--pci-radius-md);background:rgba(255,255,255,.016);text-align:center}.pci-empty strong{font-size:15px}.pci-empty p{max-width:560px;margin:8px 0 0;color:var(--pci-soft);font-size:13px;line-height:1.55}
.pci-table-wrap{overflow-x:auto;border:1px solid var(--pci-line-soft);border-radius:var(--pci-radius-md);background:rgba(255,255,255,.014)}.pci-table{width:100%;min-width:680px;border-collapse:collapse}.pci-table th,.pci-table td{padding:12px 14px;border-bottom:1px solid var(--pci-line-soft);text-align:left;vertical-align:top}.pci-table th{color:var(--pci-muted);background:rgba(255,255,255,.025);font-size:10px;font-weight:900;letter-spacing:.10em;text-transform:uppercase}.pci-table td{font-size:12px;line-height:1.5}
.pci-formula{display:grid;gap:9px;padding:16px;border:1px solid rgba(169,238,255,.18);border-radius:var(--pci-radius-md);background:rgba(120,235,255,.025)}.pci-formula code{overflow-wrap:anywhere;color:var(--pci-accent);font-family:"SFMono-Regular",Consolas,"Liberation Mono",monospace;font-size:12px;line-height:1.55}
.pci-action-row{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}.pci-action-link{min-height:34px;padding:0 13px;font-size:11px;font-weight:850;letter-spacing:.06em;text-transform:uppercase;transition:transform .18s ease,border-color .18s ease}.pci-code{overflow:auto;max-height:440px;margin:0;padding:15px;border:1px solid var(--pci-line-soft);border-radius:var(--pci-radius-md);background:rgba(8,20,34,.34);color:rgba(238,247,255,.82);font-family:"SFMono-Regular",Consolas,"Liberation Mono",monospace;font-size:11px;line-height:1.55;white-space:pre-wrap}
.pci-loading-card{grid-column:span 12;display:grid;min-height:220px;place-items:center;align-content:center;gap:12px;padding:30px;text-align:center}.pci-loading-card p{max-width:620px;margin:0;color:var(--pci-soft)}.pci-pulse{width:42px;height:42px;border:1px solid rgba(169,238,255,.28);border-radius:50%;box-shadow:0 0 0 0 rgba(169,238,255,.16);animation:pci-pulse 1.7s ease-out infinite}.pci-noscript{width:min(1360px,calc(100% - 48px));margin:16px auto;padding:18px;border:1px solid rgba(255,154,166,.34);border-radius:var(--pci-radius-md);background:rgba(255,154,166,.06);color:var(--pci-text)}
@keyframes pci-pulse{0%{box-shadow:0 0 0 0 rgba(169,238,255,.18)}70%{box-shadow:0 0 0 16px rgba(169,238,255,0)}100%{box-shadow:0 0 0 0 rgba(169,238,255,0)}}
.pci-surface :focus-visible{outline:2px solid rgba(169,238,255,.82);outline-offset:3px}
@media(max-width:980px){.pci-card[data-span="8"],.pci-card[data-span="4"]{grid-column:span 12}.pci-card{grid-column:span 6}.pci-flow{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:680px){
  .pci-topbar,.pci-layout,.pci-noscript{width:calc(100% - 24px)}
  .pci-topbar{padding:14px}
  .pci-brand-mark{width:52px;height:52px}
  .pci-logo-word{font-size:15px}
  .pci-brand-copy strong{font-size:clamp(26px,9vw,38px)}
  .pci-brand-copy small{font-size:12px}
  .pci-topbar-actions{margin-left:0;gap:0}
  .pci-status-chip{padding:0 10px;font-size:9px}
  .pci-status-chip:first-child{padding-left:0}
  .pci-back-link{margin-left:10px;min-height:32px;font-size:9px}
  .pci-rail{overflow:hidden}
  .pci-nav{flex-wrap:nowrap;overflow-x:auto;overscroll-behavior-inline:contain;padding-bottom:4px;scrollbar-width:thin}
  .pci-nav a{flex:0 0 auto;min-height:40px}
  .pci-hero{grid-template-columns:minmax(0,1fr);align-items:start;padding:20px}
  .pci-hero h1{font-size:clamp(34px,13vw,54px)}
  .pci-hero-seal{min-width:0;text-align:left}
  .pci-card,.pci-card[data-span="8"],.pci-card[data-span="6"],.pci-card[data-span="4"]{grid-column:span 12}
  .pci-alert{align-items:flex-start;flex-direction:column}
  .pci-list-row,.pci-timeline-row{grid-template-columns:minmax(0,1fr);gap:5px}.pci-list-row strong,.pci-timeline-row strong{text-align:left}
  .pci-kpi-grid{grid-template-columns:minmax(0,1fr)}
  .pci-flow{grid-template-columns:repeat(2,minmax(0,1fr))}
}
@media(prefers-reduced-motion:reduce){.pci-atmosphere::before,.pci-pulse{animation:none}.pci-nav a,.pci-back-link,.pci-action-link{transition:none}}
@media(prefers-reduced-transparency:reduce){
  .pci-topbar,.pci-hero,.pci-card,.pci-loading-card,.pci-alert,.pci-kpi{background:rgba(18,34,51,.92);backdrop-filter:none;-webkit-backdrop-filter:none}
  .pci-atmosphere::before,.pci-atmosphere::after{opacity:.08}
}
`;
  const style = document.createElement("style");
  style.dataset.pciStyle = "v1";
  style.dataset.pciVisualContract = "PRISMA_CLOUD_CENTER_STORMGLASS_LITE_V1";
  style.textContent = css;
  document.head.appendChild(style);
}());
