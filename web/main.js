import { streamGemini } from './gemini-api.js';

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

    // Disable form
    messageInput.disabled = true;
    sendButton.disabled = true;

    // Add user message to chat
    addUserMessage(message, attachedImageData?.dataUrl);

    // Clear input and attachment
    messageInput.value = '';
    const currentAttachment = attachedImageData;
    attachedImageData = null;
    attachedImageDiv.style.display = 'none';
    imageUpload.value = '';

    // Show typing indicator
    const typingElement = addTypingIndicator();

    try {
      // Prepare API request
      const parts = [];
      if (message) {
        parts.push({ text: message });
      }
      if (currentAttachment) {
        parts.unshift({
          inline_data: {
            mime_type: currentAttachment.mimeType,
            data: currentAttachment.base64
          }
        });
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

      // Call API
      const stream = streamGemini({
        model: 'gemini-2.0-flash',
        contents,
      });

      // Remove typing indicator and add assistant message
      typingElement.remove();
      const assistantElement = addAssistantMessage('');
      const contentElement = assistantElement.querySelector('.message-content');

      // Stream response
      let buffer = [];
      const md = new markdownit();

      for await (let chunk of stream) {
        buffer.push(chunk);
        contentElement.innerHTML = md.render(buffer.join(''));
        scrollToBottom();
      }

    } catch (error) {
      // Remove typing indicator and show error
      typingElement.remove();
      addAssistantMessage(`Sorry, I encountered an error: ${error.message}`);
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
  typingDiv.innerHTML = `
    <div class="message-content">
      <div class="typing-indicator">
        <span>Sahayak is typing</span>
        <div class="typing-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
  `;

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