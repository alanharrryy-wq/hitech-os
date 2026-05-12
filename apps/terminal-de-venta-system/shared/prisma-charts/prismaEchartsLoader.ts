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
        components.LegendComponent,
        components.TitleComponent,
        components.TooltipComponent,
        components.TransformComponent,
        components.VisualMapComponent,
        renderers.CanvasRenderer,
        renderers.SVGRenderer
      ]);
      return echarts;
    });
  }
  return echartsPromise;
}

