import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const read = (rel) => fs.readFileSync(path.join(root, rel), "utf8");
const fail = (message) => {
  console.error(`FAIL: ${message}`);
  process.exitCode = 1;
};
const pass = (message) => console.log(`PASS: ${message}`);

const files = {
  returnsPage: "app/returns/page.tsx",
  returnRoute: "app/sales/today/[saleId]/return/page.tsx",
  returnScreen: "components/returns/return-from-ticket-screen.tsx",
  returnsCss: "components/returns/returns.module.css",
  viewModel: "src/lib/returns-contextual/return-view-model.ts",
  packageJson: "package.json"
};

for (const [label, rel] of Object.entries(files)) {
  if (!fs.existsSync(path.join(root, rel))) fail(`${label} missing: ${rel}`);
}

if (process.exitCode) process.exit(1);

const returnsPage = read(files.returnsPage);
const returnRoute = read(files.returnRoute);
const returnScreen = read(files.returnScreen);
const returnsCss = read(files.returnsCss);
const viewModel = read(files.viewModel);
const pkg = read(files.packageJson);

if (/redirect\s*\(\s*["']\/sales\/today["']\s*\)/.test(returnsPage)) fail("/returns must not be a redirect-only alias to /sales/today");
if (!returnsPage.includes("ReturnsWorkspace") || !returnsPage.includes('mode="landing"')) fail("/returns must render the real returns landing workspace");
if (!returnsPage.includes("getTabletRuntimeSnapshot") || !returnsPage.includes("runtimeSnapshot")) fail("/returns must pass runtimeSnapshot into the shell screen");

if (!returnRoute.includes("await params")) fail("ticket return route must await params");
if (!returnRoute.includes("await searchParams")) fail("ticket return route must await searchParams");
if (!returnRoute.includes("getTabletRuntimeSnapshot") || !returnRoute.includes("runtimeSnapshot")) fail("ticket return route must pass runtimeSnapshot");
if (!returnRoute.includes("businessId")) fail("ticket return route must preserve businessId search param");

if (!returnScreen.includes("/api/pos/sales/detail")) fail("return screen must use robust sales detail endpoint");
if (returnScreen.includes("/api/pos/sales/today\").then") || /requestJson<\{\s*summary:\s*SalesTodaySummary\s*\}>\(\s*`?\/api\/pos\/sales\/today/.test(returnScreen) && !returnScreen.includes("ReturnsLandingScreen")) fail("ticket return screen must not load ticket detail from sales summary");
if (!returnScreen.includes("runtimeSnapshot")) fail("return screen must accept/pass runtimeSnapshot");
if (!returnScreen.includes("currentPath={`/sales/today/${encodeURIComponent(saleId)}/return`}")) fail("return screen must use return-aware currentPath");
if (!returnScreen.includes("Confirmar devolución")) fail("confirm return button is missing");
if (!returnScreen.includes("setLineQty")) fail("line quantity controls are missing");
if (!returnScreen.includes("RETURN_REASONS")) fail("return reason controls are missing");

if (/\.returnPage\s*\{[^}]*color\s*:\s*(white|#fff|#ffffff)\b/is.test(returnsCss)) fail(".returnPage must not use white as default text on light Tablet background");
if (!returnsCss.includes("var(--prisma-text-primary)")) fail("returns CSS must use the canonical high-contrast text token");
if (!returnsCss.includes("@media")) fail("returns CSS must include responsive rules");
if (!returnsCss.includes(".qtyControls")) fail("returns CSS must style quantity controls");

if (viewModel.includes("biz_tablet_standalone")) fail("return payload must not hardcode biz_tablet_standalone");
if (!viewModel.includes("businessId: ticket.businessId")) fail("return payload must use the ticket businessId");
if (!viewModel.includes("saleLineId: line.id")) fail("return payload must include saleLineId");
if (!viewModel.includes("productName: line.productName")) fail("return payload must include productName");
if (!viewModel.includes("amountCents: line.qty * line.priceCents")) fail("return payload must include line amount");

if (!pkg.includes("verify:tablet-returns-contextual")) fail("package.json must expose verify:tablet-returns-contextual");

if (process.exitCode) process.exit(1);
pass("tablet contextual returns screen guard");
