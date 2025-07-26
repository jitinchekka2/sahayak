// Initialize mermaid configuration
if (window.mermaid) {
    window.mermaid.initialize({
        startOnLoad: false,
        theme: 'default',
        flowchart: {
            useMaxWidth: false,
            htmlLabels: true,
            curve: 'linear'
        }
    });
}

export async function generateMermaid(prompt) {
    const response = await fetch('/api/generate_mermaid', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
    });

    const data = await response.json();
    if (data.error) throw new Error(data.error);
    
    // Log the received diagram for debugging
    console.log('Received diagram:', data.diagram);
    return data.diagram;
}

export async function renderMermaidDiagram(container, prompt) {
    try {
        // Show loading state
        container.innerHTML = '<div style="text-align: center; padding: 20px;">Generating diagram...</div>';

        // Get the diagram code
        const diagramCode = await generateMermaid(prompt);
        
        // Log the diagram code for debugging
        console.log('Attempting to render diagram:', diagramCode);
        
        // Clear the container
        container.innerHTML = '';

        // Create a div for mermaid
        const mermaidDiv = document.createElement('div');
        mermaidDiv.className = 'mermaid';
        mermaidDiv.style.background = 'white';
        mermaidDiv.style.padding = '20px';
        mermaidDiv.style.borderRadius = '8px';
        mermaidDiv.textContent = diagramCode;
        
        // Add to container
        container.appendChild(mermaidDiv);

        // Check if mermaid is available
        if (!window.mermaid) {
            throw new Error('Mermaid library not loaded');
        }

        // Clear and re-render mermaid diagrams
        await window.mermaid.run({
            nodes: [mermaidDiv],
            suppressErrors: false
        });

    } catch (error) {
        console.error('Error rendering diagram:', error);
        container.innerHTML = `
            <div style="color: red; padding: 20px; text-align: center;">
                Error generating diagram: ${error.message}<br>
                <pre style="text-align: left; margin-top: 10px;">${error.stack || ''}</pre>
            </div>`;
    }
}
