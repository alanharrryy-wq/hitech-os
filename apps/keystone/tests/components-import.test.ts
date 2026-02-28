import {
  Badge,
  Button,
  Dialog,
  DropdownMenu,
  EmptyState,
  Grid,
  InsetPanel,
  Panel,
  ScrollArea,
  Select,
  Shell,
  Stage,
  Table,
  Tabs,
  Tooltip
} from "@hitech/ui-kit";

describe("ui-kit imports", () => {
  it("exposes required keystone components", () => {
    expect(Stage).toBeTruthy();
    expect(Shell).toBeTruthy();
    expect(Grid).toBeTruthy();
    expect(Panel).toBeTruthy();
    expect(InsetPanel).toBeTruthy();
    expect(Badge).toBeTruthy();
    expect(Button).toBeTruthy();
    expect(Select).toBeTruthy();
    expect(Tabs).toBeTruthy();
    expect(Dialog).toBeTruthy();
    expect(Tooltip).toBeTruthy();
    expect(DropdownMenu).toBeTruthy();
    expect(ScrollArea).toBeTruthy();
    expect(Table).toBeTruthy();
    expect(EmptyState).toBeTruthy();
  });
});
