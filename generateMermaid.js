export async function generateMermaid(prompt) {
  const response = await fetch('/api/generate_mermaid', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt })
  });

  const data = await response.json();
  if (data.error) throw new Error(data.error);

  return data.diagram; // backend already returns cleaned diagram
}
