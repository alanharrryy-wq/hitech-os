// PHASE4_EXECUTIVE_COMMAND_CENTER_PRO_V1
// PRISMA_ECHARTS_EFFECT_SCATTER_IMPORT_V1
import { EffectScatterChart } from "echarts/charts";
let echartsPromise: Promise<typeof import("echarts/core")> | null = null;

export async function loadPrismaEcharts() {
  if (!echartsPromise) {
    echartsPromise = Promise.all([
      import("echarts/core"),
      import("echarts/charts"),
      import("echarts/components"),
      import("echarts/renderers")
    ]).then(([echarts, charts, components, renderers]) => {
      echarts.use([
        charts.BarChart,
        charts.CustomChart,
        charts.GraphChart,
        charts.HeatmapChart,
        charts.LineChart,
        charts.PictorialBarChart,
        charts.RadarChart,
        charts.SankeyChart,
        charts.ScatterChart,
        charts.TreemapChart,
        components.AriaComponent,
        components.BrushComponent,
        components.DatasetComponent,
        components.DataZoomComponent,
        components.GridComponent,
        components.GraphicComponent,
        components.LegendComponent,
        components.TitleComponent,
        components.TooltipComponent,
        components.TransformComponent,
        components.VisualMapComponent,
        renderers.CanvasRenderer,
        renderers.SVGRenderer,
  EffectScatterChart
]);
      return echarts;
    });
  }
  return echartsPromise;
}

