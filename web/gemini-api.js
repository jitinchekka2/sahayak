/**
 * Calls the given Gemini model with the given image and/or text
 * parts, streaming output (as a generator function).
 */
export async function* streamGemini({
  model = 'gemini-2.5-flash', // or gemini-1.5-flash
    contents = [],
  
} = {}) {
  // Send the prompt to the Python backend
  // Call API defined in main.py
  let response = await fetch("/api/generate", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ model, contents })
  });

  yield* streamResponseChunks(response);
}

/**
 * Renders a Mermaid diagram visually in the browser.
 * @param {HTMLElement} container - The DOM element to render the diagram into.
 * @param {string} prompt - The prompt to send to the backend for diagram generation.
 * @returns {Promise<void>}
 */
export async function renderMermaidDiagram(container, prompt) {
  const diagramCode = await generateMermaid(prompt);
  container.innerHTML = ""; // Clear previous diagram
  window.mermaid.render("mermaid-diagram", diagramCode, (svgCode) => {
    container.innerHTML = svgCode;
  });
}

/**
 * A helper that streams text output chunks from a fetch() response.
 */
async function* streamResponseChunks(response) {
  let buffer = '';

  const CHUNK_SEPARATOR = '\n\n';

  let processBuffer = async function* (streamDone = false) {
    while (true) {
      let flush = false;
      let chunkSeparatorIndex = buffer.indexOf(CHUNK_SEPARATOR);
      if (streamDone && chunkSeparatorIndex < 0) {
        flush = true;
        chunkSeparatorIndex = buffer.length;
      }
      if (chunkSeparatorIndex < 0) {
        break;
      }

      let chunk = buffer.substring(0, chunkSeparatorIndex);
      buffer = buffer.substring(chunkSeparatorIndex + CHUNK_SEPARATOR.length);
      chunk = chunk.replace(/^data:\s*/, '').trim();
      if (!chunk) {
        if (flush) break;
        continue;
      }
      let { error, text } = JSON.parse(chunk);
      if (error) {
        console.error(error);
        throw new Error(error?.message || JSON.stringify(error));
      }
      yield text;
      if (flush) break;
    }
  };

  const reader = response.body.getReader();
  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break;
      buffer += new TextDecoder().decode(value);
      console.log(new TextDecoder().decode(value));
      yield* processBuffer();
    }
  } finally {
    reader.releaseLock();
  }

  yield* processBuffer(true);
}