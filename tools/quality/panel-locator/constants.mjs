export const PANEL_LOCATOR_VERSION = '1.0.0';
export const DEFAULT_WORKERS = 18;
export const DEFAULT_REPORT_DIR_NAME = 'panel-locator';
export const ROOT_CONFIG_FILE = '.panel-locator.json';
export const SUPPORTED_CODE_EXTENSIONS = new Set(['.tsx', '.ts', '.jsx', '.js', '.mjs', '.cjs']);
export const SUPPORTED_STYLE_EXTENSIONS = new Set(['.css', '.scss', '.sass', '.module.css', '.module.scss']);
export const SUPPORTED_DOC_EXTENSIONS = new Set(['.md', '.mdx']);
export const MAX_DEFAULT_FILE_BYTES = 2_500_000;
export const MAX_LARGE_FILE_BYTES = 20_000_000;
export const BINARY_EXTENSIONS = new Set(['.png','.jpg','.jpeg','.gif','.webp','.avif','.ico','.pdf','.zip','.7z','.rar','.exe','.dll','.node','.wasm','.mp4','.mov','.avi','.mp3','.wav','.ttf','.otf','.woff','.woff2']);
export const DEFAULT_IGNORED_DIRS = new Set(['.git','node_modules','.next','dist','build','coverage','.turbo','out','.cache','__pycache__','.prisma_installer_backups','.pnpm-store']);
export const DEFAULT_SURFACE_RULES = [
  { id: 'tablet', label: 'Tablet', patterns: ['products/tablet/', 'apps/terminal-de-venta-system/products/tablet/'] },
  { id: 'tablet-pos', label: 'Tablet POS', patterns: ['products/tablet/app/components/pos/', 'tablet/app/components/pos/'] },
  { id: 'pc', label: 'PC', patterns: ['products/pc/', 'apps/terminal-de-venta-system/products/pc/'] },
  { id: 'mobile', label: 'Mobile', patterns: ['products/mobile/', 'apps/terminal-de-venta-system/products/mobile/'] },
  { id: 'chart-lab', label: 'Chart Lab', patterns: ['products/chart-lab/', 'chart-lab/'] },
  { id: 'shared-ui', label: 'Shared UI', patterns: ['shared/', 'packages/ui/', 'components/shared/', 'products/shared/'] },
  { id: 'governance', label: 'Governance', patterns: ['.governance/', 'docs/governance/', 'governance/'] },
  { id: 'docs', label: 'Docs', patterns: ['docs/'] },
  { id: 'tools', label: 'Tools', patterns: ['tools/'] },
  { id: 'root', label: 'Root', patterns: ['package.json', 'pnpm-workspace.yaml'] },
];
export const PANEL_KEYWORDS = [
  'panel','card','sheet','drawer','modal','dialog','ticket','checkout','cart','rail','shell','header','footer','toolbar','search','product','payment','keypad','grid','list','summary','total','action','button','hero','nav','sidebar','container','surface','glass','premium','empty','state','toast','popover','tabs','drawer','basket','order','receipt','catalog','filter','pagination','keyboard','customer','supplier','inventory','metric','tile','stripe','banner','layer','overlay','mask','backdrop','body','content','frame','section','zone','slot','cta'
];
export const HUMAN_PANEL_ALIASES = [
  ['ticket', 'Ticket panel'], ['checkout', 'Checkout panel'], ['payment', 'Payment panel'], ['cart', 'Cart panel'], ['search', 'Search panel'], ['product', 'Product card'], ['grid', 'Product grid'], ['keypad', 'Keypad'], ['hero', 'Hero panel'], ['summary', 'Summary panel'], ['total', 'Totals panel'], ['empty', 'Empty state'], ['rail', 'Rail'], ['sheet', 'Sheet'], ['drawer', 'Drawer'], ['modal', 'Modal'], ['dialog', 'Dialog'], ['toolbar', 'Toolbar'], ['pagination', 'Pagination'], ['customer', 'Customer panel'], ['supplier', 'Supplier panel'], ['inventory', 'Inventory panel'], ['metric', 'Metric card'], ['glass', 'Glass surface'], ['premium', 'Premium surface']
];
export const VISUAL_RISK_DEFINITIONS = [
  { id: 'display-none', severity: 8, pattern: 'display\\s*:\\s*none\\b', category: 'visibility', message: 'can hide entire panels or states' },
  { id: 'visibility-hidden', severity: 7, pattern: 'visibility\\s*:\\s*hidden\\b', category: 'visibility', message: 'can hide interactive UI without removing layout' },
  { id: 'position-fixed', severity: 8, pattern: 'position\\s*:\\s*fixed\\b', category: 'layout', message: 'can escape normal panel ownership' },
  { id: 'position-absolute', severity: 5, pattern: 'position\\s*:\\s*absolute\\b', category: 'layout', message: 'can create local layer coupling' },
  { id: 'z-index-high', severity: 8, pattern: 'z-index\\s*:\\s*(?:[5-9][0-9]{2,}|[1-9][0-9]{3,})', category: 'layering', message: 'can sit above unrelated UI' },
  { id: 'z-index-any', severity: 4, pattern: 'z-index\\s*:', category: 'layering', message: 'changes stacking context' },
  { id: 'overflow-hidden', severity: 6, pattern: 'overflow(?:-[xy])?\\s*:\\s*hidden\\b', category: 'layout', message: 'can clip content, glows, menus, or focus rings' },
  { id: 'inset-zero', severity: 5, pattern: '\\binset\\s*:\\s*0\\b', category: 'layering', message: 'often means full-cover layer' },
  { id: 'height-forced', severity: 4, pattern: '\\b(?:height|max-height|min-height)\\s*:', category: 'layout', message: 'may constrain adaptive layouts' },
  { id: 'width-forced', severity: 4, pattern: '\\b(?:width|max-width|min-width)\\s*:', category: 'layout', message: 'may constrain responsive layouts' },
  { id: 'backdrop-filter', severity: 5, pattern: 'backdrop-filter\\s*:', category: 'visual-effect', message: 'expensive visual effect and layer coupling' },
  { id: 'filter', severity: 4, pattern: '(?<!backdrop-)filter\\s*:', category: 'visual-effect', message: 'can affect paint cost and perceived contrast' },
  { id: 'pointer-events-none', severity: 7, pattern: 'pointer-events\\s*:\\s*none\\b', category: 'interaction', message: 'can break touch/click behavior' },
  { id: 'opacity-zero', severity: 7, pattern: 'opacity\\s*:\\s*0(?:\\.0+)?\\b', category: 'visibility', message: 'invisible but possibly interactive' },
  { id: 'transform', severity: 4, pattern: 'transform\\s*:', category: 'layout', message: 'creates stacking context and compositor work' },
  { id: 'box-shadow', severity: 3, pattern: 'box-shadow\\s*:', category: 'visual-effect', message: 'can be intended polish or paint risk' },
  { id: 'transition-all', severity: 5, pattern: 'transition(?:-property)?\\s*:\\s*all\\b', category: 'motion', message: 'can animate unintended properties' },
  { id: 'animation', severity: 4, pattern: 'animation(?:-name)?\\s*:', category: 'motion', message: 'can affect motion budget' },
  { id: 'negative-margin', severity: 5, pattern: 'margin(?:-[a-z]+)?\\s*:\\s*-', category: 'layout', message: 'can create invisible layout coupling' },
  { id: 'full-viewport', severity: 6, pattern: '(?:100vh|100dvh|100vw|100dvw)', category: 'layout', message: 'may fight tablet viewport shells' },
];
export const OUTPUT_FILES = {
  report: 'PANEL_LOCATOR_REPORT.md',
  selectorMap: 'PANEL_SELECTOR_MAP.json',
  surfaceMap: 'SURFACE_COMPONENT_MAP.md',
  ownerMap: 'CSS_MODULE_OWNER_MAP.json',
  pseudoMap: 'PSEUDO_LAYER_MAP.json',
  riskReport: 'VISUAL_RISK_REPORT.md',
  duplicateReport: 'DUPLICATE_SELECTOR_REPORT.md',
  guide: 'PANEL_CHANGE_GUIDE.md',
  summary: 'SUMMARY.json',
  continuation: 'CONTINUATION.md',
};
export function createRiskRegexes(){
  return VISUAL_RISK_DEFINITIONS.map((rule) => ({...rule, regex: new RegExp(rule.pattern, 'i')}));
}
