import { streamGemini } from './gemini-api.js';
import { generateMermaid } from './generateMermaid.js';
import { detectSpeakingTestIntent, initiateSpeakingTest, isSpeakingTestActive } from './speakingTest.js';

// DOM elements
const form = document.querySelector('.input-form');
const messageInput = document.querySelector('.message-input');
const messages = document.querySelector('.messages');
const attachButton = document.querySelector('#attach-button');
const imageUpload = document.querySelector('#image-upload');
const attachedImageDiv = document.querySelector('#attached-image');
const attachedPreview = document.querySelector('#attached-preview');
const removeAttachmentBtn = document.querySelector('#remove-attachment');
const sendButton = document.querySelector('.send-btn');
const suggestionsContainer = document.querySelector('.suggestions');

// State
let attachedImageData = null;
let conversationHistory = [
  {
    role: 'user',
    parts: [{ text: "You are Sahayak, a helpful AI assistant with various tools. When users want to practice speaking, take a speaking test, or improve their pronunciation, you should automatically initiate the speaking test tool. Please introduce yourself as Sahayak and be friendly and helpful." }]
  },
  {
    role: 'model',
    parts: [{ text: "Hello! I'm Sahayak, your AI assistant. I'm here to help you with any questions or tasks you have. I can also help you practice speaking and pronunciation - just let me know if you'd like to take a speaking test! How can I assist you today?" }]
  }
];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  messageInput.focus();
  scrollToBottom();

  // Add suggestion click handlers
  const suggestionButtons = document.querySelectorAll('.suggestion-btn');
  suggestionButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const suggestion = btn.dataset.suggestion;
      messageInput.value = suggestion;
      messageInput.focus();
    });
  });

  // Handle attach button click
  attachButton.addEventListener('click', () => {
    imageUpload.click();
  });

  // Handle file selection
  imageUpload.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (event) => {
        attachedImageData = {
          base64: event.target.result.split(',')[1],
          mimeType: file.type,
          dataUrl: event.target.result
        };

        // Show preview
        attachedPreview.src = event.target.result;
        attachedImageDiv.style.display = 'block';
      };
      reader.readAsDataURL(file);
    }
  });

  // Handle remove attachment
  removeAttachmentBtn.addEventListener('click', () => {
    attachedImageData = null;
    attachedImageDiv.style.display = 'none';
    imageUpload.value = '';
  });

  // Handle form submission
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const message = messageInput.value.trim();

    if (!message && !attachedImageData) {
      return;
    }

    // Check for speaking test intent first
    if (message) {
      const isSpeakingIntent = await detectSpeakingTestIntent(message, conversationHistory);
      if (isSpeakingIntent) {
        addUserMessage(message);
        messageInput.value = '';
        await initiateSpeakingTest(addAssistantMessage, scrollToBottom, conversationHistory);
        messageInput.focus();
        return;
      }
    }

    // Disable form
    messageInput.disabled = true;
    sendButton.disabled = true;

    // Add user message to chat
    addUserMessage(message, attachedImageData?.dataUrl);
    try {
      // Prepare API request
      const parts = [];
      const isWorksheetMode = !!currentAttachment;

    if (isWorksheetMode) {
      // Worksheet generator logic
      parts.push({
        inline_data: {
          mime_type: currentAttachment.mimeType,
          data: currentAttachment.base64
        }
      });

      parts.push({
        text: `Based on this textbook page image, generate 3 differentiated worksheets:
    - Grade 3: Simple instructions, 3 easy comprehension questions, and one creative drawing activity.
    - Grade 6: Moderate complexity, 3 analytical questions, and one summarization activity.
    - Grade 9: Higher-order thinking questions, a critical thinking task, and one research prompt.
    Each worksheet should be clearly separated and labeled.`
      });
    } else {
      // First, let's ask the LLM to determine if this is a diagram generation request
      const routerResponse = await streamGemini({
        model: 'gemini-2.0-flash',
        contents: [{
          role: 'user',
          parts: [{ text: `Analyze if this request would benefit from a diagram/flowchart/visualization. 
          Respond with YES if any of these are true:
          1. It describes a process or cycle (like photosynthesis, water cycle, etc.)
          2. It involves steps or stages in a sequence
          3. It describes relationships between components
          4. It explains a system or mechanism
          5. It contains words like: process, cycle, steps, stages, flow, mechanism
          6. It's explaining a scientific concept with multiple parts
          
          Only respond with "YES" or "NO": "${message}"` }]
        }]
      });

      let shouldGenerateDiagram = false;
      for await (let chunk of routerResponse) {
        if (chunk.trim().toUpperCase() === 'YES') {
          shouldGenerateDiagram = true;
          break;
        }
      }

      if (shouldGenerateDiagram) {
        try {
          const diagramCode = await generateMermaid(message);
          const assistantElement = addAssistantMessage('');
          renderMermaidDiagram(diagramCode, assistantElement.querySelector('.message-content'));
          return; // Skip regular Gemini streaming
        } catch (err) {
          addAssistantMessage(`Error generating Mermaid diagram: ${err.message}`);
          return;
        }
      } else {
        // Regular assistant query
        parts.push({ text: message });
      }
    }


      const contents = [
        {
          role: 'user',
          parts: [{ text: "You are Sahayak, a helpful AI assistant. Please introduce yourself as Sahayak and be friendly and helpful." }]
        },
        {
          role: 'model',
          parts: [{ text: "Hello! I'm Sahayak, your AI assistant. I'm here to help you with any questions or tasks you have. How can I assist you today?" }]
        },
        {
          role: 'user',
          parts: parts
        }
      ];
      const stream = streamGemini({
        model: 'gemini-2.0-flash',
        contents: conversationHistory,
      });

      // Remove typing indicator and add assistant message
      typingElement.remove();
      const assistantElement = addAssistantMessage('');
      const contentElement = assistantElement.querySelector('.message-content');

      // Stream response
      let buffer = [];
      const md = new markdownit();
      let fullContent = '';
      for await (let chunk of stream) {
        buffer.push(chunk);
        fullContent += chunk;
        contentElement.innerHTML = md.render(buffer.join(''));
        scrollToBottom();
      }
      if (fullContent.includes('flowchart')) {
        renderMermaidDiagram(fullContent, contentElement);
      }

      // Add assistant response to conversation history
      conversationHistory.push({
        role: 'model',
        parts: [{ text: fullContent }]
      });

      if (fullContent.includes('flowchart')) {
        renderMermaidDiagram(fullContent, contentElement);
      }

    } catch (error) {
      // Remove typing indicator and show error
      typingElement.remove();
      const errorMessage = `Sorry, I encountered an error: ${error.message}`;
      addAssistantMessage(errorMessage);
      conversationHistory.push({
        role: 'model',
        parts: [{ text: errorMessage }]
      });
    } finally {
      // Re-enable form
      messageInput.disabled = false;
      sendButton.disabled = false;
      messageInput.focus();
    }
  });

  // Handle Enter key (without Shift)
  messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      form.dispatchEvent(new Event('submit'));
    }
  });
});

function renderMermaidDiagram(code, container) {
  const mermaidDiv = document.createElement('div');
  mermaidDiv.className = 'mermaid';
  mermaidDiv.textContent = code.trim(); // No regex needed now


  const codeBox = document.createElement('pre');
  codeBox.textContent = mermaidDiv.textContent;

  container.innerHTML = '';
  container.appendChild(mermaidDiv);
  container.appendChild(document.createElement('hr'));
  container.appendChild(codeBox);

  if (window.mermaid) {
    window.mermaid.initialize({ startOnLoad: false });
    window.mermaid.init(undefined, mermaidDiv);
  }
}

// --- Helper Functions ---
function addUserMessage(text, imageUrl = null) {
  const messageDiv = document.createElement('div');
  messageDiv.className = 'message user-message';

  let content = '';
  if (imageUrl) {
    content += `<img src="${imageUrl}" class="message-image" alt="User uploaded image">`;
  }
  if (text) {
    content += `<p>${escapeHtml(text)}</p>`;
  }

  messageDiv.innerHTML = `
    <div class="message-content">
      ${content}
    </div>
  `;

  messages.appendChild(messageDiv);
  scrollToBottom();
  return messageDiv;
}

function addAssistantMessage(text) {
  const messageDiv = document.createElement('div');
  messageDiv.className = 'message assistant-message';
  messageDiv.innerHTML = `
    <div class="message-content">
      ${text}
    </div>
  `;

  messages.appendChild(messageDiv);
  scrollToBottom();
  return messageDiv;
}

function addTypingIndicator() {
  const typingDiv = document.createElement('div');
  typingDiv.className = 'message assistant-message typing-indicator';

  messages.appendChild(typingDiv);
  scrollToBottom();
  return typingDiv;
}

function scrollToBottom() {
  requestAnimationFrame(() => {
    messages.scrollTop = messages.scrollHeight;
  });
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}