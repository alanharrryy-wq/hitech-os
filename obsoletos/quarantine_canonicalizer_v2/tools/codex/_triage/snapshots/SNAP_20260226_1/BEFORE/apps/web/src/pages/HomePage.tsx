import { Button, Card, Section, Text } from "@hitech/ui-kit";

export interface HomePageProps {
  apiBaseUrl: string;
  onOpenHealth(): void;
}

export function HomePage({ apiBaseUrl, onOpenHealth }: HomePageProps) {
  return (
    <Section
      heading="HITECH-OS"
      description="Deterministic monorepo baseline with typed contracts and strict guardrails"
    >
      <Card title="System Overview" subtitle="Bootstrap mode">
        <Text>
          This web app is intentionally minimal: it proves contract usage, flag gating defaults, and API
          connectivity.
        </Text>
        <Text tone="muted" as="small">
          Core API target: {apiBaseUrl}
        </Text>
      </Card>

      <Card title="Actions" subtitle="Manual smoke-friendly controls">
        <Button variant="primary" onClick={onOpenHealth}>
          Open Health Dashboard
        </Button>
      </Card>
    </Section>
  );
}
