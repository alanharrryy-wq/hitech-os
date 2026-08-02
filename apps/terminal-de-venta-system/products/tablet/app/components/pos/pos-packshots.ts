/* PRISMA_DARK_PACKSHOTS_197 */
export type PosPackshotKind = "bottle" | "water" | "bag" | "carton" | "bread" | "jar" | "box";
export type PrismaPackshotSkin = "dark";

export type PosPackshot = {
  src: string;
  alt: string;
  kind: PosPackshotKind;
  skin: PrismaPackshotSkin;
  slug: string;
  fallbackSrcs: string[];
};

/* PRISMA_TABLET_PACKSHOT_ENGINE_01
 * PRISMA_TABLET_PACKSHOT_ENGINE_02
 * PRISMA_TABLET_PACKSHOT_ENGINE_03
 * Visual-only resolver for skin-aware product packshots.
 *
 * Public asset contract:
 *   managed product media -> /product-media/catalog/*.png
 *
 * Why v03 exists:
 * v02 mapped the generated image library, but water products still collapsed into one
 * repeated bottle. v03 adds specific water aliases and keeps the resolver visual-only.
 *
 * This file must remain visual-only. Do not change POS sale, stock, sync, DB or API behavior here.
 */
export const POS_PACKSHOT_FILENAMES = [
  "water_bottle_512.png",
  "cola_bottle_512.png",
  "chips_bag_512.png",
  "milk_carton_512.png",
  "bread_loaf_512.png",
  "coffee_jar_512.png",
  "detergent_bag_512.png",
  "cereal_box_512.png",
  "candy_bar_512.png",
  "icecream_bar_512.png",
  "pet_food_bag_512.png",
  "hygiene_bottle_512.png",
  "disposables_stack_512.png",
  "noodles_cup_512.png",
  "counter_goods_512.png"
] as const;

const LEGACY_GENERIC_BASE = "/pos-packshots";
const LEGACY_PRODUCT_BASE = "/products/packshots";
const SKIN_PRODUCT_BASE = "/product-media/catalog";

const DEFAULT_FALLBACK_FILE = "cereal_box_512.png";

type LegacyGenericFile = (typeof POS_PACKSHOT_FILENAMES)[number];

type PackshotRule = {
  file: LegacyGenericFile | string;
  alt: string;
  kind: PosPackshotKind;
  base?: string;
  slug?: string;
  category?: string;
};

type GeneratedPackshotRule = {
  slug: string;
  alt: string;
  kind: PosPackshotKind;
  category: string;
  any: string[];
  all?: string[];
  not?: string[];
};

type ResolveOptions = {
  skin?: PrismaPackshotSkin | null;
};

const CATEGORY_FALLBACKS: Record<string, { file: LegacyGenericFile; alt: string; kind: PosPackshotKind }> = {
  bebidas: { file: "cola_bottle_512.png", alt: "Packshot genérico de bebida", kind: "bottle" },
  botanas: { file: "chips_bag_512.png", alt: "Packshot genérico de botana", kind: "bag" },
  lacteos: { file: "milk_carton_512.png", alt: "Packshot genérico de lácteo", kind: "carton" },
  panaderia: { file: "bread_loaf_512.png", alt: "Packshot genérico de panadería", kind: "bread" },
  abarrotes: { file: "coffee_jar_512.png", alt: "Packshot genérico de abarrote", kind: "jar" },
  cafe: { file: "coffee_jar_512.png", alt: "Packshot genérico de café", kind: "jar" },
  conservas: { file: "coffee_jar_512.png", alt: "Packshot genérico de conserva", kind: "jar" },
  pastas: { file: "cereal_box_512.png", alt: "Packshot genérico de pasta", kind: "box" },
  galletas: { file: "candy_bar_512.png", alt: "Packshot genérico de galletas", kind: "box" },
  cereales: { file: "cereal_box_512.png", alt: "Packshot genérico de cereal", kind: "box" },
  dulces: { file: "candy_bar_512.png", alt: "Packshot genérico de dulce", kind: "box" },
  limpieza: { file: "detergent_bag_512.png", alt: "Packshot genérico de limpieza", kind: "bag" },
  higiene: { file: "hygiene_bottle_512.png", alt: "Packshot genérico de higiene", kind: "bottle" },
  cuidado_personal: { file: "hygiene_bottle_512.png", alt: "Packshot genérico de cuidado personal", kind: "bottle" },
  papel_higienico: { file: "hygiene_bottle_512.png", alt: "Packshot genérico de papel higiénico", kind: "box" },
  mascotas: { file: "pet_food_bag_512.png", alt: "Packshot genérico de mascotas", kind: "bag" },
  desechables: { file: "disposables_stack_512.png", alt: "Packshot genérico de desechables", kind: "box" },
  mostrador: { file: "counter_goods_512.png", alt: "Packshot genérico de mostrador", kind: "box" },
  congelados: { file: "icecream_bar_512.png", alt: "Packshot genérico de congelado", kind: "carton" }
};

/* Existing generated packshot fallbacks. These names are intentionally product-generic,
 * because the new image library is generic even when labels in the source image are fictitious.
 */
const CATEGORY_SKIN_FALLBACK_SLUGS: Record<string, string> = {
  bebidas: "agua-purificada-600ml",
  botanas: "papas-clasicas-45g",
  lacteos: "leche-entera-1l",
  panaderia: "pan-blanco-680g",
  abarrotes: "arroz-1kg",
  cafe: "cafe-soluble-200g",
  conservas: "atun-en-agua-140g",
  pastas: "pasta-espagueti-500g",
  galletas: "galletas-sandwich-rellenas-de-crema-300g",
  cereales: "cereal-500g",
  dulces: "galletas-sandwich-rellenas-de-crema-300g",
  limpieza: "detergente-multiusos-1kg",
  higiene: "jabon-de-barra-humectante-150g",
  cuidado_personal: "jabon-de-barra-humectante-150g",
  papel_higienico: "papel-higienico-suave-4-rollos",
  mascotas: "croquetas-para-perro-adulto-2kg"
};

const GENERATED_PRODUCT_RULES: GeneratedPackshotRule[] = [
  { slug: "atun-en-sobre-en-agua-80g", alt: "Packshot de atún en sobre", kind: "jar", category: "conservas", any: ["atun"], all: ["sobre"] },
  { slug: "atun-en-agua-80g", alt: "Packshot de atún en agua 80 g", kind: "jar", category: "conservas", any: ["atun"], all: ["80"] },
  { slug: "atun-en-agua-140g", alt: "Packshot de atún 140 g", kind: "jar", category: "conservas", any: ["atun", "dolores"] },
  { slug: "aceite-vegetal", alt: "Packshot de aceite vegetal", kind: "bottle", category: "abarrotes", any: ["aceite", "capullo", "patrona"] },
  { slug: "arroz-1kg", alt: "Packshot de arroz", kind: "box", category: "abarrotes", any: ["arroz", "verde valle"] },
  { slug: "azucar-refinada-1kg", alt: "Packshot de azúcar", kind: "box", category: "abarrotes", any: ["azucar", "estandar"] },
  { slug: "sal-de-mesa-refinada-1kg", alt: "Packshot de sal de mesa", kind: "box", category: "abarrotes", any: ["sal"] },
  { slug: "harina-de-trigo-tradicional-1kg", alt: "Packshot de harina de trigo", kind: "box", category: "abarrotes", any: ["harina"] },
  { slug: "frijol-negro-seleccionado-900g", alt: "Packshot de frijol negro", kind: "box", category: "abarrotes", any: ["frijol"] },
  { slug: "lentejas-seleccionadas-900g", alt: "Packshot de lentejas", kind: "box", category: "abarrotes", any: ["lenteja"] },
  { slug: "pasta-espagueti-500g", alt: "Packshot de pasta espagueti", kind: "box", category: "pastas", any: ["pasta", "espagueti", "spaghetti"] },
  { slug: "avena-hojuelas-500g", alt: "Packshot de avena", kind: "box", category: "cereales", any: ["avena", "quaker"] },
  { slug: "cereal-500g", alt: "Packshot de cereal", kind: "box", category: "cereales", any: ["cereal", "zucaritas", "corn flakes", "choco krispis", "froot loops"] },
  { slug: "cafe-soluble-200g", alt: "Packshot de café soluble", kind: "jar", category: "cafe", any: ["nescafe", "cafe soluble", "clasico 200", "cafe clasico"] },
  { slug: "cafe-molido-100-arabica-250g", alt: "Packshot de café molido", kind: "bag", category: "cafe", any: ["cafe molido", "arabica"] },
  { slug: "cacao-en-polvo-400g", alt: "Packshot de cacao en polvo", kind: "box", category: "abarrotes", any: ["cacao", "chocolate en polvo"] },
  { slug: "miel-de-abeja-350g", alt: "Packshot de miel", kind: "jar", category: "abarrotes", any: ["miel"] },
  { slug: "mermelada-de-fresa-450g", alt: "Packshot de mermelada", kind: "jar", category: "abarrotes", any: ["mermelada"] },
  { slug: "mayonesa-receta-deliciosa-390g", alt: "Packshot de mayonesa", kind: "jar", category: "abarrotes", any: ["mayonesa"] },
  { slug: "salsa-de-tomate-340g", alt: "Packshot de salsa de tomate", kind: "jar", category: "abarrotes", any: ["salsa de tomate", "catsup", "ketchup"] },
  { slug: "salsa-picante-150ml", alt: "Packshot de salsa picante", kind: "bottle", category: "abarrotes", any: ["salsa picante", "valentina", "chile"] },
  { slug: "salsa-de-soya-500ml", alt: "Packshot de salsa de soya", kind: "bottle", category: "abarrotes", any: ["salsa de soya", "soya"] },
  { slug: "vinagre-blanco-750ml", alt: "Packshot de vinagre", kind: "bottle", category: "abarrotes", any: ["vinagre"] },
  { slug: "elote-dulce-en-grano-285g", alt: "Packshot de elote en grano", kind: "jar", category: "conservas", any: ["elote"] },
  { slug: "chicharos-tiernos-285g", alt: "Packshot de chícharos", kind: "jar", category: "conservas", any: ["chicharo", "chicharos", "guisante"] },
  { slug: "papas-clasicas-45g", alt: "Packshot de papas clásicas", kind: "bag", category: "botanas", any: ["papas", "sabritas", "chips", "botana", "doritos", "cheetos", "tostitos", "takis"] },
  { slug: "galletas-saladas-horneadas-200g", alt: "Packshot de galletas saladas", kind: "box", category: "galletas", any: ["galletas saladas", "crackers"] },
  { slug: "galletas-sandwich-rellenas-de-crema-300g", alt: "Packshot de galletas sándwich", kind: "box", category: "galletas", any: ["galletas", "sandwich", "crema", "oreo"], not: ["crema acida", "crema para", "crema corporal", "crema de cacahuate", "crema manos"] },
  { slug: "pan-de-caja-multigrano-fibra-y-semillas-620g", alt: "Packshot de pan multigrano", kind: "bread", category: "panaderia", any: ["multigrano", "semillas"] },
  { slug: "pan-integral-620g", alt: "Packshot de pan integral", kind: "bread", category: "panaderia", any: ["pan integral", "integral"] },
  { slug: "pan-de-centeno-sabor-intenso-620g", alt: "Packshot de pan de centeno", kind: "bread", category: "panaderia", any: ["centeno"] },
  { slug: "pan-blanco-680g", alt: "Packshot de pan blanco", kind: "bread", category: "panaderia", any: ["pan blanco", "bimbo blanco", "pan bimbo", "pan"] },
  { slug: "pan-para-hamburguesa-360g", alt: "Packshot de pan para hamburguesa", kind: "bread", category: "panaderia", any: ["hamburguesa"] },
  { slug: "pan-para-hot-dog-360g", alt: "Packshot de pan para hot dog", kind: "bread", category: "panaderia", any: ["hot dog", "hot-dog"] },
  { slug: "pan-dulce-surtido-tradicional-450g", alt: "Packshot de pan dulce", kind: "bread", category: "panaderia", any: ["pan dulce", "mantecadas", "gansito", "pinguinos", "nito"] },
  { slug: "leche-deslactosada-1l", alt: "Packshot de leche deslactosada", kind: "carton", category: "lacteos", any: ["deslactosada"] },
  { slug: "leche-descremada-1l", alt: "Packshot de leche descremada", kind: "carton", category: "lacteos", any: ["descremada"] },
  { slug: "leche-saborizada-de-chocolate-1l", alt: "Packshot de leche de chocolate", kind: "carton", category: "lacteos", any: ["leche chocolate", "sabor chocolate", "chocolate 1l"] },
  { slug: "leche-saborizada-de-fresa-1l", alt: "Packshot de leche de fresa", kind: "carton", category: "lacteos", any: ["leche fresa", "sabor fresa", "fresa 1l"] },
  { slug: "leche-condensada-387g", alt: "Packshot de leche condensada", kind: "carton", category: "lacteos", any: ["condensada"] },
  { slug: "leche-evaporada-387g", alt: "Packshot de leche evaporada", kind: "carton", category: "lacteos", any: ["evaporada"] },
  { slug: "leche-entera-1l", alt: "Packshot de leche entera", kind: "carton", category: "lacteos", any: ["leche", "lala"] },
  { slug: "bebida-de-yogur-natural-1l", alt: "Packshot de bebida de yogur", kind: "carton", category: "lacteos", any: ["yogur", "yoghurt", "yogurt"] },
  { slug: "crema-acida-400g", alt: "Packshot de crema ácida", kind: "carton", category: "lacteos", any: ["crema acida", "crema ácida"] },
  { slug: "crema-para-batir-500ml", alt: "Packshot de crema para batir", kind: "carton", category: "lacteos", any: ["crema para batir"] },
  { slug: "crema-para-cafe-500ml", alt: "Packshot de crema para café", kind: "carton", category: "lacteos", any: ["crema para cafe", "crema para café"] },
  { slug: "mantequilla-200g", alt: "Packshot de mantequilla", kind: "carton", category: "lacteos", any: ["mantequilla"] },
  { slug: "margarina-225g", alt: "Packshot de margarina", kind: "carton", category: "lacteos", any: ["margarina"] },
  { slug: "queso-cheddar-200g", alt: "Packshot de queso cheddar", kind: "carton", category: "lacteos", any: ["cheddar"] },
  { slug: "queso-crema-190g", alt: "Packshot de queso crema", kind: "carton", category: "lacteos", any: ["queso crema"] },
  { slug: "queso-mozzarella-400g", alt: "Packshot de queso mozzarella", kind: "carton", category: "lacteos", any: ["mozzarella"] },
  { slug: "queso-oaxaca-400g", alt: "Packshot de queso oaxaca", kind: "carton", category: "lacteos", any: ["oaxaca"] },
  { slug: "queso-panela-400g", alt: "Packshot de queso panela", kind: "carton", category: "lacteos", any: ["panela"] },
  { slug: "queso-manchego-180g", alt: "Packshot de queso manchego", kind: "carton", category: "lacteos", any: ["manchego"] },
  { slug: "queso-cottage-300g", alt: "Packshot de queso cottage", kind: "carton", category: "lacteos", any: ["cottage"] },
  { slug: "agua-con-gas-burbuja-fina-600ml", alt: "Packshot de agua con gas", kind: "water", category: "bebidas", any: ["agua con gas", "burbuja", "topo chico"] },
  { slug: "agua-mineral-600ml", alt: "Packshot de agua mineral", kind: "water", category: "bebidas", any: ["agua mineral", "mineral"] },
  { slug: "agua-tonica-600ml", alt: "Packshot de agua tónica", kind: "water", category: "bebidas", any: ["agua tonica", "agua tónica"] },
  { slug: "agua-natural-600ml", alt: "Packshot de agua natural", kind: "water", category: "bebidas", any: ["agua natural"] },
  { slug: "agua-tonica-600ml", alt: "Packshot de agua tónica", kind: "water", category: "bebidas", any: ["agua tonica", "agua tónica", "tonica", "tónica"] },
  { slug: "agua-con-gas-burbuja-fina-600ml", alt: "Packshot de agua con gas", kind: "water", category: "bebidas", any: ["agua con gas", "con gas", "burbuja", "topo chico"] },
  { slug: "agua-mineral-600ml", alt: "Packshot de agua mineral", kind: "water", category: "bebidas", any: ["agua mineral", "mineral", "cristal"] },
  { slug: "agua-natural-600ml", alt: "Packshot de agua natural", kind: "water", category: "bebidas", any: ["agua natural", "bonafont", "natural 1", "natural 600"] },
  { slug: "agua-purificada-600ml", alt: "Packshot de agua purificada", kind: "water", category: "bebidas", any: ["agua", "ciel", "purificada"] },
  { slug: "refresco-de-limon-600ml", alt: "Packshot de refresco de limón", kind: "bottle", category: "bebidas", any: ["limon", "limón", "sprite", "7up"] },
  { slug: "refresco-de-naranja-600ml", alt: "Packshot de refresco de naranja", kind: "bottle", category: "bebidas", any: ["naranja", "fanta"] },
  { slug: "jugo-de-naranja-1l", alt: "Packshot de jugo de naranja", kind: "carton", category: "bebidas", any: ["jugo de naranja"] },
  { slug: "jugo-de-manzana-1l", alt: "Packshot de jugo de manzana", kind: "carton", category: "bebidas", any: ["jugo de manzana", "sidral"] },
  { slug: "jugo-de-uva-1l", alt: "Packshot de jugo de uva", kind: "carton", category: "bebidas", any: ["jugo de uva"] },
  { slug: "nectar-de-durazno-1l", alt: "Packshot de néctar de durazno", kind: "carton", category: "bebidas", any: ["durazno"] },
  { slug: "nectar-de-mango-1l", alt: "Packshot de néctar de mango", kind: "carton", category: "bebidas", any: ["mango"] },
  { slug: "nectar-de-guayaba-1l", alt: "Packshot de néctar de guayaba", kind: "carton", category: "bebidas", any: ["guayaba"] },
  { slug: "bebida-isotonica-600ml", alt: "Packshot de bebida isotónica", kind: "bottle", category: "bebidas", any: ["gatorade", "powerade", "isotonica", "isotónica"] },
  { slug: "bebida-energetica-energia-activa-355ml", alt: "Packshot de bebida energética", kind: "bottle", category: "bebidas", any: ["energetica", "energética", "energy", "monster", "red bull"] },
  { slug: "bebida-de-avena-1l", alt: "Packshot de bebida de avena", kind: "carton", category: "bebidas", any: ["bebida de avena"] },
  { slug: "bebida-de-almendra-1l", alt: "Packshot de bebida de almendra", kind: "carton", category: "bebidas", any: ["bebida de almendra", "almendra"] },
  { slug: "bebida-de-arroz-1l", alt: "Packshot de bebida de arroz", kind: "carton", category: "bebidas", any: ["bebida de arroz"] },
  { slug: "bebida-de-soya-1l", alt: "Packshot de bebida de soya", kind: "carton", category: "bebidas", any: ["bebida de soya", "soya"] },
  { slug: "detergente-multiusos-1kg", alt: "Packshot de detergente", kind: "bag", category: "limpieza", any: ["detergente", "ace 1kg", "ace "] },
  { slug: "lavatrastes-liquido-concentrado-750ml", alt: "Packshot de lavatrastes", kind: "bottle", category: "limpieza", any: ["lavatrastes", "salvo"] },
  { slug: "limpiador-multiusos-limpieza-profunda-750ml", alt: "Packshot de limpiador multiusos", kind: "bottle", category: "limpieza", any: ["limpiador", "fabuloso", "pinol", "multiusos"] },
  { slug: "blanqueador-liquido-hogar-1l", alt: "Packshot de blanqueador", kind: "bottle", category: "limpieza", any: ["blanqueador", "cloralex", "cloro"] },
  { slug: "suavizante-de-ropa-frescura-elegante-1-5l", alt: "Packshot de suavizante", kind: "bottle", category: "limpieza", any: ["suavizante", "suavitel"] },
  { slug: "shampoo-nutritivo-cabello-normal-750ml", alt: "Packshot de shampoo", kind: "bottle", category: "cuidado_personal", any: ["shampoo", "champu"] },
  { slug: "pasta-dental-menta-fresca-120g", alt: "Packshot de pasta dental", kind: "box", category: "cuidado_personal", any: ["pasta dental", "colgate"] },
  { slug: "jabon-de-barra-humectante-150g", alt: "Packshot de jabón de barra", kind: "box", category: "cuidado_personal", any: ["jabon", "jabón"] },
  { slug: "desodorante-spray-proteccion-150ml", alt: "Packshot de desodorante", kind: "bottle", category: "cuidado_personal", any: ["desodorante"] },
  { slug: "enjuague-bucal-menta-fresca-500ml", alt: "Packshot de enjuague bucal", kind: "bottle", category: "cuidado_personal", any: ["enjuague"] },
  { slug: "crema-corporal-hidratacion-profunda-750ml", alt: "Packshot de crema corporal", kind: "bottle", category: "cuidado_personal", any: ["crema corporal"] },
  { slug: "crema-para-manos-nutricion-intensa-75ml", alt: "Packshot de crema para manos", kind: "bottle", category: "cuidado_personal", any: ["crema para manos"] },
  { slug: "papel-higienico-suave-4-rollos", alt: "Packshot de papel higiénico", kind: "box", category: "papel_higienico", any: ["papel higienico", "papel higiénico"] },
  { slug: "croquetas-para-perro-adulto-2kg", alt: "Packshot de croquetas para perro", kind: "bag", category: "mascotas", any: ["perro", "croquetas", "pedigree", "dog chow"] },
  { slug: "alimento-para-gato-adulto-2kg", alt: "Packshot de alimento para gato", kind: "bag", category: "mascotas", any: ["gato", "whiskas"] }
];

function normalizeProductText(value: string | null | undefined) {
  return (value ?? "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();
}

function normalizeCategory(value: string | null | undefined) {
  return normalizeProductText(value)
    .replace(/\s+/g, "-")
    .replace(/[^a-z0-9_-]/g, "")
    .replace(/_+/g, "_")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
}

export function slugifyPackshot(value: string | null | undefined) {
  const normalized = normalizeProductText(value)
    .replace(/&/g, " y ")
    .replace(/\+/g, " mas ")
    .replace(/([0-9])\s+(ml|g|kg|l)\b/g, "$1$2")
    .replace(/([0-9])\.([0-9])\s*l\b/g, "$1-$2l")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");

  return normalized || "producto";
}

function unique(values: string[]) {
  return values.filter((value, index, list) => value && list.indexOf(value) === index);
}

function oppositeSkin(_skin: PrismaPackshotSkin): PrismaPackshotSkin {
  return "dark";
}

function normalizeSkin(_skin?: PrismaPackshotSkin | null): PrismaPackshotSkin {
  return "dark";
}

function fileToSlug(file: string) {
  return file.replace(/\.png$/i, "");
}

function skinPath(_skin: PrismaPackshotSkin, fileOrSlug: string) {
  const file = fileOrSlug.endsWith(".png") ? fileOrSlug : `${fileOrSlug}.png`;
  return `${SKIN_PRODUCT_BASE}/${file}`;
}

function legacyProductPath(file: string) {
  return `${LEGACY_PRODUCT_BASE}/${file}`;
}

function legacyGenericPath(file: string) {
  return `${LEGACY_GENERIC_BASE}/${file}`;
}

function skinFallbackSlugForCategory(category: string | null | undefined) {
  const normalized = normalizeCategory(category);
  return normalized ? CATEGORY_SKIN_FALLBACK_SLUGS[normalized] : null;
}

function makePackshot(rule: PackshotRule, skin: PrismaPackshotSkin, category: string | null | undefined, directSlug?: string): PosPackshot {
  const slug = rule.slug ?? fileToSlug(rule.file);
  const otherSkin = oppositeSkin(skin);
  const categoryKey = rule.category ?? normalizeCategory(category);
  const categoryFallback = categoryKey ? CATEGORY_FALLBACKS[categoryKey] : null;
  const categorySkinFallback = skinFallbackSlugForCategory(categoryKey);
  const genericFile = categoryFallback?.file ?? (POS_PACKSHOT_FILENAMES.includes(rule.file as LegacyGenericFile) ? (rule.file as LegacyGenericFile) : DEFAULT_FALLBACK_FILE);
  const legacySpecificSrc = rule.base === LEGACY_PRODUCT_BASE ? legacyProductPath(rule.file) : null;
  const legacyGenericSrc = legacyGenericPath(genericFile);
  const isLegacyGenericRule = !rule.slug && rule.base !== LEGACY_PRODUCT_BASE && POS_PACKSHOT_FILENAMES.includes(rule.file as LegacyGenericFile);

  const sources = isLegacyGenericRule
    ? unique([
        legacyGenericSrc,
        categorySkinFallback ? skinPath(skin, categorySkinFallback) : "",
        categorySkinFallback ? skinPath(otherSkin, categorySkinFallback) : "",
        legacyGenericPath(DEFAULT_FALLBACK_FILE)
      ])
    : unique([
        skinPath(skin, slug),
        skinPath(otherSkin, slug),
        directSlug && directSlug !== slug ? skinPath(skin, directSlug) : "",
        directSlug && directSlug !== slug ? skinPath(otherSkin, directSlug) : "",
        categorySkinFallback ? skinPath(skin, categorySkinFallback) : "",
        categorySkinFallback ? skinPath(otherSkin, categorySkinFallback) : "",
        legacySpecificSrc ?? "",
        legacyGenericSrc,
        legacyGenericPath(DEFAULT_FALLBACK_FILE)
      ]);

  return {
    src: sources[0],
    fallbackSrcs: sources.slice(1),
    alt: rule.alt,
    kind: rule.kind,
    skin,
    slug
  };
}

function includesAny(text: string, needles: string[]) {
  return needles.some((needle) => text.includes(normalizeProductText(needle)));
}

function includesAll(text: string, needles: string[] | undefined) {
  return !needles || needles.every((needle) => text.includes(normalizeProductText(needle)));
}

function includesNone(text: string, needles: string[] | undefined) {
  return !needles || needles.every((needle) => !text.includes(normalizeProductText(needle)));
}

function ruleFromGeneratedAliases(text: string): PackshotRule | null {
  const rule = GENERATED_PRODUCT_RULES.find((candidate) => includesAny(text, candidate.any) && includesAll(text, candidate.all) && includesNone(text, candidate.not));

  if (!rule) {
    return null;
  }

  return {
    slug: rule.slug,
    file: `${rule.slug}.png`,
    alt: rule.alt,
    kind: rule.kind,
    category: rule.category
  };
}

function ruleFromLegacySpecificProductText(text: string): PackshotRule | null {
  if (includesAny(text, ["coca cola 600", "coca-cola-600", "coca 600"])) {
    return { file: "coca-cola-600ml.png", alt: "Packshot de Coca Cola 600 ml", kind: "bottle", base: LEGACY_PRODUCT_BASE };
  }

  if (includesAny(text, ["sabritas original 45", "sabritas-original-45", "sabritas 45"])) {
    return { file: "sabritas-original-45g.png", alt: "Packshot de Sabritas Original 45 g", kind: "bag", base: LEGACY_PRODUCT_BASE };
  }

  if (includesAny(text, ["leche lala entera 1", "lala entera 1", "lala 1l"])) {
    return { file: "leche-lala-entera-1l.png", alt: "Packshot de Leche Lala Entera 1 L", kind: "carton", base: LEGACY_PRODUCT_BASE };
  }

  if (includesAny(text, ["agua ciel 1", "ciel 1l", "agua-ciel-1l"])) {
    return { file: "agua-ciel-1l.png", alt: "Packshot de Agua Ciel 1 L", kind: "water", base: LEGACY_PRODUCT_BASE };
  }

  if (includesAny(text, ["nescafe clasico 200", "nescafe-clasico-200", "nescafe 200"])) {
    return { file: "nescafe-clasico-200g.png", alt: "Packshot de Nescafé Clásico 200 g", kind: "jar", base: LEGACY_PRODUCT_BASE };
  }

  if (includesAny(text, ["pan bimbo blanco grande", "bimbo blanco grande", "pan-bimbo-blanco-grande"])) {
    return { file: "pan-bimbo-blanco-grande.png", alt: "Packshot de Pan Bimbo Blanco Grande", kind: "bread", base: LEGACY_PRODUCT_BASE };
  }

  if (includesAny(text, ["ace 1", "ace-1kg", "detergente ace"])) {
    return { file: "ace-1kg.png", alt: "Packshot de Ace 1 kg", kind: "box", base: LEGACY_PRODUCT_BASE };
  }

  if (includesAny(text, ["zucaritas kelloggs 730", "zucaritas kellogg", "zucaritas-kelloggs-730"])) {
    return { file: "zucaritas-kelloggs-730g.png", alt: "Packshot de Zucaritas Kellogg's 730 g", kind: "box", base: LEGACY_PRODUCT_BASE };
  }

  return null;
}

function ruleFromGenericCategoryText(text: string): PackshotRule | null {
  if (includesAny(text, ["agua", "bonafont", "ciel", "cristal", "mineral", "topo chico"])) {
    return { file: "water_bottle_512.png", alt: "Packshot genérico de agua", kind: "water", category: "bebidas" };
  }

  if (includesAny(text, ["coca", "cola", "sprite", "fanta", "sidral", "manzanita", "penafiel", "powerade", "gatorade", "electrolit", "fuze", "refresco"])) {
    return { file: "cola_bottle_512.png", alt: "Packshot genérico de bebida", kind: "bottle", category: "bebidas" };
  }

  if (includesAny(text, ["sabritas", "paketaxo", "tostitos", "doritos", "cheetos", "ruffles", "churrumais", "takis", "barcel", "kiyakis", "cacahuates", "palomitas", "botana"])) {
    return { file: "chips_bag_512.png", alt: "Packshot genérico de botana", kind: "bag", category: "botanas" };
  }

  if (includesAny(text, ["leche", "yoghurt", "yogurt", "yakult", "crema", "almendra", "jugo", "jumex", "boing", "nectar"])) {
    return { file: "milk_carton_512.png", alt: "Packshot genérico de lácteo o jugo", kind: "carton", category: "lacteos" };
  }

  if (includesAny(text, ["pan", "bimbo", "doners", "mantecadas", "nito", "pinguinos", "gansito", "canelitas", "barritas"])) {
    return { file: "bread_loaf_512.png", alt: "Packshot genérico de panadería", kind: "bread", category: "panaderia" };
  }

  if (includesAny(text, ["atun", "frijoles", "chiles", "elote", "mayonesa", "salsa", "cafe", "nescafe", "mccormick", "costena", "herdez"])) {
    return { file: "coffee_jar_512.png", alt: "Packshot genérico de frasco o conserva", kind: "jar", category: "abarrotes" };
  }

  if (includesAny(text, ["maruchan", "sopa instantanea", "sopa "])) {
    return { file: "noodles_cup_512.png", alt: "Packshot genérico de sopa instantánea", kind: "jar", category: "abarrotes" };
  }

  if (includesAny(text, ["zucaritas", "corn flakes", "choco krispis", "froot loops", "granola", "cereal", "fitness"])) {
    return { file: "cereal_box_512.png", alt: "Packshot genérico de cereal", kind: "box", category: "cereales" };
  }

  if (includesAny(text, ["trident", "clorets", "halls", "carlos v", "snickers", "hershey", "mazapan", "pelon", "paleta", "duvalin", "kinder", "m&m", "dulce", "chocolate", "gomita", "gomitas"])) {
    return { file: "candy_bar_512.png", alt: "Packshot genérico de dulce", kind: "box", category: "dulces" };
  }

  if (includesAny(text, ["detergente", "fabuloso", "cloralex", "pinol", "salvo", "zote", "suavitel", "escoba", "fibra", "basura", "aluminio", "limpieza"])) {
    return { file: "detergent_bag_512.png", alt: "Packshot genérico de limpieza", kind: "bag", category: "limpieza" };
  }

  if (includesAny(text, ["papel higienico", "pasta", "cepillo", "jabon", "shampoo", "desodorante", "toallas femeninas", "panuelos", "gel antibacterial", "higiene"])) {
    return { file: "hygiene_bottle_512.png", alt: "Packshot genérico de higiene", kind: "bottle", category: "higiene" };
  }

  if (includesAny(text, ["croquetas", "whiskas", "pedigree", "dog chow", "arena para gato", "premios para perro", "mascota"])) {
    return { file: "pet_food_bag_512.png", alt: "Packshot genérico de mascotas", kind: "bag", category: "mascotas" };
  }

  if (includesAny(text, ["vaso desechable", "plato desechable", "servilletas", "popotes", "desechable"])) {
    return { file: "disposables_stack_512.png", alt: "Packshot genérico de desechables", kind: "box", category: "desechables" };
  }

  if (includesAny(text, ["hielo", "paleta holanda", "magnum", "helado", "congelado"])) {
    return { file: "icecream_bar_512.png", alt: "Packshot genérico de congelado", kind: "carton", category: "congelados" };
  }

  if (includesAny(text, ["encendedor", "cerillos", "pilas", "cubrebocas", "mostrador"])) {
    return { file: "counter_goods_512.png", alt: "Packshot genérico de mostrador", kind: "box", category: "mostrador" };
  }

  if (includesAny(text, ["arroz", "azucar", "sal", "pasta", "spaghetti", "harina"])) {
    return { file: "cereal_box_512.png", alt: "Packshot genérico de abarrotes secos", kind: "box", category: "abarrotes" };
  }

  return null;
}

function ruleFromGeneratedSlug(name: string, category: string | null | undefined): PackshotRule {
  const slug = slugifyPackshot(name);
  const categoryKey = normalizeCategory(category);
  const categoryRule = categoryKey ? CATEGORY_FALLBACKS[categoryKey] : null;

  return {
    slug,
    file: `${slug}.png`,
    alt: `Packshot de ${name}`,
    kind: categoryRule?.kind ?? "box",
    category: categoryKey || undefined
  };
}

export function resolveProductPackshot(
  name: string,
  category?: string | null,
  sku?: string | null,
  options: ResolveOptions = {}
): PosPackshot | null {
  const skin = normalizeSkin(options.skin);
  const text = normalizeProductText(`${name} ${sku ?? ""}`);
  const directSlug = slugifyPackshot(name);
  const rule =
    ruleFromGeneratedAliases(text) ??
    ruleFromGenericCategoryText(text) ??
    ruleFromGeneratedSlug(name, category);

  return makePackshot(rule, skin, category, directSlug);
}

export function resolveNextPackshotSrc(currentSrc: string, fallbackSrcs: string[]) {
  const currentPath = safePathname(currentSrc);
  const currentIndex = fallbackSrcs.findIndex((src) => safePathname(src) === currentPath || src === currentSrc);
  return fallbackSrcs[currentIndex + 1] ?? null;
}

function safePathname(value: string) {
  try {
    return new URL(value, "https://prisma.local").pathname;
  } catch {
    return value;
  }
}
