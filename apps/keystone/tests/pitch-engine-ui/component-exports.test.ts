import {
  PitchEngineWorkbench,
  ProgramLibraryPanel,
  TimelineEditorPanel,
  ReplayTransportPanel,
  TimelinePreviewPanel,
  SceneRecorderPanel,
  DirectorControlsPanel,
  TriagePanel,
  OperatorStatusHud,
  SupportBundlePanel
} from "../../components/pitch-engine";
import { SceneStudioPage, SceneStudioHelpPanel } from "../../components/scene-studio";

describe("pitch-engine and scene-studio exports", () => {
  it("exports pitch-engine surfaces", () => {
    expect(PitchEngineWorkbench).toBeTruthy();
    expect(ProgramLibraryPanel).toBeTruthy();
    expect(TimelineEditorPanel).toBeTruthy();
    expect(ReplayTransportPanel).toBeTruthy();
    expect(TimelinePreviewPanel).toBeTruthy();
    expect(SceneRecorderPanel).toBeTruthy();
    expect(DirectorControlsPanel).toBeTruthy();
    expect(TriagePanel).toBeTruthy();
    expect(OperatorStatusHud).toBeTruthy();
    expect(SupportBundlePanel).toBeTruthy();
  });

  it("exports scene-studio integration components", () => {
    expect(SceneStudioPage).toBeTruthy();
    expect(SceneStudioHelpPanel).toBeTruthy();
  });
});
