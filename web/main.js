import { streamGemini } from './gemini-api.js';
import { generateMermaid } from './generateMermaid.js';

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

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  messageInput.focus();
  scrollToBottom();

  const suggestionButtons = document.querySelectorAll('.suggestion-btn');
  suggestionButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      messageInput.value = btn.dataset.suggestion;
      messageInput.focus();
    });
  });

  attachButton.addEventListener('click', () => imageUpload.click());

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
        attachedPreview.src = event.target.result;
        attachedImageDiv.style.display = 'block';
      };
      reader.readAsDataURL(file);
    }
  });

  removeAttachmentBtn.addEventListener('click', () => {
    attachedImageData = null;
    attachedImageDiv.style.display = 'none';
    imageUpload.value = '';
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = messageInput.value.trim();
    if (!message && !attachedImageData) return;

    messageInput.disabled = true;
    sendButton.disabled = true;

    addUserMessage(message, attachedImageData?.dataUrl);
    messageInput.value = '';

    const currentAttachment = attachedImageData;
    attachedImageData = null;
    attachedImageDiv.style.display = 'none';
    imageUpload.value = '';

    const typingElement = addTypingIndicator();

    try {
      const isAssessmentRequest = /(quiz|test|assessment|mcq|questions|evaluate|evaluate me|assess me|test me)/i.test(message) && currentAttachment;

      if (isAssessmentRequest) {
        typingElement.remove();
        showAssessmentOptions(currentAttachment, message);
        return;
      }

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
        const diagramCode = await generateMermaid(message);
        const assistantElement = addAssistantMessage('');
        renderMermaidDiagram(diagramCode, assistantElement.querySelector('.message-content'));
        return;
      }

      const parts = [{ text: message }];
      const contents = [
        { role: 'user', parts: [{ text: "You are Sahayak, a helpful AI assistant. Please introduce yourself as Sahayak and be friendly and helpful." }] },
        { role: 'model', parts: [{ text: "Hello! I'm Sahayak, your AI assistant. I'm here to help you with any questions or tasks you have. How can I assist you today?" }] },
        { role: 'user', parts }
      ];

      const stream = streamGemini({ model: 'gemini-2.0-flash', contents });
      typingElement.remove();
      const assistantElement = addAssistantMessage('');
      const contentElement = assistantElement.querySelector('.message-content');
      const buffer = [];
      const md = new markdownit();

      for await (let chunk of stream) {
        buffer.push(chunk);
        contentElement.innerHTML = md.render(buffer.join(''));
        scrollToBottom();
      }
    } catch (error) {
      typingElement.remove();
      addAssistantMessage(`Sorry, I encountered an error: ${error.message}`);
    } finally {
      messageInput.disabled = false;
      sendButton.disabled = false;
      messageInput.focus();
    }
  });

  messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      form.dispatchEvent(new Event('submit'));
    }
  });
});


function showAssessmentOptions(imageData, userMessage) {
  const assistantElement = addAssistantMessage('<strong>Select the type of assessment you want:</strong>', true);
  const container = document.createElement('div');
  container.className = 'assessment-options';

  const types = ['MCQs', 'Fill in the Blanks', 'Short Answers'];
  types.forEach(type => {
    const btn = document.createElement('button');
    btn.textContent = type;
    btn.className = 'btn assessment-btn';
    btn.addEventListener('click', () => generateAssessment(type, imageData, userMessage, assistantElement));
    container.appendChild(btn);
  });

  assistantElement.querySelector('.message-content').appendChild(container);
}

async function generateAssessment(type, imageData, userMessage, assistantElement) {
  const promptMap = {
    'MCQs': `Generate 5 multiple choice questions from this textbook page image.`,
    'Fill in the Blanks': `Generate 5 fill-in-the-blank questions based on this image.`,
    'Short Answers': `Generate 5 short answer questions from the textbook page image.`
  };

  const parts = [
    {
      inline_data: {
        mime_type: imageData.mimeType,
        data: imageData.base64
      }
    },
    { text: promptMap[type] }
  ];

  const contents = [
    { role: 'user', parts }
  ];

  const stream = streamGemini({ model: 'gemini-2.0-flash', contents });
  const contentElement = assistantElement.querySelector('.message-content');
  contentElement.innerHTML = `<strong>${type}:</strong><br>`;
  const buffer = [];
  const md = new markdownit();

  for await (let chunk of stream) {
    buffer.push(chunk);
    const rendered = md.render(buffer.join('').replace(/\([a-d]\)\s*/g, '\n$& '));
    contentElement.innerHTML = rendered;
    scrollToBottom();
  }
}

// Utility
function renderMermaidDiagram(code, container) {
  const mermaidDiv = document.createElement('div');
  mermaidDiv.className = 'mermaid';
  mermaidDiv.textContent = code.trim();
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

function addUserMessage(text, imageUrl = null) {
  const div = document.createElement('div');
  div.className = 'message user-message';
  div.innerHTML = `
    <div class="message-content">
      ${imageUrl ? `<img src="${imageUrl}" class="message-image">` : ''}
      ${text ? `<p>${escapeHtml(text)}</p>` : ''}
    </div>`;
  messages.appendChild(div);
  scrollToBottom();
  return div;
}

function addAssistantMessage(content, isHTML = false) {
  const messageElement = document.createElement('div');
  messageElement.className = 'message assistant-message';

  const messageContent = document.createElement('div');
  messageContent.className = 'message-content';

  // 🛠️ Allow HTML or plain text rendering
  if (isHTML) {
    messageContent.innerHTML = content;
  } else {
    messageContent.textContent = content;
  }

  messageElement.appendChild(messageContent);
  document.getElementById('messages').appendChild(messageElement);
  return messageElement;
}

function addTypingIndicator() {
  const div = document.createElement('div');
  div.className = 'message assistant-message typing-indicator';
  messages.appendChild(div);
  scrollToBottom();
  return div;
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