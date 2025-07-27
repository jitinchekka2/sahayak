import { streamGemini } from './gemini-api.js';

// Speaking test paragraphs
const speakingTestParagraphs = [
    "The sun dipped below the horizon, painting the sky in shades of orange and pink. A gentle breeze rustled the leaves in the trees, creating a soft, whispering sound.",
    "Technology has advanced at an incredible pace over the last few decades. From the first computers to the powerful devices in our pockets, the change has been monumental.",
    "A balanced diet and regular exercise are crucial for maintaining good health. It is important to consume a variety of nutrients and stay active to keep your body and mind in top shape.",
    "The old library was a quiet sanctuary, filled with the scent of aged paper and leather-bound books. Every shelf held stories waiting to be discovered by an eager reader."
];

// State variables
let speakingTestActive = false;
let mediaRecorder;
let audioChunks = [];

/**
 * Detects if the user wants to take a speaking test based on their message and conversation history
 * @param {string} message - The user's latest message
 * @param {Array} conversationHistory - The conversation history
 * @returns {Promise<boolean>} - True if speaking test intent is detected
 */
export async function detectSpeakingTestIntent(message, conversationHistory) {
    try {
        // Get the last few messages for context
        const recentHistory = conversationHistory.slice(-5);
        const conversationContext = recentHistory.map(msg => {
            const role = msg.role === 'user' ? 'User' : 'Assistant';
            const text = msg.parts[0]?.text || '';
            return `${role}: ${text.substring(0, 200)}...`;
        }).join('\n');

        // Create a focused conversation history for intent detection
        const intentDetectionHistory = [
            {
                role: 'user',
                parts: [{
                    text: `You are an intent detection AI. Analyze if the user wants to take a speaking test or practice pronunciation based on their latest message and conversation context.

RECENT CONVERSATION:
${conversationContext}

LATEST USER MESSAGE: "${message}"

Look for:
- Direct requests for speaking tests or pronunciation practice
- Requests to "repeat", "try again", "do another one" if they previously took a speaking test
- Any variation of wanting to practice speaking skills
- Requests for speech evaluation or feedback

Important: If the user previously took a speaking test and now asks to "repeat", "try again", "do it again", "another one", etc., this should be YES.

Respond with exactly "YES" or "NO" only.`
                }]
            }
        ];

        const stream = streamGemini({
            model: 'gemini-2.5-flash',
            contents: intentDetectionHistory,
        });

        let response = '';
        for await (let chunk of stream) {
            response += chunk;
        }

        // Clean up the response and check if it's "yes"
        const cleanResponse = response.trim().toLowerCase();
        console.log('Intent detection response:', cleanResponse);
        return cleanResponse === 'yes' || cleanResponse.startsWith('yes');

    } catch (error) {
        console.error('Error detecting speaking intent:', error);
        // Fallback to enhanced keyword detection
        const speakingKeywords = [
            'speaking test', 'pronunciation', 'speak', 'reading practice',
            'voice', 'record', 'speaking practice', 'oral', 'articulation',
            'fluency', 'speech', 'speaking skills', 'read aloud', 'repeat',
            'again', 'another', 'try again', 'do it again', 'one more'
        ];

        const lowerMessage = message.toLowerCase();
        return speakingKeywords.some(keyword => lowerMessage.includes(keyword));
    }
}

/**
 * Initiates a speaking test by displaying a random paragraph and recording controls
 * @param {Function} addAssistantMessage - Function to add assistant messages to the chat
 * @param {Function} scrollToBottom - Function to scroll chat to bottom
 * @param {Array} conversationHistory - The conversation history to update
 */
export async function initiateSpeakingTest(addAssistantMessage, scrollToBottom, conversationHistory) {
    if (speakingTestActive) return;

    speakingTestActive = true;
    const randomIndex = Math.floor(Math.random() * speakingTestParagraphs.length);
    const selectedText = speakingTestParagraphs[randomIndex];

    const testMessage = `🎤 **Speaking Test Initiated**

I'll help you practice your speaking and pronunciation! Please read the following paragraph aloud when you're ready:

---

*"${selectedText}"*

---

Click the "Start Recording" button below when you're ready to begin. I'll analyze your pronunciation, fluency, and provide feedback to help you improve.`;

    const assistantElement = addAssistantMessage('');
    const contentElement = assistantElement.querySelector('.message-content');
    const md = new markdownit();
    contentElement.innerHTML = md.render(testMessage);

    // Add recording controls
    const controlsDiv = document.createElement('div');
    controlsDiv.className = 'speaking-test-controls';
    controlsDiv.innerHTML = `
    <div style="margin-top: 15px; display: flex; gap: 10px; align-items: center;">
      <button id="start-speaking-btn" class="suggestion-btn" style="background: #4CAF50;">🎙️ Start Recording</button>
      <button id="stop-speaking-btn" class="suggestion-btn" style="background: #f44336; display: none;" disabled>⏹️ Stop Recording</button>
      <span id="recording-status" style="color: #666; font-size: 14px;"></span>
    </div>
  `;

    contentElement.appendChild(controlsDiv);

    // Store the text for analysis
    window.currentSpeakingText = selectedText;

    // Add event listeners
    setupSpeakingTestControls(addAssistantMessage, conversationHistory);

    scrollToBottom();
}

/**
 * Sets up event listeners for speaking test controls
 * @param {Function} addAssistantMessage - Function to add assistant messages to the chat
 * @param {Array} conversationHistory - The conversation history to update
 */
function setupSpeakingTestControls(addAssistantMessage, conversationHistory) {
    const startBtn = document.getElementById('start-speaking-btn');
    const stopBtn = document.getElementById('stop-speaking-btn');
    const status = document.getElementById('recording-status');

    if (!startBtn || !stopBtn) return;

    startBtn.addEventListener('click', async () => {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            alert('Your browser does not support audio recording.');
            return;
        }

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            const options = { mimeType: 'audio/webm;codecs=opus' };
            if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                mediaRecorder = new MediaRecorder(stream);
            } else {
                mediaRecorder = new MediaRecorder(stream, options);
            }

            audioChunks = [];

            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: options.mimeType });
                audioChunks = [];

                if (audioBlob.size === 0) {
                    alert("Recording was empty. Please try recording for a longer duration.");
                    resetSpeakingTestControls();
                    return;
                }

                await analyzeSpeaking(audioBlob, window.currentSpeakingText, addAssistantMessage, conversationHistory);
                resetSpeakingTestControls();
            };

            mediaRecorder.start();
            startBtn.style.display = 'none';
            stopBtn.style.display = 'inline-block';
            stopBtn.disabled = false;
            status.textContent = 'Recording... Speak clearly into your microphone.';
            status.style.color = '#f44336';

        } catch (error) {
            alert(`Error starting recording: ${error.message}`);
        }
    });

    stopBtn.addEventListener('click', () => {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
            status.textContent = 'Processing your recording...';
            status.style.color = '#FF9800';
        }
    });
}

/**
 * Resets the speaking test controls to their initial state
 */
function resetSpeakingTestControls() {
    const startBtn = document.getElementById('start-speaking-btn');
    const stopBtn = document.getElementById('stop-speaking-btn');
    const status = document.getElementById('recording-status');

    if (startBtn) startBtn.style.display = 'inline-block';
    if (stopBtn) {
        stopBtn.style.display = 'none';
        stopBtn.disabled = true;
    }
    if (status) {
        status.textContent = '';
    }

    speakingTestActive = false;
}

/**
 * Analyzes the recorded speech and provides feedback
 * @param {Blob} audioBlob - The recorded audio blob
 * @param {string} originalText - The text that was supposed to be read
 * @param {Function} addAssistantMessage - Function to add assistant messages to the chat
 * @param {Array} conversationHistory - The conversation history to update
 */
async function analyzeSpeaking(audioBlob, originalText, addAssistantMessage, conversationHistory) {
    const analysisElement = addAssistantMessage('');
    const contentElement = analysisElement.querySelector('.message-content');
    contentElement.innerHTML = '🔄 Analyzing your speaking... Please wait.';

    const formData = new FormData();
    formData.append('audio_file', audioBlob, 'recording.webm');
    formData.append('original_text', originalText);

    try {
        const response = await fetch('/api/analyze_reading', {
            method: 'POST',
            body: formData,
        });

        const result = await response.json();

        if (result.error) {
            contentElement.innerHTML = `❌ Error: ${result.error}`;
        } else {
            const md = new markdownit();
            contentElement.innerHTML = md.render(result.analysis);

            // Add conversation to history
            conversationHistory.push({
                role: 'model',
                parts: [{ text: result.analysis }]
            });
        }
    } catch (error) {
        contentElement.innerHTML = `❌ An unexpected error occurred: ${error.message}`;
    }
}

/**
 * Checks if a speaking test is currently active
 * @returns {boolean} - True if speaking test is active
 */
export function isSpeakingTestActive() {
    return speakingTestActive;
}