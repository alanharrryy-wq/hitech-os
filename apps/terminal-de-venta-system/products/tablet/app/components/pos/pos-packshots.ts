export type PosPackshotKind = "bottle" | "water" | "bag" | "carton" | "bread" | "jar" | "box";

export type PosPackshot = {
  src: string;
  alt: string;
  kind: PosPackshotKind;
};

/* PRISMA_TABLET_PRODUCT_PACKSHOTS_04J
 * Public asset contract:
 *   products/tablet/app/public/pos-packshots/*.png -> /pos-packshots/*.png
 * This file is the only product-name-to-packshot resolver for /pos cards and ticket thumbnails.
 * Assets are PRISMA-owned generic packshot illustrations, not official brand art.
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

const PACKSHOT_BASE = "/pos-packshots";
const PRODUCT_PACKSHOT_BASE = "/products/packshots";

type PackshotFile = (typeof POS_PACKSHOT_FILENAMES)[number];

type PackshotRule = {
  file: PackshotFile | string;
  alt: string;
  kind: PosPackshotKind;
  base?: string;
};

function normalizeProductText(value: string | null | undefined) {
  return (value ?? "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}

function makePackshot(rule: PackshotRule): PosPackshot {
  return { src: `${rule.base ?? PACKSHOT_BASE}/${rule.file}`, alt: rule.alt, kind: rule.kind };
}

function includesAny(text: string, needles: string[]) {
  return needles.some((needle) => text.includes(needle));
}

function ruleFromProductText(text: string): PackshotRule | null {
  if (includesAny(text, ["coca cola 600", "coca-cola-600", "coca 600"])) {
    return { file: "coca-cola-600ml.png", alt: "Packshot de Coca Cola 600 ml", kind: "bottle", base: PRODUCT_PACKSHOT_BASE };
  }

  if (includesAny(text, ["sabritas original 45", "sabritas-original-45", "sabritas 45"])) {
    return { file: "sabritas-original-45g.png", alt: "Packshot de Sabritas Original 45 g", kind: "bag", base: PRODUCT_PACKSHOT_BASE };
  }

  if (includesAny(text, ["leche lala entera 1", "lala entera 1", "lala 1l"])) {
    return { file: "leche-lala-entera-1l.png", alt: "Packshot de Leche Lala Entera 1 L", kind: "carton", base: PRODUCT_PACKSHOT_BASE };
  }

  if (includesAny(text, ["agua ciel 1", "ciel 1l", "agua-ciel-1l"])) {
    return { file: "agua-ciel-1l.png", alt: "Packshot de Agua Ciel 1 L", kind: "water", base: PRODUCT_PACKSHOT_BASE };
  }

  if (includesAny(text, ["nescafe clasico 200", "nescafe-clasico-200", "nescafe 200"])) {
    return { file: "nescafe-clasico-200g.png", alt: "Packshot de Nescafe Clasico 200 g", kind: "jar", base: PRODUCT_PACKSHOT_BASE };
  }

  if (includesAny(text, ["pan bimbo blanco grande", "bimbo blanco grande", "pan-bimbo-blanco-grande"])) {
    return { file: "pan-bimbo-blanco-grande.png", alt: "Packshot de Pan Bimbo Blanco Grande", kind: "bread", base: PRODUCT_PACKSHOT_BASE };
  }

  if (includesAny(text, ["ace 1", "ace-1kg", "detergente ace"])) {
    return { file: "ace-1kg.png", alt: "Packshot de Ace 1 kg", kind: "box", base: PRODUCT_PACKSHOT_BASE };
  }

  if (includesAny(text, ["zucaritas kelloggs 730", "zucaritas kellogg", "zucaritas-kelloggs-730"])) {
    return { file: "zucaritas-kelloggs-730g.png", alt: "Packshot de Zucaritas Kelloggs 730 g", kind: "box", base: PRODUCT_PACKSHOT_BASE };
  }

  if (includesAny(text, ["agua", "bonafont", "ciel", "cristal", "mineral", "topo chico"])) {
    return { file: "water_bottle_512.png", alt: "Packshot genérico de agua", kind: "water" };
  }

  if (includesAny(text, ["coca", "cola", "sprite", "fanta", "sidral", "manzanita", "penafiel", "powerade", "gatorade", "electrolit", "fuze", "refresco"])) {
    return { file: "cola_bottle_512.png", alt: "Packshot genérico de bebida", kind: "bottle" };
  }

  if (includesAny(text, ["sabritas", "paketaxo", "tostitos", "doritos", "cheetos", "ruffles", "churrumais", "takis", "barcel", "kiyakis", "cacahuates", "palomitas", "botana"])) {
    return { file: "chips_bag_512.png", alt: "Packshot genérico de botana", kind: "bag" };
  }

  if (includesAny(text, ["leche", "yoghurt", "yogurt", "yakult", "crema", "almendra", "jugo", "jumex", "boing", "nectar"])) {
    return { file: "milk_carton_512.png", alt: "Packshot genérico de lácteo o jugo", kind: "carton" };
  }

  if (includesAny(text, ["pan", "bimbo", "doners", "mantecadas", "nito", "pinguinos", "gansito", "canelitas", "barritas"])) {
    return { file: "bread_loaf_512.png", alt: "Packshot genérico de panadería", kind: "bread" };
  }

  if (includesAny(text, ["atun", "frijoles", "chiles", "elote", "mayonesa", "salsa", "cafe", "nescafe", "mccormick", "costena", "herdez"])) {
    return { file: "coffee_jar_512.png", alt: "Packshot genérico de frasco o conserva", kind: "jar" };
  }

  if (includesAny(text, ["maruchan", "sopa instantanea", "sopa "])) {
    return { file: "noodles_cup_512.png", alt: "Packshot genérico de sopa instantánea", kind: "jar" };
  }

  if (includesAny(text, ["zucaritas", "corn flakes", "choco krispis", "froot loops", "granola", "cereal", "fitness"])) {
    return { file: "cereal_box_512.png", alt: "Packshot genérico de cereal", kind: "box" };
  }

  if (includesAny(text, ["trident", "clorets", "halls", "carlos v", "snickers", "hershey", "mazapan", "pelon", "paleta", "duvalin", "kinder", "m&m", "dulce", "chocolate"])) {
    return { file: "candy_bar_512.png", alt: "Packshot genérico de dulce", kind: "box" };
  }

  if (includesAny(text, ["detergente", "fabuloso", "cloralex", "pinol", "salvo", "zote", "suavitel", "escoba", "fibra", "basura", "aluminio", "limpieza"])) {
    return { file: "detergent_bag_512.png", alt: "Packshot genérico de limpieza", kind: "bag" };
  }

  if (includesAny(text, ["papel higienico", "pasta", "cepillo", "jabon", "shampoo", "desodorante", "toallas femeninas", "panuelos", "gel antibacterial", "higiene"])) {
    return { file: "hygiene_bottle_512.png", alt: "Packshot genérico de higiene", kind: "bottle" };
  }

  if (includesAny(text, ["croquetas", "whiskas", "pedigree", "dog chow", "arena para gato", "premios para perro", "mascota"])) {
    return { file: "pet_food_bag_512.png", alt: "Packshot genérico de mascotas", kind: "bag" };
  }

  if (includesAny(text, ["vaso desechable", "plato desechable", "servilletas", "popotes", "desechable"])) {
    return { file: "disposables_stack_512.png", alt: "Packshot genérico de desechables", kind: "box" };
  }

  if (includesAny(text, ["hielo", "paleta holanda", "magnum", "helado", "congelado"])) {
    return { file: "icecream_bar_512.png", alt: "Packshot genérico de congelado", kind: "carton" };
  }

  if (includesAny(text, ["encendedor", "cerillos", "pilas", "cubrebocas", "mostrador"])) {
    return { file: "counter_goods_512.png", alt: "Packshot genérico de mostrador", kind: "box" };
  }

  if (includesAny(text, ["arroz", "azucar", "sal", "pasta", "spaghetti", "harina"])) {
    return { file: "cereal_box_512.png", alt: "Packshot genérico de abarrotes secos", kind: "box" };
  }

  return null;
}

function ruleFromCategory(category: string): PackshotRule | null {
  switch (category) {
    case "bebidas":
      return { file: "cola_bottle_512.png", alt: "Packshot genérico de bebida", kind: "bottle" };
    case "botanas":
      return { file: "chips_bag_512.png", alt: "Packshot genérico de botana", kind: "bag" };
    case "lacteos":
      return { file: "milk_carton_512.png", alt: "Packshot genérico de lácteo", kind: "carton" };
    case "panaderia":
      return { file: "bread_loaf_512.png", alt: "Packshot genérico de panadería", kind: "bread" };
    case "abarrotes":
      return { file: "coffee_jar_512.png", alt: "Packshot genérico de abarrote", kind: "jar" };
    case "cereales":
      return { file: "cereal_box_512.png", alt: "Packshot genérico de cereal", kind: "box" };
    case "dulces":
      return { file: "candy_bar_512.png", alt: "Packshot genérico de dulce", kind: "box" };
    case "limpieza":
      return { file: "detergent_bag_512.png", alt: "Packshot genérico de limpieza", kind: "bag" };
    case "higiene":
      return { file: "hygiene_bottle_512.png", alt: "Packshot genérico de higiene", kind: "bottle" };
    case "mascotas":
      return { file: "pet_food_bag_512.png", alt: "Packshot genérico de mascotas", kind: "bag" };
    case "desechables":
      return { file: "disposables_stack_512.png", alt: "Packshot genérico de desechables", kind: "box" };
    case "mostrador":
      return { file: "counter_goods_512.png", alt: "Packshot genérico de mostrador", kind: "box" };
    case "congelados":
      return { file: "icecream_bar_512.png", alt: "Packshot genérico de congelado", kind: "carton" };
    default:
      return null;
  }
}

export function resolveProductPackshot(name: string, category?: string | null, sku?: string | null): PosPackshot | null {
  const text = normalizeProductText(`${name} ${sku ?? ""}`);
  const normalizedCategory = normalizeProductText(category);

  return makePackshot(
    ruleFromProductText(text) ??
      ruleFromCategory(normalizedCategory) ??
      { file: "cereal_box_512.png", alt: "Packshot genérico de producto", kind: "box" }
  );
}
