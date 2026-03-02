import type { FeatureFlags, HealthReport } from "@hitech/contracts";
import { Button, Card, Section, Text } from "@hitech/ui-kit";

export interface HealthPageProps {
  flags: FeatureFlags;
  health: HealthReport | null;
  loading: boolean;
  error: string | null;
  onRefresh(): void;
  onBack(): void;
}

export function HealthPage({ flags, health, loading, error, onRefresh, onBack }: HealthPageProps) {
  const enabled = flags.enableHealthDashboard;

  return (
    <Section
      heading="Health Dashboard"
      description="Reads /health from core-api using shared contract types."
    >
      <Card title="Feature Gate" subtitle="`enableHealthDashboard` default is OFF">
        {enabled ? (
          <Text tone="success">Health dashboard feature flag is enabled.</Text>
        ) : (
          <Text tone="danger">
            Health dashboard feature flag is OFF. Data refresh remains available for smoke checks.
          </Text>
        )}
      </Card>

      <Card title="Runtime State" subtitle="Deterministic JSON snapshot">
        {loading ? <Text>Loading...</Text> : null}
        {error ? <Text tone="danger">{error}</Text> : null}
        {!loading && !error && health ? (
          <pre className="web-pre">{JSON.stringify(health, null, 2)}</pre>
        ) : null}
      </Card>

      <div className="web-actions">
        <Button onClick={onRefresh}>Refresh Health</Button>
        <Button variant="secondary" onClick={onBack}>
          Back Home
        </Button>
      </div>
    </Section>
  );
}
