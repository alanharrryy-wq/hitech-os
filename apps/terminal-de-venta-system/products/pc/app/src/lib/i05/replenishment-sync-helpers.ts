export function formatLatency(seconds: number) {
  return `${seconds.toFixed(2)} s`;
}

export function badgeForPriority(priority: string) {
  return priority === 'high' ? 'Alta' : priority === 'medium' ? 'Media' : 'Baja';
}
