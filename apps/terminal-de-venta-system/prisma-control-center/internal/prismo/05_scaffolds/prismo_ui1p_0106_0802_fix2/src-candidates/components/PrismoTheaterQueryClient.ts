export type PrismoTheaterQueryInput = {
  objective: string;
  domain: string;
  lens: string;
  freeText?: string;
  contextNote?: string;
  autoRender: true;
};

export async function queryPrismoTheater(input: PrismoTheaterQueryInput) {
  const response = await fetch('/api/prismo/theater/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  });
  if (!response.ok) {
    throw new Error(`PRISMO Theater query failed: ${response.status}`);
  }
  return response.json();
}
