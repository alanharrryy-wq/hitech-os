export const projectIterationIndex = [
  {
    "id": "pc_i01",
    "scope": "gobierno base, glosario es-MX, rutas /gobierno y /glosario",
    "routes": [
      "/gobierno",
      "/glosario"
    ],
    "depends_on": [
      "PC_TWIN_CHAT_PACK_6.1.1.zip"
    ],
    "replaces_files": false
  },
  {
    "id": "pc_i02",
    "scope": "catalogo y stock, rutas /catalogo-activo /existencias-criticas /salud-barcodes",
    "routes": [
      "/catalogo-activo",
      "/existencias-criticas",
      "/salud-barcodes"
    ],
    "depends_on": [
      "pc_i01.zip"
    ],
    "replaces_files": false
  },
  {
    "id": "pc_i03",
    "scope": "conteos, auditoria, ajustes, indice acumulativo",
    "routes": [
      "/conteos-operativos",
      "/auditoria-inventario",
      "/ajustes-inventario"
    ],
    "depends_on": [
      "pc_i02.zip"
    ],
    "replaces_files": false
  }
] as const;

export const ajustesResumen = [
  {
    "location": "A-01",
    "category": "Bebidas",
    "eventos": 2000,
    "unidades": 12006
  },
  {
    "location": "RACK-2",
    "category": "Farmacia",
    "eventos": 2000,
    "unidades": 12001
  },
  {
    "location": "A-03",
    "category": "Lácteos",
    "eventos": 2000,
    "unidades": 12000
  },
  {
    "location": "B-02",
    "category": "Limpieza",
    "eventos": 2000,
    "unidades": 11998
  },
  {
    "location": "C-06",
    "category": "Snacks",
    "eventos": 2000,
    "unidades": 11992
  }
] as const;
