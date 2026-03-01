import { GridLayoutConfig, GridLayoutConfigSchema } from "../mission-control/layout.js";
import { parseOrThrow } from "../parsing.js";

export const LAYOUT_FIXTURE: GridLayoutConfig = {
  version: 1,
  compactType: "vertical",
  bounded: true,
  allowOverlap: false,
  breakpoints: [
    {
      breakpoint: "xs",
      columns: 4,
      rowHeight: 84,
      gap: 8,
      items: [
        {
          widgetId: "wid_stat-001",
          panelSize: "sm",
          locked: false,
          resizable: true,
          draggable: true,
          position: { x: 0, y: 0, w: 2, h: 2, minW: 1, minH: 1, maxW: null, maxH: null }
        },
        {
          widgetId: "wid_feed-001",
          panelSize: "lg",
          locked: false,
          resizable: true,
          draggable: true,
          position: { x: 0, y: 2, w: 4, h: 4, minW: 2, minH: 2, maxW: null, maxH: null }
        }
      ]
    },
    {
      breakpoint: "sm",
      columns: 6,
      rowHeight: 88,
      gap: 10,
      items: [
        {
          widgetId: "wid_stat-001",
          panelSize: "sm",
          locked: false,
          resizable: true,
          draggable: true,
          position: { x: 0, y: 0, w: 2, h: 2, minW: 1, minH: 1, maxW: null, maxH: null }
        },
        {
          widgetId: "wid_table-001",
          panelSize: "lg",
          locked: false,
          resizable: true,
          draggable: true,
          position: { x: 2, y: 0, w: 4, h: 4, minW: 2, minH: 2, maxW: null, maxH: null }
        },
        {
          widgetId: "wid_feed-001",
          panelSize: "md",
          locked: false,
          resizable: true,
          draggable: true,
          position: { x: 0, y: 2, w: 2, h: 4, minW: 2, minH: 2, maxW: 4, maxH: null }
        }
      ]
    },
    {
      breakpoint: "md",
      columns: 12,
      rowHeight: 96,
      gap: 12,
      items: [
        {
          widgetId: "wid_stat-001",
          panelSize: "sm",
          locked: false,
          resizable: true,
          draggable: true,
          position: { x: 0, y: 0, w: 3, h: 2, minW: 2, minH: 2, maxW: 6, maxH: null }
        },
        {
          widgetId: "wid_table-001",
          panelSize: "xl",
          locked: false,
          resizable: true,
          draggable: true,
          position: { x: 3, y: 0, w: 6, h: 4, minW: 4, minH: 2, maxW: null, maxH: null }
        },
        {
          widgetId: "wid_feed-001",
          panelSize: "lg",
          locked: false,
          resizable: true,
          draggable: true,
          position: { x: 9, y: 0, w: 3, h: 6, minW: 3, minH: 3, maxW: null, maxH: null }
        },
        {
          widgetId: "wid_chart-001",
          panelSize: "lg",
          locked: false,
          resizable: true,
          draggable: true,
          // Keep chart below the table block on md to preserve a collision-free baseline.
          position: { x: 0, y: 4, w: 6, h: 4, minW: 4, minH: 3, maxW: null, maxH: null }
        },
        {
          widgetId: "wid_dial-001",
          panelSize: "sm",
          locked: false,
          resizable: false,
          draggable: true,
          position: { x: 6, y: 4, w: 3, h: 2, minW: 2, minH: 2, maxW: 4, maxH: 4 }
        }
      ]
    },
    {
      breakpoint: "lg",
      columns: 16,
      rowHeight: 100,
      gap: 12,
      items: [
        {
          widgetId: "wid_stat-001",
          panelSize: "sm",
          locked: false,
          resizable: true,
          draggable: true,
          position: { x: 0, y: 0, w: 3, h: 2, minW: 2, minH: 2, maxW: 5, maxH: null }
        },
        {
          widgetId: "wid_stat-002",
          panelSize: "sm",
          locked: false,
          resizable: true,
          draggable: true,
          position: { x: 3, y: 0, w: 3, h: 2, minW: 2, minH: 2, maxW: 5, maxH: null }
        },
        {
          widgetId: "wid_table-001",
          panelSize: "xl",
          locked: false,
          resizable: true,
          draggable: true,
          position: { x: 0, y: 2, w: 10, h: 5, minW: 6, minH: 3, maxW: null, maxH: null }
        },
        {
          widgetId: "wid_feed-001",
          panelSize: "lg",
          locked: false,
          resizable: true,
          draggable: true,
          position: { x: 10, y: 0, w: 6, h: 7, minW: 4, minH: 3, maxW: null, maxH: null }
        },
        {
          widgetId: "wid_chart-001",
          panelSize: "lg",
          locked: false,
          resizable: true,
          draggable: true,
          position: { x: 0, y: 7, w: 8, h: 4, minW: 4, minH: 3, maxW: null, maxH: null }
        },
        {
          widgetId: "wid_dial-001",
          panelSize: "sm",
          locked: false,
          resizable: false,
          draggable: true,
          position: { x: 8, y: 7, w: 2, h: 2, minW: 2, minH: 2, maxW: 2, maxH: 2 }
        }
      ]
    }
  ]
};

export function getLayoutFixture(): GridLayoutConfig {
  return LAYOUT_FIXTURE;
}

export function parseLayoutFixture(): GridLayoutConfig {
  return parseOrThrow(GridLayoutConfigSchema, LAYOUT_FIXTURE, {
    resource: "layout",
    operation: "fixture-parse"
  });
}
