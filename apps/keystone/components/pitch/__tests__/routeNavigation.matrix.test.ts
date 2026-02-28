import { describe, expect, it } from 'vitest';
import { selectRouteNavigation } from '../../../lib/pitch';

type RouteId = 'pitch-index' | '01-double-engine' | '02-industrial-flow' | '03-hitech-os' | '04-valuation';

interface NavCase {
  readonly id: string;
  readonly routeId: RouteId;
  readonly query: {
    readonly layers: string;
    readonly layerProfile: 'neutral' | 'fx' | 'perf';
    readonly debug: '0' | '1';
  };
  readonly expectPrev: RouteId | null;
  readonly expectNext: RouteId | null;
}

const cases: ReadonlyArray<NavCase> = [
  {
    id: 'nav-0001',
    routeId: 'pitch-index',
    query: {
      layers: 'all',
      layerProfile: 'neutral',
      debug: '0',
    },
    expectPrev: null,
    expectNext: '01-double-engine',
  },
  {
    id: 'nav-0002',
    routeId: 'pitch-index',
    query: {
      layers: 'all',
      layerProfile: 'neutral',
      debug: '1',
    },
    expectPrev: null,
    expectNext: '01-double-engine',
  },
  {
    id: 'nav-0003',
    routeId: 'pitch-index',
    query: {
      layers: 'none',
      layerProfile: 'neutral',
      debug: '0',
    },
    expectPrev: null,
    expectNext: '01-double-engine',
  },
  {
    id: 'nav-0004',
    routeId: 'pitch-index',
    query: {
      layers: 'none',
      layerProfile: 'neutral',
      debug: '1',
    },
    expectPrev: null,
    expectNext: '01-double-engine',
  },
  {
    id: 'nav-0005',
    routeId: 'pitch-index',
    query: {
      layers: 'list',
      layerProfile: 'neutral',
      debug: '0',
    },
    expectPrev: null,
    expectNext: '01-double-engine',
  },
  {
    id: 'nav-0006',
    routeId: 'pitch-index',
    query: {
      layers: 'list',
      layerProfile: 'neutral',
      debug: '1',
    },
    expectPrev: null,
    expectNext: '01-double-engine',
  },
  {
    id: 'nav-0007',
    routeId: 'pitch-index',
    query: {
      layers: 'surfaceBase,chartGrid',
      layerProfile: 'neutral',
      debug: '0',
    },
    expectPrev: null,
    expectNext: '01-double-engine',
  },
  {
    id: 'nav-0008',
    routeId: 'pitch-index',
    query: {
      layers: 'surfaceBase,chartGrid',
      layerProfile: 'neutral',
      debug: '1',
    },
    expectPrev: null,
    expectNext: '01-double-engine',
  },
  {
    id: 'nav-0009',
    routeId: 'pitch-index',
    query: {
      layers: 'surfaceBase,glassTint',
      layerProfile: 'neutral',
      debug: '0',
    },
    expectPrev: null,
    expectNext: '01-double-engine',
  },
  {
    id: 'nav-0010',
    routeId: 'pitch-index',
    query: {
      layers: 'surfaceBase,glassTint',
      layerProfile: 'neutral',
      debug: '1',
    },
    expectPrev: null,
    expectNext: '01-double-engine',
  },
  {
    id: 'nav-0011',
    routeId: 'pitch-index',
    query: {
      layers: 'all',
      layerProfile: 'fx',
      debug: '0',
    },
    expectPrev: null,
    expectNext: '01-double-engine',
  },
  {
    id: 'nav-0012',
    routeId: 'pitch-index',
    query: {
      layers: 'all',
      layerProfile: 'fx',
      debug: '1',
    },
    expectPrev: null,
    expectNext: '01-double-engine',
  },
  {
    id: 'nav-0013',
    routeId: 'pitch-index',
    query: {
      layers: 'none',
      layerProfile: 'fx',
      debug: '0',
    },
    expectPrev: null,
    expectNext: '01-double-engine',
  },
  {
    id: 'nav-0014',
    routeId: 'pitch-index',
    query: {
      layers: 'none',
      layerProfile: 'fx',
      debug: '1',
    },
    expectPrev: null,
    expectNext: '01-double-engine',
  },
  {
    id: 'nav-0015',
    routeId: 'pitch-index',
    query: {
      layers: 'list',
      layerProfile: 'fx',
      debug: '0',
    },
    expectPrev: null,
    expectNext: '01-double-engine',
  },
  {
    id: 'nav-0016',
    routeId: 'pitch-index',
    query: {
      layers: 'list',
      layerProfile: 'fx',
      debug: '1',
    },
    expectPrev: null,
    expectNext: '01-double-engine',
  },
  {
    id: 'nav-0017',
    routeId: 'pitch-index',
    query: {
      layers: 'surfaceBase,chartGrid',
      layerProfile: 'fx',
      debug: '0',
    },
    expectPrev: null,
    expectNext: '01-double-engine',
  },
  {
    id: 'nav-0018',
    routeId: 'pitch-index',
    query: {
      layers: 'surfaceBase,chartGrid',
      layerProfile: 'fx',
      debug: '1',
    },
    expectPrev: null,
    expectNext: '01-double-engine',
  },
  {
    id: 'nav-0019',
    routeId: 'pitch-index',
    query: {
      layers: 'surfaceBase,glassTint',
      layerProfile: 'fx',
      debug: '0',
    },
    expectPrev: null,
    expectNext: '01-double-engine',
  },
  {
    id: 'nav-0020',
    routeId: 'pitch-index',
    query: {
      layers: 'surfaceBase,glassTint',
      layerProfile: 'fx',
      debug: '1',
    },
    expectPrev: null,
    expectNext: '01-double-engine',
  },
  {
    id: 'nav-0021',
    routeId: 'pitch-index',
    query: {
      layers: 'all',
      layerProfile: 'perf',
      debug: '0',
    },
    expectPrev: null,
    expectNext: '01-double-engine',
  },
  {
    id: 'nav-0022',
    routeId: 'pitch-index',
    query: {
      layers: 'all',
      layerProfile: 'perf',
      debug: '1',
    },
    expectPrev: null,
    expectNext: '01-double-engine',
  },
  {
    id: 'nav-0023',
    routeId: 'pitch-index',
    query: {
      layers: 'none',
      layerProfile: 'perf',
      debug: '0',
    },
    expectPrev: null,
    expectNext: '01-double-engine',
  },
  {
    id: 'nav-0024',
    routeId: 'pitch-index',
    query: {
      layers: 'none',
      layerProfile: 'perf',
      debug: '1',
    },
    expectPrev: null,
    expectNext: '01-double-engine',
  },
  {
    id: 'nav-0025',
    routeId: 'pitch-index',
    query: {
      layers: 'list',
      layerProfile: 'perf',
      debug: '0',
    },
    expectPrev: null,
    expectNext: '01-double-engine',
  },
  {
    id: 'nav-0026',
    routeId: 'pitch-index',
    query: {
      layers: 'list',
      layerProfile: 'perf',
      debug: '1',
    },
    expectPrev: null,
    expectNext: '01-double-engine',
  },
  {
    id: 'nav-0027',
    routeId: 'pitch-index',
    query: {
      layers: 'surfaceBase,chartGrid',
      layerProfile: 'perf',
      debug: '0',
    },
    expectPrev: null,
    expectNext: '01-double-engine',
  },
  {
    id: 'nav-0028',
    routeId: 'pitch-index',
    query: {
      layers: 'surfaceBase,chartGrid',
      layerProfile: 'perf',
      debug: '1',
    },
    expectPrev: null,
    expectNext: '01-double-engine',
  },
  {
    id: 'nav-0029',
    routeId: 'pitch-index',
    query: {
      layers: 'surfaceBase,glassTint',
      layerProfile: 'perf',
      debug: '0',
    },
    expectPrev: null,
    expectNext: '01-double-engine',
  },
  {
    id: 'nav-0030',
    routeId: 'pitch-index',
    query: {
      layers: 'surfaceBase,glassTint',
      layerProfile: 'perf',
      debug: '1',
    },
    expectPrev: null,
    expectNext: '01-double-engine',
  },
  {
    id: 'nav-0031',
    routeId: '01-double-engine',
    query: {
      layers: 'all',
      layerProfile: 'neutral',
      debug: '0',
    },
    expectPrev: 'pitch-index',
    expectNext: '02-industrial-flow',
  },
  {
    id: 'nav-0032',
    routeId: '01-double-engine',
    query: {
      layers: 'all',
      layerProfile: 'neutral',
      debug: '1',
    },
    expectPrev: 'pitch-index',
    expectNext: '02-industrial-flow',
  },
  {
    id: 'nav-0033',
    routeId: '01-double-engine',
    query: {
      layers: 'none',
      layerProfile: 'neutral',
      debug: '0',
    },
    expectPrev: 'pitch-index',
    expectNext: '02-industrial-flow',
  },
  {
    id: 'nav-0034',
    routeId: '01-double-engine',
    query: {
      layers: 'none',
      layerProfile: 'neutral',
      debug: '1',
    },
    expectPrev: 'pitch-index',
    expectNext: '02-industrial-flow',
  },
  {
    id: 'nav-0035',
    routeId: '01-double-engine',
    query: {
      layers: 'list',
      layerProfile: 'neutral',
      debug: '0',
    },
    expectPrev: 'pitch-index',
    expectNext: '02-industrial-flow',
  },
  {
    id: 'nav-0036',
    routeId: '01-double-engine',
    query: {
      layers: 'list',
      layerProfile: 'neutral',
      debug: '1',
    },
    expectPrev: 'pitch-index',
    expectNext: '02-industrial-flow',
  },
  {
    id: 'nav-0037',
    routeId: '01-double-engine',
    query: {
      layers: 'surfaceBase,chartGrid',
      layerProfile: 'neutral',
      debug: '0',
    },
    expectPrev: 'pitch-index',
    expectNext: '02-industrial-flow',
  },
  {
    id: 'nav-0038',
    routeId: '01-double-engine',
    query: {
      layers: 'surfaceBase,chartGrid',
      layerProfile: 'neutral',
      debug: '1',
    },
    expectPrev: 'pitch-index',
    expectNext: '02-industrial-flow',
  },
  {
    id: 'nav-0039',
    routeId: '01-double-engine',
    query: {
      layers: 'surfaceBase,glassTint',
      layerProfile: 'neutral',
      debug: '0',
    },
    expectPrev: 'pitch-index',
    expectNext: '02-industrial-flow',
  },
  {
    id: 'nav-0040',
    routeId: '01-double-engine',
    query: {
      layers: 'surfaceBase,glassTint',
      layerProfile: 'neutral',
      debug: '1',
    },
    expectPrev: 'pitch-index',
    expectNext: '02-industrial-flow',
  },
  {
    id: 'nav-0041',
    routeId: '01-double-engine',
    query: {
      layers: 'all',
      layerProfile: 'fx',
      debug: '0',
    },
    expectPrev: 'pitch-index',
    expectNext: '02-industrial-flow',
  },
  {
    id: 'nav-0042',
    routeId: '01-double-engine',
    query: {
      layers: 'all',
      layerProfile: 'fx',
      debug: '1',
    },
    expectPrev: 'pitch-index',
    expectNext: '02-industrial-flow',
  },
  {
    id: 'nav-0043',
    routeId: '01-double-engine',
    query: {
      layers: 'none',
      layerProfile: 'fx',
      debug: '0',
    },
    expectPrev: 'pitch-index',
    expectNext: '02-industrial-flow',
  },
  {
    id: 'nav-0044',
    routeId: '01-double-engine',
    query: {
      layers: 'none',
      layerProfile: 'fx',
      debug: '1',
    },
    expectPrev: 'pitch-index',
    expectNext: '02-industrial-flow',
  },
  {
    id: 'nav-0045',
    routeId: '01-double-engine',
    query: {
      layers: 'list',
      layerProfile: 'fx',
      debug: '0',
    },
    expectPrev: 'pitch-index',
    expectNext: '02-industrial-flow',
  },
  {
    id: 'nav-0046',
    routeId: '01-double-engine',
    query: {
      layers: 'list',
      layerProfile: 'fx',
      debug: '1',
    },
    expectPrev: 'pitch-index',
    expectNext: '02-industrial-flow',
  },
  {
    id: 'nav-0047',
    routeId: '01-double-engine',
    query: {
      layers: 'surfaceBase,chartGrid',
      layerProfile: 'fx',
      debug: '0',
    },
    expectPrev: 'pitch-index',
    expectNext: '02-industrial-flow',
  },
  {
    id: 'nav-0048',
    routeId: '01-double-engine',
    query: {
      layers: 'surfaceBase,chartGrid',
      layerProfile: 'fx',
      debug: '1',
    },
    expectPrev: 'pitch-index',
    expectNext: '02-industrial-flow',
  },
  {
    id: 'nav-0049',
    routeId: '01-double-engine',
    query: {
      layers: 'surfaceBase,glassTint',
      layerProfile: 'fx',
      debug: '0',
    },
    expectPrev: 'pitch-index',
    expectNext: '02-industrial-flow',
  },
  {
    id: 'nav-0050',
    routeId: '01-double-engine',
    query: {
      layers: 'surfaceBase,glassTint',
      layerProfile: 'fx',
      debug: '1',
    },
    expectPrev: 'pitch-index',
    expectNext: '02-industrial-flow',
  },
  {
    id: 'nav-0051',
    routeId: '01-double-engine',
    query: {
      layers: 'all',
      layerProfile: 'perf',
      debug: '0',
    },
    expectPrev: 'pitch-index',
    expectNext: '02-industrial-flow',
  },
  {
    id: 'nav-0052',
    routeId: '01-double-engine',
    query: {
      layers: 'all',
      layerProfile: 'perf',
      debug: '1',
    },
    expectPrev: 'pitch-index',
    expectNext: '02-industrial-flow',
  },
  {
    id: 'nav-0053',
    routeId: '01-double-engine',
    query: {
      layers: 'none',
      layerProfile: 'perf',
      debug: '0',
    },
    expectPrev: 'pitch-index',
    expectNext: '02-industrial-flow',
  },
  {
    id: 'nav-0054',
    routeId: '01-double-engine',
    query: {
      layers: 'none',
      layerProfile: 'perf',
      debug: '1',
    },
    expectPrev: 'pitch-index',
    expectNext: '02-industrial-flow',
  },
  {
    id: 'nav-0055',
    routeId: '01-double-engine',
    query: {
      layers: 'list',
      layerProfile: 'perf',
      debug: '0',
    },
    expectPrev: 'pitch-index',
    expectNext: '02-industrial-flow',
  },
  {
    id: 'nav-0056',
    routeId: '01-double-engine',
    query: {
      layers: 'list',
      layerProfile: 'perf',
      debug: '1',
    },
    expectPrev: 'pitch-index',
    expectNext: '02-industrial-flow',
  },
  {
    id: 'nav-0057',
    routeId: '01-double-engine',
    query: {
      layers: 'surfaceBase,chartGrid',
      layerProfile: 'perf',
      debug: '0',
    },
    expectPrev: 'pitch-index',
    expectNext: '02-industrial-flow',
  },
  {
    id: 'nav-0058',
    routeId: '01-double-engine',
    query: {
      layers: 'surfaceBase,chartGrid',
      layerProfile: 'perf',
      debug: '1',
    },
    expectPrev: 'pitch-index',
    expectNext: '02-industrial-flow',
  },
  {
    id: 'nav-0059',
    routeId: '01-double-engine',
    query: {
      layers: 'surfaceBase,glassTint',
      layerProfile: 'perf',
      debug: '0',
    },
    expectPrev: 'pitch-index',
    expectNext: '02-industrial-flow',
  },
  {
    id: 'nav-0060',
    routeId: '01-double-engine',
    query: {
      layers: 'surfaceBase,glassTint',
      layerProfile: 'perf',
      debug: '1',
    },
    expectPrev: 'pitch-index',
    expectNext: '02-industrial-flow',
  },
  {
    id: 'nav-0061',
    routeId: '02-industrial-flow',
    query: {
      layers: 'all',
      layerProfile: 'neutral',
      debug: '0',
    },
    expectPrev: '01-double-engine',
    expectNext: '03-hitech-os',
  },
  {
    id: 'nav-0062',
    routeId: '02-industrial-flow',
    query: {
      layers: 'all',
      layerProfile: 'neutral',
      debug: '1',
    },
    expectPrev: '01-double-engine',
    expectNext: '03-hitech-os',
  },
  {
    id: 'nav-0063',
    routeId: '02-industrial-flow',
    query: {
      layers: 'none',
      layerProfile: 'neutral',
      debug: '0',
    },
    expectPrev: '01-double-engine',
    expectNext: '03-hitech-os',
  },
  {
    id: 'nav-0064',
    routeId: '02-industrial-flow',
    query: {
      layers: 'none',
      layerProfile: 'neutral',
      debug: '1',
    },
    expectPrev: '01-double-engine',
    expectNext: '03-hitech-os',
  },
  {
    id: 'nav-0065',
    routeId: '02-industrial-flow',
    query: {
      layers: 'list',
      layerProfile: 'neutral',
      debug: '0',
    },
    expectPrev: '01-double-engine',
    expectNext: '03-hitech-os',
  },
  {
    id: 'nav-0066',
    routeId: '02-industrial-flow',
    query: {
      layers: 'list',
      layerProfile: 'neutral',
      debug: '1',
    },
    expectPrev: '01-double-engine',
    expectNext: '03-hitech-os',
  },
  {
    id: 'nav-0067',
    routeId: '02-industrial-flow',
    query: {
      layers: 'surfaceBase,chartGrid',
      layerProfile: 'neutral',
      debug: '0',
    },
    expectPrev: '01-double-engine',
    expectNext: '03-hitech-os',
  },
  {
    id: 'nav-0068',
    routeId: '02-industrial-flow',
    query: {
      layers: 'surfaceBase,chartGrid',
      layerProfile: 'neutral',
      debug: '1',
    },
    expectPrev: '01-double-engine',
    expectNext: '03-hitech-os',
  },
  {
    id: 'nav-0069',
    routeId: '02-industrial-flow',
    query: {
      layers: 'surfaceBase,glassTint',
      layerProfile: 'neutral',
      debug: '0',
    },
    expectPrev: '01-double-engine',
    expectNext: '03-hitech-os',
  },
  {
    id: 'nav-0070',
    routeId: '02-industrial-flow',
    query: {
      layers: 'surfaceBase,glassTint',
      layerProfile: 'neutral',
      debug: '1',
    },
    expectPrev: '01-double-engine',
    expectNext: '03-hitech-os',
  },
  {
    id: 'nav-0071',
    routeId: '02-industrial-flow',
    query: {
      layers: 'all',
      layerProfile: 'fx',
      debug: '0',
    },
    expectPrev: '01-double-engine',
    expectNext: '03-hitech-os',
  },
  {
    id: 'nav-0072',
    routeId: '02-industrial-flow',
    query: {
      layers: 'all',
      layerProfile: 'fx',
      debug: '1',
    },
    expectPrev: '01-double-engine',
    expectNext: '03-hitech-os',
  },
  {
    id: 'nav-0073',
    routeId: '02-industrial-flow',
    query: {
      layers: 'none',
      layerProfile: 'fx',
      debug: '0',
    },
    expectPrev: '01-double-engine',
    expectNext: '03-hitech-os',
  },
  {
    id: 'nav-0074',
    routeId: '02-industrial-flow',
    query: {
      layers: 'none',
      layerProfile: 'fx',
      debug: '1',
    },
    expectPrev: '01-double-engine',
    expectNext: '03-hitech-os',
  },
  {
    id: 'nav-0075',
    routeId: '02-industrial-flow',
    query: {
      layers: 'list',
      layerProfile: 'fx',
      debug: '0',
    },
    expectPrev: '01-double-engine',
    expectNext: '03-hitech-os',
  },
  {
    id: 'nav-0076',
    routeId: '02-industrial-flow',
    query: {
      layers: 'list',
      layerProfile: 'fx',
      debug: '1',
    },
    expectPrev: '01-double-engine',
    expectNext: '03-hitech-os',
  },
  {
    id: 'nav-0077',
    routeId: '02-industrial-flow',
    query: {
      layers: 'surfaceBase,chartGrid',
      layerProfile: 'fx',
      debug: '0',
    },
    expectPrev: '01-double-engine',
    expectNext: '03-hitech-os',
  },
  {
    id: 'nav-0078',
    routeId: '02-industrial-flow',
    query: {
      layers: 'surfaceBase,chartGrid',
      layerProfile: 'fx',
      debug: '1',
    },
    expectPrev: '01-double-engine',
    expectNext: '03-hitech-os',
  },
  {
    id: 'nav-0079',
    routeId: '02-industrial-flow',
    query: {
      layers: 'surfaceBase,glassTint',
      layerProfile: 'fx',
      debug: '0',
    },
    expectPrev: '01-double-engine',
    expectNext: '03-hitech-os',
  },
  {
    id: 'nav-0080',
    routeId: '02-industrial-flow',
    query: {
      layers: 'surfaceBase,glassTint',
      layerProfile: 'fx',
      debug: '1',
    },
    expectPrev: '01-double-engine',
    expectNext: '03-hitech-os',
  },
  {
    id: 'nav-0081',
    routeId: '02-industrial-flow',
    query: {
      layers: 'all',
      layerProfile: 'perf',
      debug: '0',
    },
    expectPrev: '01-double-engine',
    expectNext: '03-hitech-os',
  },
  {
    id: 'nav-0082',
    routeId: '02-industrial-flow',
    query: {
      layers: 'all',
      layerProfile: 'perf',
      debug: '1',
    },
    expectPrev: '01-double-engine',
    expectNext: '03-hitech-os',
  },
  {
    id: 'nav-0083',
    routeId: '02-industrial-flow',
    query: {
      layers: 'none',
      layerProfile: 'perf',
      debug: '0',
    },
    expectPrev: '01-double-engine',
    expectNext: '03-hitech-os',
  },
  {
    id: 'nav-0084',
    routeId: '02-industrial-flow',
    query: {
      layers: 'none',
      layerProfile: 'perf',
      debug: '1',
    },
    expectPrev: '01-double-engine',
    expectNext: '03-hitech-os',
  },
  {
    id: 'nav-0085',
    routeId: '02-industrial-flow',
    query: {
      layers: 'list',
      layerProfile: 'perf',
      debug: '0',
    },
    expectPrev: '01-double-engine',
    expectNext: '03-hitech-os',
  },
  {
    id: 'nav-0086',
    routeId: '02-industrial-flow',
    query: {
      layers: 'list',
      layerProfile: 'perf',
      debug: '1',
    },
    expectPrev: '01-double-engine',
    expectNext: '03-hitech-os',
  },
  {
    id: 'nav-0087',
    routeId: '02-industrial-flow',
    query: {
      layers: 'surfaceBase,chartGrid',
      layerProfile: 'perf',
      debug: '0',
    },
    expectPrev: '01-double-engine',
    expectNext: '03-hitech-os',
  },
  {
    id: 'nav-0088',
    routeId: '02-industrial-flow',
    query: {
      layers: 'surfaceBase,chartGrid',
      layerProfile: 'perf',
      debug: '1',
    },
    expectPrev: '01-double-engine',
    expectNext: '03-hitech-os',
  },
  {
    id: 'nav-0089',
    routeId: '02-industrial-flow',
    query: {
      layers: 'surfaceBase,glassTint',
      layerProfile: 'perf',
      debug: '0',
    },
    expectPrev: '01-double-engine',
    expectNext: '03-hitech-os',
  },
  {
    id: 'nav-0090',
    routeId: '02-industrial-flow',
    query: {
      layers: 'surfaceBase,glassTint',
      layerProfile: 'perf',
      debug: '1',
    },
    expectPrev: '01-double-engine',
    expectNext: '03-hitech-os',
  },
  {
    id: 'nav-0091',
    routeId: '03-hitech-os',
    query: {
      layers: 'all',
      layerProfile: 'neutral',
      debug: '0',
    },
    expectPrev: '02-industrial-flow',
    expectNext: '04-valuation',
  },
  {
    id: 'nav-0092',
    routeId: '03-hitech-os',
    query: {
      layers: 'all',
      layerProfile: 'neutral',
      debug: '1',
    },
    expectPrev: '02-industrial-flow',
    expectNext: '04-valuation',
  },
  {
    id: 'nav-0093',
    routeId: '03-hitech-os',
    query: {
      layers: 'none',
      layerProfile: 'neutral',
      debug: '0',
    },
    expectPrev: '02-industrial-flow',
    expectNext: '04-valuation',
  },
  {
    id: 'nav-0094',
    routeId: '03-hitech-os',
    query: {
      layers: 'none',
      layerProfile: 'neutral',
      debug: '1',
    },
    expectPrev: '02-industrial-flow',
    expectNext: '04-valuation',
  },
  {
    id: 'nav-0095',
    routeId: '03-hitech-os',
    query: {
      layers: 'list',
      layerProfile: 'neutral',
      debug: '0',
    },
    expectPrev: '02-industrial-flow',
    expectNext: '04-valuation',
  },
  {
    id: 'nav-0096',
    routeId: '03-hitech-os',
    query: {
      layers: 'list',
      layerProfile: 'neutral',
      debug: '1',
    },
    expectPrev: '02-industrial-flow',
    expectNext: '04-valuation',
  },
  {
    id: 'nav-0097',
    routeId: '03-hitech-os',
    query: {
      layers: 'surfaceBase,chartGrid',
      layerProfile: 'neutral',
      debug: '0',
    },
    expectPrev: '02-industrial-flow',
    expectNext: '04-valuation',
  },
  {
    id: 'nav-0098',
    routeId: '03-hitech-os',
    query: {
      layers: 'surfaceBase,chartGrid',
      layerProfile: 'neutral',
      debug: '1',
    },
    expectPrev: '02-industrial-flow',
    expectNext: '04-valuation',
  },
  {
    id: 'nav-0099',
    routeId: '03-hitech-os',
    query: {
      layers: 'surfaceBase,glassTint',
      layerProfile: 'neutral',
      debug: '0',
    },
    expectPrev: '02-industrial-flow',
    expectNext: '04-valuation',
  },
  {
    id: 'nav-0100',
    routeId: '03-hitech-os',
    query: {
      layers: 'surfaceBase,glassTint',
      layerProfile: 'neutral',
      debug: '1',
    },
    expectPrev: '02-industrial-flow',
    expectNext: '04-valuation',
  },
  {
    id: 'nav-0101',
    routeId: '03-hitech-os',
    query: {
      layers: 'all',
      layerProfile: 'fx',
      debug: '0',
    },
    expectPrev: '02-industrial-flow',
    expectNext: '04-valuation',
  },
  {
    id: 'nav-0102',
    routeId: '03-hitech-os',
    query: {
      layers: 'all',
      layerProfile: 'fx',
      debug: '1',
    },
    expectPrev: '02-industrial-flow',
    expectNext: '04-valuation',
  },
  {
    id: 'nav-0103',
    routeId: '03-hitech-os',
    query: {
      layers: 'none',
      layerProfile: 'fx',
      debug: '0',
    },
    expectPrev: '02-industrial-flow',
    expectNext: '04-valuation',
  },
  {
    id: 'nav-0104',
    routeId: '03-hitech-os',
    query: {
      layers: 'none',
      layerProfile: 'fx',
      debug: '1',
    },
    expectPrev: '02-industrial-flow',
    expectNext: '04-valuation',
  },
  {
    id: 'nav-0105',
    routeId: '03-hitech-os',
    query: {
      layers: 'list',
      layerProfile: 'fx',
      debug: '0',
    },
    expectPrev: '02-industrial-flow',
    expectNext: '04-valuation',
  },
  {
    id: 'nav-0106',
    routeId: '03-hitech-os',
    query: {
      layers: 'list',
      layerProfile: 'fx',
      debug: '1',
    },
    expectPrev: '02-industrial-flow',
    expectNext: '04-valuation',
  },
  {
    id: 'nav-0107',
    routeId: '03-hitech-os',
    query: {
      layers: 'surfaceBase,chartGrid',
      layerProfile: 'fx',
      debug: '0',
    },
    expectPrev: '02-industrial-flow',
    expectNext: '04-valuation',
  },
  {
    id: 'nav-0108',
    routeId: '03-hitech-os',
    query: {
      layers: 'surfaceBase,chartGrid',
      layerProfile: 'fx',
      debug: '1',
    },
    expectPrev: '02-industrial-flow',
    expectNext: '04-valuation',
  },
  {
    id: 'nav-0109',
    routeId: '03-hitech-os',
    query: {
      layers: 'surfaceBase,glassTint',
      layerProfile: 'fx',
      debug: '0',
    },
    expectPrev: '02-industrial-flow',
    expectNext: '04-valuation',
  },
  {
    id: 'nav-0110',
    routeId: '03-hitech-os',
    query: {
      layers: 'surfaceBase,glassTint',
      layerProfile: 'fx',
      debug: '1',
    },
    expectPrev: '02-industrial-flow',
    expectNext: '04-valuation',
  },
  {
    id: 'nav-0111',
    routeId: '03-hitech-os',
    query: {
      layers: 'all',
      layerProfile: 'perf',
      debug: '0',
    },
    expectPrev: '02-industrial-flow',
    expectNext: '04-valuation',
  },
  {
    id: 'nav-0112',
    routeId: '03-hitech-os',
    query: {
      layers: 'all',
      layerProfile: 'perf',
      debug: '1',
    },
    expectPrev: '02-industrial-flow',
    expectNext: '04-valuation',
  },
  {
    id: 'nav-0113',
    routeId: '03-hitech-os',
    query: {
      layers: 'none',
      layerProfile: 'perf',
      debug: '0',
    },
    expectPrev: '02-industrial-flow',
    expectNext: '04-valuation',
  },
  {
    id: 'nav-0114',
    routeId: '03-hitech-os',
    query: {
      layers: 'none',
      layerProfile: 'perf',
      debug: '1',
    },
    expectPrev: '02-industrial-flow',
    expectNext: '04-valuation',
  },
  {
    id: 'nav-0115',
    routeId: '03-hitech-os',
    query: {
      layers: 'list',
      layerProfile: 'perf',
      debug: '0',
    },
    expectPrev: '02-industrial-flow',
    expectNext: '04-valuation',
  },
  {
    id: 'nav-0116',
    routeId: '03-hitech-os',
    query: {
      layers: 'list',
      layerProfile: 'perf',
      debug: '1',
    },
    expectPrev: '02-industrial-flow',
    expectNext: '04-valuation',
  },
  {
    id: 'nav-0117',
    routeId: '03-hitech-os',
    query: {
      layers: 'surfaceBase,chartGrid',
      layerProfile: 'perf',
      debug: '0',
    },
    expectPrev: '02-industrial-flow',
    expectNext: '04-valuation',
  },
  {
    id: 'nav-0118',
    routeId: '03-hitech-os',
    query: {
      layers: 'surfaceBase,chartGrid',
      layerProfile: 'perf',
      debug: '1',
    },
    expectPrev: '02-industrial-flow',
    expectNext: '04-valuation',
  },
  {
    id: 'nav-0119',
    routeId: '03-hitech-os',
    query: {
      layers: 'surfaceBase,glassTint',
      layerProfile: 'perf',
      debug: '0',
    },
    expectPrev: '02-industrial-flow',
    expectNext: '04-valuation',
  },
  {
    id: 'nav-0120',
    routeId: '03-hitech-os',
    query: {
      layers: 'surfaceBase,glassTint',
      layerProfile: 'perf',
      debug: '1',
    },
    expectPrev: '02-industrial-flow',
    expectNext: '04-valuation',
  },
  {
    id: 'nav-0121',
    routeId: '04-valuation',
    query: {
      layers: 'all',
      layerProfile: 'neutral',
      debug: '0',
    },
    expectPrev: '03-hitech-os',
    expectNext: null,
  },
  {
    id: 'nav-0122',
    routeId: '04-valuation',
    query: {
      layers: 'all',
      layerProfile: 'neutral',
      debug: '1',
    },
    expectPrev: '03-hitech-os',
    expectNext: null,
  },
  {
    id: 'nav-0123',
    routeId: '04-valuation',
    query: {
      layers: 'none',
      layerProfile: 'neutral',
      debug: '0',
    },
    expectPrev: '03-hitech-os',
    expectNext: null,
  },
  {
    id: 'nav-0124',
    routeId: '04-valuation',
    query: {
      layers: 'none',
      layerProfile: 'neutral',
      debug: '1',
    },
    expectPrev: '03-hitech-os',
    expectNext: null,
  },
  {
    id: 'nav-0125',
    routeId: '04-valuation',
    query: {
      layers: 'list',
      layerProfile: 'neutral',
      debug: '0',
    },
    expectPrev: '03-hitech-os',
    expectNext: null,
  },
  {
    id: 'nav-0126',
    routeId: '04-valuation',
    query: {
      layers: 'list',
      layerProfile: 'neutral',
      debug: '1',
    },
    expectPrev: '03-hitech-os',
    expectNext: null,
  },
  {
    id: 'nav-0127',
    routeId: '04-valuation',
    query: {
      layers: 'surfaceBase,chartGrid',
      layerProfile: 'neutral',
      debug: '0',
    },
    expectPrev: '03-hitech-os',
    expectNext: null,
  },
  {
    id: 'nav-0128',
    routeId: '04-valuation',
    query: {
      layers: 'surfaceBase,chartGrid',
      layerProfile: 'neutral',
      debug: '1',
    },
    expectPrev: '03-hitech-os',
    expectNext: null,
  },
  {
    id: 'nav-0129',
    routeId: '04-valuation',
    query: {
      layers: 'surfaceBase,glassTint',
      layerProfile: 'neutral',
      debug: '0',
    },
    expectPrev: '03-hitech-os',
    expectNext: null,
  },
  {
    id: 'nav-0130',
    routeId: '04-valuation',
    query: {
      layers: 'surfaceBase,glassTint',
      layerProfile: 'neutral',
      debug: '1',
    },
    expectPrev: '03-hitech-os',
    expectNext: null,
  },
  {
    id: 'nav-0131',
    routeId: '04-valuation',
    query: {
      layers: 'all',
      layerProfile: 'fx',
      debug: '0',
    },
    expectPrev: '03-hitech-os',
    expectNext: null,
  },
  {
    id: 'nav-0132',
    routeId: '04-valuation',
    query: {
      layers: 'all',
      layerProfile: 'fx',
      debug: '1',
    },
    expectPrev: '03-hitech-os',
    expectNext: null,
  },
  {
    id: 'nav-0133',
    routeId: '04-valuation',
    query: {
      layers: 'none',
      layerProfile: 'fx',
      debug: '0',
    },
    expectPrev: '03-hitech-os',
    expectNext: null,
  },
  {
    id: 'nav-0134',
    routeId: '04-valuation',
    query: {
      layers: 'none',
      layerProfile: 'fx',
      debug: '1',
    },
    expectPrev: '03-hitech-os',
    expectNext: null,
  },
  {
    id: 'nav-0135',
    routeId: '04-valuation',
    query: {
      layers: 'list',
      layerProfile: 'fx',
      debug: '0',
    },
    expectPrev: '03-hitech-os',
    expectNext: null,
  },
  {
    id: 'nav-0136',
    routeId: '04-valuation',
    query: {
      layers: 'list',
      layerProfile: 'fx',
      debug: '1',
    },
    expectPrev: '03-hitech-os',
    expectNext: null,
  },
  {
    id: 'nav-0137',
    routeId: '04-valuation',
    query: {
      layers: 'surfaceBase,chartGrid',
      layerProfile: 'fx',
      debug: '0',
    },
    expectPrev: '03-hitech-os',
    expectNext: null,
  },
  {
    id: 'nav-0138',
    routeId: '04-valuation',
    query: {
      layers: 'surfaceBase,chartGrid',
      layerProfile: 'fx',
      debug: '1',
    },
    expectPrev: '03-hitech-os',
    expectNext: null,
  },
  {
    id: 'nav-0139',
    routeId: '04-valuation',
    query: {
      layers: 'surfaceBase,glassTint',
      layerProfile: 'fx',
      debug: '0',
    },
    expectPrev: '03-hitech-os',
    expectNext: null,
  },
  {
    id: 'nav-0140',
    routeId: '04-valuation',
    query: {
      layers: 'surfaceBase,glassTint',
      layerProfile: 'fx',
      debug: '1',
    },
    expectPrev: '03-hitech-os',
    expectNext: null,
  },
  {
    id: 'nav-0141',
    routeId: '04-valuation',
    query: {
      layers: 'all',
      layerProfile: 'perf',
      debug: '0',
    },
    expectPrev: '03-hitech-os',
    expectNext: null,
  },
  {
    id: 'nav-0142',
    routeId: '04-valuation',
    query: {
      layers: 'all',
      layerProfile: 'perf',
      debug: '1',
    },
    expectPrev: '03-hitech-os',
    expectNext: null,
  },
  {
    id: 'nav-0143',
    routeId: '04-valuation',
    query: {
      layers: 'none',
      layerProfile: 'perf',
      debug: '0',
    },
    expectPrev: '03-hitech-os',
    expectNext: null,
  },
  {
    id: 'nav-0144',
    routeId: '04-valuation',
    query: {
      layers: 'none',
      layerProfile: 'perf',
      debug: '1',
    },
    expectPrev: '03-hitech-os',
    expectNext: null,
  },
  {
    id: 'nav-0145',
    routeId: '04-valuation',
    query: {
      layers: 'list',
      layerProfile: 'perf',
      debug: '0',
    },
    expectPrev: '03-hitech-os',
    expectNext: null,
  },
  {
    id: 'nav-0146',
    routeId: '04-valuation',
    query: {
      layers: 'list',
      layerProfile: 'perf',
      debug: '1',
    },
    expectPrev: '03-hitech-os',
    expectNext: null,
  },
  {
    id: 'nav-0147',
    routeId: '04-valuation',
    query: {
      layers: 'surfaceBase,chartGrid',
      layerProfile: 'perf',
      debug: '0',
    },
    expectPrev: '03-hitech-os',
    expectNext: null,
  },
  {
    id: 'nav-0148',
    routeId: '04-valuation',
    query: {
      layers: 'surfaceBase,chartGrid',
      layerProfile: 'perf',
      debug: '1',
    },
    expectPrev: '03-hitech-os',
    expectNext: null,
  },
  {
    id: 'nav-0149',
    routeId: '04-valuation',
    query: {
      layers: 'surfaceBase,glassTint',
      layerProfile: 'perf',
      debug: '0',
    },
    expectPrev: '03-hitech-os',
    expectNext: null,
  },
  {
    id: 'nav-0150',
    routeId: '04-valuation',
    query: {
      layers: 'surfaceBase,glassTint',
      layerProfile: 'perf',
      debug: '1',
    },
    expectPrev: '03-hitech-os',
    expectNext: null,
  },
];

describe('route navigation matrix', () => {
  it('preserves deterministic prev/next and query propagation', () => {
    for (const testCase of cases) {
      const nav = selectRouteNavigation(testCase.routeId, testCase.query);
      expect(nav.current.id, `${testCase.id}:current`).toBe(testCase.routeId);
      expect(nav.prev?.id ?? null, `${testCase.id}:prev`).toBe(testCase.expectPrev);
      expect(nav.next?.id ?? null, `${testCase.id}:next`).toBe(testCase.expectNext);
      expect(nav.items.length, `${testCase.id}:items`).toBe(5);

      for (const item of nav.items) {
        expect(item.href).toContain(`layers=${testCase.query.layers}`);
        expect(item.href).toContain(`layerProfile=${testCase.query.layerProfile}`);
        expect(item.href).toContain(`debug=${testCase.query.debug}`);
      }
    }
  });

  it('keeps matrix size deterministic', () => {
    expect(cases.length).toBe(150);
    expect(cases[0]?.id).toBe("nav-0001");
    expect(cases[cases.length - 1]?.id).toBe("nav-0150");
  });
});

