# Sahayak Web Components

This directory contains the frontend components for the Sahayak AI Assistant.

## File Structure

### Core Files
- `index.html` - Main HTML page with chat interface
- `style.css` - All CSS styles for the application
- `main.js` - Main application logic and chat functionality

### Modules
- `gemini-api.js` - Gemini AI API integration
- `generateMermaid.js` - Mermaid diagram generation
- `speakingTest.js` - Speaking test and pronunciation evaluation

## Speaking Test Module (`speakingTest.js`)

The speaking test functionality has been modularized for better maintainability. This module provides:

### Exported Functions
- `detectSpeakingTestIntent(message, conversationHistory)` - AI-powered intent detection
- `initiateSpeakingTest(addAssistantMessage, scrollToBottom, conversationHistory)` - Starts a speaking test
- `isSpeakingTestActive()` - Checks if a test is currently running

### Features
- AI-powered intent detection using Gemini
- Contextual understanding of follow-up requests
- Audio recording and analysis
- Automatic paragraph selection
- Real-time feedback and evaluation

### Usage in main.js
```javascript
import { detectSpeakingTestIntent, initiateSpeakingTest } from './speakingTest.js';

// Detect intent
const isSpeaking = await detectSpeakingTestIntent(message, conversationHistory);

// Initiate test
if (isSpeaking) {
  await initiateSpeakingTest(addAssistantMessage, scrollToBottom, conversationHistory);
}
```

## Dependencies
- `markdownit` - Markdown rendering
- `mermaid` - Diagram generation
- Native Web APIs:
  - MediaRecorder for audio recording
  - getUserMedia for microphone access
  - Fetch API for backend communication
