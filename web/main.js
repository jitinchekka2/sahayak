import { streamGemini } from './gemini-api.js';
import { generateMermaid } from './generateMermaid.js';
import { detectSpeakingTestIntent, initiateSpeakingTest } from './speakingTest.js';

// DOM elements
const form = document.querySelector('.input-form');
const messageInput = document.querySelector('.message-input');
const messages = document.querySelector('.messages');
const attachButton = document.querySelector('#attach-button');
const micButton = document.querySelector('#mic-button');
const imageUpload = document.querySelector('#image-upload');
const attachedImageDiv = document.querySelector('#attached-image');
const attachedPreview = document.querySelector('#attached-preview');
const removeAttachmentBtn = document.querySelector('#remove-attachment');
const sendButton = document.querySelector('.send-btn');
const suggestionsContainer = document.querySelector('.suggestions');

// State
let attachedImageData = null;
let isRecording = false;
let recognition = null;
let conversationHistory = [
  {
    role: 'user',
    parts: [{ text: "You are Sahayak, a helpful AI assistant with various tools. Please introduce yourself as Sahayak and be friendly and helpful." }]
  },
  {
    role: 'model',
    parts: [{ text: "Hello! I'm Sahayak, your AI assistant. I'm here to help you with any questions or tasks you have. How can I assist you today?" }]
  }
];

// Initialize speech recognition
function initSpeechRecognition() {
  // Browser compatibility for Speech Recognition API
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = function () {
      isRecording = true;
      micButton.classList.add('recording');
    };

    recognition.onresult = function (event) {
      const transcript = Array.from(event.results)
        .map(result => result[0].transcript)
        .join('');

      messageInput.value = transcript;
    };

    recognition.onerror = function (event) {
      console.error('Speech recognition error:', event.error);
      stopRecording();
    };

    recognition.onend = function () {
      stopRecording();
    };
  } else {
    micButton.style.display = 'none';
    console.warn('Speech recognition not supported in this browser');
  }
}

function toggleRecording() {
  if (!recognition) {
    initSpeechRecognition();
  }

  if (isRecording) {
    stopRecording();
  } else {
    startRecording();
  }
}

function startRecording() {
  if (recognition) {
    messageInput.placeholder = "Listening...";
    recognition.start();
  }
}

function stopRecording() {
  if (recognition) {
    recognition.stop();
    isRecording = false;
    micButton.classList.remove('recording');
    messageInput.placeholder = "Enter a prompt for Sahayak";
  }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  messageInput.focus();
  scrollToBottom();

  // Initialize speech recognition if available
  if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    initSpeechRecognition();
  }

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

  // Handle mic button click
  micButton.addEventListener('click', toggleRecording);

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

    // Stop recording if active
    if (isRecording) {
      stopRecording();
    }

    const message = messageInput.value.trim();

    if (!message && !attachedImageData) {
      return;
    }

    // Disable form
    messageInput.disabled = true;
    sendButton.disabled = true;

    // Add user message to chat
    addUserMessage(message, attachedImageData?.dataUrl);

    // Clear form immediately after adding user message
    messageInput.value = '';

    // Clear attachment
    attachedImageData = null;
    attachedImageDiv.style.display = 'none';
    imageUpload.value = '';

    // Add typing indicator
    const typingElement = addTypingIndicator();

    // Check for speaking test intent first
    if (message) {
      const isSpeakingIntent = await detectSpeakingTestIntent(message, conversationHistory);
      if (isSpeakingIntent) {
        console.log("Detected speaking test intent:", message);
        messageInput.value = '';

        // Remove typing indicator before starting the speaking test
        typingElement.remove();

        try {
          await initiateSpeakingTest(addAssistantMessage, scrollToBottom, conversationHistory);
        } finally {
          // Make sure form is re-enabled even after speaking test
          messageInput.disabled = false;
          sendButton.disabled = false;
          messageInput.focus();
        }
        return;
      }
    }

    try {
      // Prepare API request
      const parts = [];

      // First, let's ask the LLM to determine if this is a diagram generation request
      const routerResponse = await streamGemini({
        model: 'gemini-2.5-flash',
        contents: [{
          role: 'user',
          parts: [{
            text: `Analyze if this request would benefit from a diagram/flowchart/visualization. 
          Respond with YES if any of these are true:
          1. It describes a process or cycle (like photosynthesis, water cycle, etc.)
          2. It involves steps or stages in a sequence
          3. It describes relationships between components
          4. It explains a system or mechanism
          5. It contains words like: process, cycle, steps, stages, flow, mechanism
          6. It's explaining a scientific concept with multiple parts
          
          Only respond with "YES" or "NO": "${message}"`
          }]
        }]
      });

      let shouldGenerateDiagram = false;
      for await (let chunk of routerResponse) {
        if (chunk.trim().toUpperCase() === 'YES') {
          shouldGenerateDiagram = true;
          break;
        }
      }

      // Always prepare regular assistant query
      if (attachedImageData) {
        parts.push({
          inline_data: {
            mime_type: attachedImageData.mimeType,
            data: attachedImageData.base64
          }
        });
      }
      parts.push({ text: message });


      // Add the current user message to conversation history before making the API call
      conversationHistory.push({
        role: 'user',
        parts: parts
      });
      const stream = streamGemini({
        model: 'gemini-2.5-flash',
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

      // Generate diagram if needed, after the text response
      if (shouldGenerateDiagram) {
        try {
          const diagramCode = await generateMermaid(message);
          // Add separator and diagram
          const separatorHr = document.createElement('hr');
          contentElement.appendChild(separatorHr);

          const diagramSection = document.createElement('div');
          diagramSection.className = 'diagram-section';
          contentElement.appendChild(diagramSection);

          renderMermaidDiagram(diagramCode, diagramSection);
        } catch (err) {
          const errorP = document.createElement('p');
          errorP.style.color = '#f44336';
          errorP.textContent = `Error generating diagram: ${err.message}`;
          contentElement.appendChild(document.createElement('hr'));
          contentElement.appendChild(errorP);
        }
      }

      // Add assistant response to conversation history
      conversationHistory.push({
        role: 'model',
        parts: [{ text: fullContent }]
      });

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
  // Clean up the code - remove any markdown code blocks
  const cleanCode = code.replace(/```mermaid\n?/g, '').replace(/```\n?/g, '').trim();

  const mermaidDiv = document.createElement('div');
  mermaidDiv.className = 'mermaid';
  mermaidDiv.textContent = cleanCode;

  container.innerHTML = '';
  container.appendChild(mermaidDiv);

  // Initialize and render mermaid
  if (window.mermaid) {
    window.mermaid.initialize({
      startOnLoad: false,
      theme: 'default',
      securityLevel: 'loose'
    });

    // Generate a unique id for this diagram
    const diagramId = 'mermaid-diagram-' + Date.now();
    mermaidDiv.id = diagramId;

    try {
      window.mermaid.init(undefined, mermaidDiv);
    } catch (error) {
      console.error('Mermaid rendering error:', error);
      container.innerHTML = `<p style="color: #f44336;">Error rendering diagram: ${error.message}</p>`;
    }
  } else {
    container.innerHTML = '<p style="color: #f44336;">Mermaid library not loaded</p>';
  }
}
// Helper functions
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