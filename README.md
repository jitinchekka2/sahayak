# Sahayak - AI-Powered Teaching Assistant

Sahayak is an AI-powered assistant designed to help teachers prepare for and conduct effective parent-teacher meetings. It analyzes student data to generate personalized talking points, meeting agendas, and summaries.

## Project Overview

Sahayak offers the following key features:

- **AI-Generated Talking Points**: Automatically analyzes student data to identify key discussion points categorized by academic performance, behavioral aspects, social development, and goals.
- **Meeting Dashboard**: An intuitive interface for teachers to select students and view personalized talking points.
- **Downloadable Meeting Agendas**: Generate and download structured meeting agendas for each student.
- **AI Meeting Summaries**: Generate comprehensive meeting summaries using Gemini AI.
- **Speaking Practice**: Interactive speaking test and pronunciation evaluation for students.
- **Mermaid Integration**: Visualize student data and meeting agendas using Mermaid diagrams.

## Architecture

The project uses a modern web architecture:

- **Frontend**: HTML, CSS, JavaScript for the web interface
- **Backend**: Python with Flask for API endpoints
- **Database**: Firestore for student data storage
- **AI**: Google's Gemini AI for generating talking points and summaries

## Project Structure

```
├── functions/              # Backend Python code
│   ├── ai_talking_points.py   # AI talking points generation logic
│   ├── firestore_integration.py  # Database integration
│   ├── main.py             # Flask application and API endpoints
│   └── requirements.txt    # Python dependencies
├── web/                    # Frontend assets
│   ├── index.html          # Main application page
│   ├── meeting_dashboard.html  # Parent-teacher meeting dashboard
│   ├── main.js             # Main application JavaScript
│   ├── gemini-api.js       # Gemini API integration
│   ├── speakingTest.js     # Speaking test functionality
│   └── style.css           # Application styles
└── firebase.json           # Firebase configuration
```

## Getting Started

### Prerequisites

- Python 3.9+
- Firebase account
- Google Gemini API key

### Installation

1. Clone the repository
2. Install Python dependencies:
   ```
   cd functions
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```
   # In functions/.env
   GOOGLE_GENAI_API_KEY=your_gemini_api_key
   ```

4. Deploy to Firebase:
   ```
   firebase deploy
   ```

## Usage

Access the deployed application at: [https://agentic-ai-hackathon-467108.web.app/meeting_dashboard.html](https://agentic-ai-hackathon-467108.web.app/meeting_dashboard.html)

1. Navigate to the Meeting Dashboard
2. Select a student from the list
3. View automatically generated talking points
4. Generate AI summaries or download meeting agendas as needed

## API Endpoints

- `GET /api/students` - List all students
- `GET /api/students/<id>` - Get student details
- `GET /api/students/<id>/talking-points` - Generate AI talking points
- `GET /api/students/<id>/download-agenda` - Download meeting agenda
- `POST /api/meeting-summary` - Generate AI meeting summary

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python, Flask
- **Database**: Firebase Firestore
- **AI**: Google Generative AI (Gemini)
- **Deployment**: Firebase Hosting and Functions

## License

This project is licensed under the MIT