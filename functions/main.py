# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

import firebase_functions
from firebase_functions import https_fn
from flask import Flask, jsonify, request, send_file, send_from_directory, Response, make_response
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional, Union, Generator, Tuple

DEFAULT_GENAI_MODEL = "models/gemini-2.5-flash"
web_dir = os.path.join(os.path.dirname(__file__), '..', 'web')


# Import our custom modules - handle optional dependencies
StudentDatabase = None
TalkingPointsGenerator = None
generate_meeting_agenda = None

# Try to import AI talking points (doesn't require Firebase)
try:
    # Try absolute import first (for Firebase Functions)
    from functions.ai_talking_points import TalkingPointsGenerator, generate_meeting_agenda
    AI_TALKING_POINTS_AVAILABLE = True
    print("✅ AI talking points module loaded")
except ImportError:
    try:
        # Try relative import (for local development)
        from ai_talking_points import TalkingPointsGenerator, generate_meeting_agenda
        AI_TALKING_POINTS_AVAILABLE = True
        print("✅ AI talking points module loaded")
    except ImportError as e:
        print(f"⚠️ AI talking points module not available: {e}")
        AI_TALKING_POINTS_AVAILABLE = False

# Try to import Firebase-dependent modules
try:
    # Try absolute import first (for Firebase Functions)
    from functions.firestore_integration import StudentDatabase
    FIREBASE_AVAILABLE = True
    print("✅ Firebase integration loaded")
except ImportError:
    try:
        # Try relative import (for local development)
        from firestore_integration import StudentDatabase
        FIREBASE_AVAILABLE = True
        print("✅ Firebase integration loaded")
    except ImportError as e:
        print(f"⚠️ Firebase integration not available: {e}")
        FIREBASE_AVAILABLE = False

# Try to import data generator (may have its own dependencies)
# Removed - synthetic data generation not needed anymore
DATA_GENERATOR_AVAILABLE = False

load_dotenv()


class StudentMeetingAPI:
    def __init__(self, app: Flask):
        self.app = app

        # Initialize only if modules are available
        self.talking_points_generator = None

        if AI_TALKING_POINTS_AVAILABLE and TalkingPointsGenerator:
            self.talking_points_generator = TalkingPointsGenerator()
            print("✅ AI talking points generator initialized")

        # Initialize database if Firebase is available
        self.db = None
        if FIREBASE_AVAILABLE and StudentDatabase:
            try:
                self.db = StudentDatabase()
                print("✅ Firestore database connected")
            except Exception as e:
                print(f"⚠️ Firestore connection failed: {e}")
                print("📝 Using local JSON files for data storage")

        self.setup_routes()

    def setup_routes(self):
        """Setup API routes for student management"""

        @self.app.route("/api/students", methods=["GET"])
        def get_students():
            """Get all students or filter by grade/teacher"""
            try:
                grade = request.args.get("grade")
                teacher_id = request.args.get("teacher_id")

                if self.db:
                    if grade:
                        students = self.db.get_students_by_grade(grade)
                    elif teacher_id:
                        students = self.db.get_students_by_teacher(teacher_id)
                    else:
                        # Get all students (limit to 50 for performance)
                        students = self.db.search_students(
                            "metadata.academicYear", "==", "2024-2025")[:50]
                else:
                    # Fallback to local JSON file
                    students = self.load_local_students()
                    if grade:
                        students = [s for s in students if s.get(
                            "personalInfo", {}).get("grade") == grade]

                return jsonify({
                    "success": True,
                    "data": students,
                    "count": len(students)
                })

            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/students/<student_id>", methods=["GET"])
        def get_student(student_id):
            """Get complete student profile including sub-collections"""
            try:
                if self.db:
                    student_data = self.db.get_complete_student_profile(
                        student_id)
                else:
                    # Fallback to local data
                    students = self.load_local_students()
                    student_data = next(
                        (s for s in students if s.get("studentId") == student_id), None)

                if not student_data:
                    return jsonify({"success": False, "error": "Student not found"}), 404

                return jsonify({
                    "success": True,
                    "data": student_data
                })

            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/students/<student_id>/talking-points", methods=["GET"])
        def generate_talking_points(student_id):
            """Generate AI talking points for a specific student"""
            try:
                # Get student data
                if self.db:
                    student_data = self.db.get_complete_student_profile(
                        student_id)
                else:
                    students = self.load_local_students()
                    student_data = next(
                        (s for s in students if s.get("studentId") == student_id), None)

                if not student_data:
                    return jsonify({"success": False, "error": "Student not found"}), 404

                # Generate talking points
                if self.talking_points_generator:
                    talking_points = self.talking_points_generator.generate_talking_points(
                        student_data)
                else:
                    return jsonify({"success": False, "error": "AI talking points module not available"}), 503

                # Generate meeting agenda
                if generate_meeting_agenda:
                    agenda = generate_meeting_agenda(talking_points)
                else:
                    agenda = {
                        "error": "Meeting agenda generation not available"}

                return jsonify({
                    "success": True,
                    "data": {
                        "talking_points": talking_points,
                        "meeting_agenda": agenda,
                        "generated_at": talking_points["meeting_summary"]["meeting_date"]
                    }
                })

            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/students/<student_id>/assessments", methods=["GET", "POST"])
        def handle_assessments(student_id: str) -> Union[Response, Tuple[Response, int]]:
            """Get or add student assessments"""
            if request.method == "GET":
                try:
                    limit = request.args.get("limit", type=int, default=10)

                    if self.db:
                        assessments = self.db.get_student_assessments(
                            student_id, limit)
                    else:
                        # Mock data for local testing
                        assessments = self.generate_mock_assessments(
                            student_id, limit)

                    return jsonify({
                        "success": True,
                        "data": assessments,
                        "count": len(assessments)
                    })

                except Exception as e:
                    return jsonify({"success": False, "error": str(e)}), 500

            elif request.method == "POST":
                try:
                    assessment_data = request.get_json()

                    if self.db:
                        assessment_id = self.db.add_assessment(
                            student_id, assessment_data)
                        return jsonify({
                            "success": True,
                            "data": {"assessment_id": assessment_id}
                        })
                    else:
                        return jsonify({"success": False, "error": "Database not available"}), 503

                except Exception as e:
                    return jsonify({"success": False, "error": str(e)}), 500

            # This should never be reached, but add it for type safety
            return jsonify({"success": False, "error": "Invalid request method"}), 405

        @self.app.route("/api/meeting-summary", methods=["POST"])
        def generate_meeting_summary():
            """Generate AI-powered meeting summary using Gemini"""
            try:
                req_data = request.get_json()
                student_id = req_data.get("student_id")
                additional_notes = req_data.get("notes", "")

                if not student_id:
                    return jsonify({"success": False, "error": "student_id is required"}), 400

                # Get student data and talking points
                if self.db:
                    student_data = self.db.get_complete_student_profile(
                        student_id)
                else:
                    students = self.load_local_students()
                    student_data = next(
                        (s for s in students if s.get("studentId") == student_id), None)

                if not student_data:
                    return jsonify({"success": False, "error": "Student not found"}), 404

                if self.talking_points_generator:
                    talking_points = self.talking_points_generator.generate_talking_points(
                        student_data)
                else:
                    return jsonify({"success": False, "error": "AI talking points module not available"}), 503

                # Prepare prompt for Gemini
                first_name = student_data['personalInfo']['firstName']
                last_name = student_data['personalInfo']['lastName']
                grade = student_data['personalInfo']['grade']

                prompt = f"""
As an experienced teacher, create a comprehensive parent-teacher meeting summary for:
Student: {first_name} {last_name} (Grade {grade})

Student Data Summary:
- Current GPA: {student_data.get('academicProfile', {}).get('currentGPA', 'N/A')}
- Attendance Rate: {student_data.get('behavioralProfile', {}).get('attendance', {}).get('attendanceRate', 'N/A')}
- Learning Style: {student_data.get('academicProfile', {}).get('learningStyle', 'N/A')}
- Participation Level: {student_data.get('behavioralProfile', {}).get('participation', {}).get('level', 'N/A')}

Key Talking Points:
{json.dumps(talking_points['talking_points_by_category'], indent=2)}

Additional Teacher Notes: {additional_notes}

Please create:
1. A warm, professional meeting summary
2. Key strengths to celebrate
3. Areas for growth with specific strategies
4. Action items for parents and teacher
5. Next steps and follow-up timeline

Keep the tone positive, constructive, and focused on the student's success.
"""

                # Use existing Gemini integration
                API_KEY = os.environ.get('GOOGLE_GENAI_API_KEY')
                if not API_KEY or API_KEY == 'TODO':
                    return jsonify({"success": False, "error": "Gemini API key not configured"}), 500

                model = genai.GenerativeModel("gemini-2.0-flash")
                response = model.generate_content(prompt)

                return jsonify({
                    "success": True,
                    "data": {
                        "meeting_summary": response.text,
                        "student_info": {
                            "name": f"{first_name} {last_name}",
                            "grade": grade,
                            "student_id": student_id
                        },
                        "talking_points": talking_points,
                        "generated_at": talking_points["meeting_summary"]["meeting_date"]
                    }
                })

            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/students/<student_id>/download-agenda", methods=["GET"])
        def download_agenda(student_id):
            """Download meeting agenda as a formatted text file"""
            try:
                # Get student data
                if self.db:
                    student_data = self.db.get_complete_student_profile(
                        student_id)
                else:
                    students = self.load_local_students()
                    student_data = next(
                        (s for s in students if s.get("studentId") == student_id), None)

                if not student_data:
                    return jsonify({"success": False, "error": "Student not found"}), 404

                # Get student info for filename
                first_name = student_data['personalInfo']['firstName']
                last_name = student_data['personalInfo']['lastName']

                # Generate talking points and agenda
                if self.talking_points_generator:
                    talking_points = self.talking_points_generator.generate_talking_points(
                        student_data)
                else:
                    return jsonify({"success": False, "error": "AI talking points module not available"}), 503

                # Generate meeting agenda
                if generate_meeting_agenda:
                    agenda_text = generate_meeting_agenda(talking_points)
                    # Convert to dict format for consistency
                    agenda = {
                        "title": f"Parent-Teacher Conference - {first_name} {last_name}",
                        "formatted_text": agenda_text,
                        "duration": "30 minutes"
                    }
                else:
                    # Create a basic agenda if the full generator isn't available
                    agenda = self.create_basic_agenda(
                        student_data, talking_points)

                # Use the pre-formatted text if available, otherwise format it
                if isinstance(agenda, dict) and 'formatted_text' in agenda:
                    agenda_content = agenda['formatted_text']
                else:
                    agenda_content = self.format_agenda_for_download(
                        student_data, agenda, talking_points)

                # Create filename
                filename = f"meeting_agenda_{first_name}_{last_name}_{talking_points['meeting_summary']['meeting_date'].replace(':', '-').replace(' ', '_')}.txt"

                # Return file as download
                response = make_response(agenda_content)
                response.headers['Content-Type'] = 'text/plain; charset=utf-8'
                response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response

            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

    def create_basic_agenda(self, student_data, talking_points):
        """Create a basic agenda when full generator isn't available"""
        first_name = student_data['personalInfo']['firstName']
        last_name = student_data['personalInfo']['lastName']
        grade = student_data['personalInfo']['grade']

        return {
            "title": f"Parent-Teacher Conference - {first_name} {last_name}",
            "duration": "30 minutes",
            "agenda_items": [
                {
                    "time": "5 minutes",
                    "topic": "Welcome & Introductions",
                    "description": "Brief welcome and agenda overview"
                },
                {
                    "time": "10 minutes",
                    "topic": "Academic Progress Review",
                    "description": "Discussion of grades, assignments, and academic strengths"
                },
                {
                    "time": "10 minutes",
                    "topic": "Behavioral & Social Development",
                    "description": "Classroom behavior, participation, and social interactions"
                },
                {
                    "time": "5 minutes",
                    "topic": "Next Steps & Action Items",
                    "description": "Goals and follow-up actions for student success"
                }
            ]
        }

    def format_agenda_for_download(self, student_data, agenda, talking_points):
        """Format the agenda as a readable text file"""
        first_name = student_data['personalInfo']['firstName']
        last_name = student_data['personalInfo']['lastName']
        grade = student_data['personalInfo']['grade']
        meeting_date = talking_points['meeting_summary']['meeting_date']

        # Use a list to collect all parts, then join them
        agenda_parts = [
            "PARENT-TEACHER CONFERENCE AGENDA",
            "=====================================",
            "",
            f"Student: {first_name} {last_name}",
            f"Grade: {grade}",
            f"Date: {meeting_date}",
            f"Duration: {agenda.get('duration', '30 minutes')}",
            "",
            "AGENDA OVERVIEW:",
            agenda.get('title', f'Conference for {first_name} {last_name}'),
            "",
            "MEETING STRUCTURE:"
        ]

        # Add agenda items
        if 'agenda_items' in agenda:
            for i, item in enumerate(agenda['agenda_items'], 1):
                agenda_parts.extend([
                    "",
                    f"{i}. {item.get('topic', 'Discussion Item')} ({item.get('time', '5 minutes')})",
                    f"   {item.get('description', '')}"
                ])

        # Add key talking points
        agenda_parts.extend([
            "",
            "",
            "KEY DISCUSSION POINTS:",
            "=====================",
            "",
            "ACADEMIC STRENGTHS:"
        ])

        academic_points = talking_points.get(
            'talking_points_by_category', {}).get('academic', [])
        for point in academic_points[:3]:  # Top 3 academic points
            if point.get('priority') in ['high', 'medium']:
                agenda_parts.append(f"• {point.get('point', '')}")

        agenda_parts.extend([
            "",
            "AREAS FOR GROWTH:"
        ])

        growth_points = [p for p in academic_points if 'improve' in p.get(
            'point', '').lower() or 'develop' in p.get('point', '').lower()]
        for point in growth_points[:2]:  # Top 2 growth areas
            agenda_parts.append(f"• {point.get('point', '')}")

        # Add behavioral insights
        behavioral_points = talking_points.get(
            'talking_points_by_category', {}).get('behavioral', [])
        if behavioral_points:
            agenda_parts.extend([
                "",
                "BEHAVIORAL OBSERVATIONS:"
            ])
            for point in behavioral_points[:3]:
                agenda_parts.append(f"• {point.get('point', '')}")

        # Add summary and goals
        agenda_parts.extend([
            "",
            "",
            "MEETING GOALS:",
            "=============",
            f"1. Celebrate {first_name}'s strengths and achievements",
            "2. Discuss any areas needing attention or support",
            "3. Align on strategies for continued growth",
            "4. Set clear action items for home and school",
            "",
            "NOTES SECTION:",
            "=============",
            "(Space for additional notes during the meeting)",
            "",
            "_________________________________________________",
            "",
            "_________________________________________________",
            "",
            "_________________________________________________",
            "",
            "_________________________________________________",
            "",
            "",
            "Generated by Sahayak Parent-Teacher Meeting Assistant"
        ])

        return '\n'.join(agenda_parts)

    def load_local_students(self) -> List[Dict[str, Any]]:
        """Load students from local JSON file as fallback"""
        try:
            with open("synthetic_students.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def generate_mock_assessments(self, student_id: str, limit: int) -> List[Dict[str, Any]]:
        """Generate mock assessment data for testing"""
        # Return mock data for testing purposes
        return [
            {
                "id": f"mock_{i}",
                "student_id": student_id,
                "subject": "Math",
                "score": 85,
                "date": "2024-01-01"
            } for i in range(limit)
        ]

# Update your existing main.py to include these new endpoints


def create_enhanced_app():
    """Create Flask app with enhanced student management features"""

    API_KEY = os.environ.get('GOOGLE_GENAI_API_KEY', 'TODO')
    if not API_KEY:
        raise ValueError(
            "API key not found. Please set the GOOGLE_GENAI_API_KEY environment variable.")

    genai.configure(api_key=API_KEY)
    app = Flask(__name__)

    # Original routes
    @app.route("/")
    def index():
        return send_from_directory(web_dir, 'index.html')

    @app.route("/api/generate", methods=["POST"])
    def generate_api() -> Union[Response, Tuple[Generator[str, None, None], Dict[str, str]]]:
        if request.method == "POST":
            if not API_KEY or API_KEY == 'TODO':
                return jsonify({"error": '''
                    To get started, get an API key at
                    https://g.co/ai/idxGetGeminiKey and enter it in
                    main.py
                    '''.replace('\n', '')})
            try:
                req_body = request.get_json()
                contents = req_body.get("contents")
                model_name = req_body.get("model")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(contents, stream=True)

                def stream() -> Generator[str, None, None]:
                    for chunk in response:
                        yield 'data: %s\n\n' % json.dumps({"text": chunk.text})

                return stream(), {'Content-Type': 'text/event-stream'}

            except Exception as e:
                return jsonify({"error": str(e)})

        # This should never be reached, but add it for type safety
        return jsonify({"error": "Invalid request method"})

    @app.route('/<path:path>')
    def static_files(path):
        return send_from_directory(web_dir, path)

    # Add student management API
    student_api = StudentMeetingAPI(app)

    @app.route("/api/generate_mermaid", methods=["POST"])
    def generate_mermaid():
        data = request.json
        if not data or not isinstance(data, dict):
            return jsonify({"error": "Invalid request data"}), 400
        prompt = data.get("prompt")

        if not data or not isinstance(data, dict):
            return jsonify({"error": "Invalid request data"}), 400
        prompt = data.get("prompt")
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400

        system_prompt = """
        You are a Mermaid diagram expert. Convert natural language descriptions into valid Mermaid diagram syntax.

        CRITICAL RULES:
        1. Return ONLY the Mermaid code, no explanations or markdown formatting
        2. Start directly with the diagram type (flowchart, sequenceDiagram, etc.)
        3. Use proper Mermaid syntax - NEVER use semicolons (;) in flowcharts
        4. Make the diagram clear and well-structured
        5. Each edge must be on a new line
        6. Avoid malformed connections
        """

        full_prompt = f"{system_prompt}\n\nUser request: \"{prompt}\"\n\nMermaid diagram:"
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(full_prompt)

            text = response.text.strip() if response.text else ""
            # Remove markdown and code blocks
            text = (
                text.replace("```mermaid", "")
                    .replace("```", "")
                    .strip()
            )
            # Process the diagram content
            lines = text.splitlines()
            processed_lines = []

            for line in lines:
                line = line.strip()
                if line.startswith("graph"):
                    processed_lines.append("graph LR")  # Force left-to-right layout
                elif "-->" in line:
                    parts = line.split("-->")
                    if len(parts) == 2:
                        source = parts[0].strip()
                        target = parts[1].strip()

                        # Clean up nodes and ensure proper ID-label format
                        def clean_node(node):
                            import re
                            # Remove any special characters and extra spaces
                            node = node.strip().replace(";", "")

                            # Try to extract existing ID and label if present
                            id_label_match = re.match(r'([A-Za-z0-9_]+)\s*\[(.*?)\]', node)

                            if id_label_match:
                                # If node already has ID and label format
                                node_id = id_label_match.group(1)
                                label = id_label_match.group(2).strip()
                            else:
                                # If it's just text or incorrectly formatted
                                # Clean up any existing brackets
                                clean_text = re.sub(r'[\[\]\(\)\{\}]', '', node).strip()
                                # Create an ID from the text
                                node_id = re.sub(r'[^A-Za-z0-9_]', '', clean_text.lower())
                                label = clean_text

                            # Ensure we have a valid ID
                            if not node_id:
                                node_id = f"node_{len(processed_lines)}"

                            # Return properly formatted node with ID and label
                            return f"{node_id}[{label}]"

                        source = clean_node(source)
                        target = clean_node(target)

                        processed_lines.append(f"{source} --> {target}")

            # Create the final diagram
            diagram = "\n".join(processed_lines)

            # Log the generated diagram for debugging
            print("Generated Mermaid diagram:", diagram)
                        
            # Only keep the diagram part
            lines = text.splitlines()
            # Find the graph LR line
            graph_start = next((i for i, l in enumerate(lines) if l.strip() == "graph LR"), 0)
            diagram_lines = ["graph LR"]  # Start with clean graph LR
            
            # Process each line after graph LR
            for line in lines[graph_start + 1:]:
                line = line.strip()
                # Skip empty lines, comments, and non-diagram content
                if not line or line.startswith("%") or ":" in line:
                    continue
                    
                # Clean up the line
                clean_line = (
                    line.strip()
                        .replace(";", "")  # Remove semicolons
                        .replace("  ", " ")  # Remove double spaces
                )
                # Only add lines that match the expected format: X --> Y or X[Label] --> Y[Label]
                if "-->" in clean_line:
                    parts = clean_line.split("-->")
                    if len(parts) == 2:
                        # Ensure proper spacing around arrow
                        clean_line = f"{parts[0].strip()} --> {parts[1].strip()}"
                        diagram_lines.append(clean_line)            
            # Join the lines with proper newlines
            diagram = "\n".join(diagram_lines)
            
            # Log the final diagram for debugging
            print("Final processed diagram:", diagram)

            return jsonify({"diagram": diagram})

        except Exception as e:
            print("Error in generate_mermaid:", e)  # Debug log
            return jsonify({"error": str(e)}), 500

    @app.route("/api/analyze_reading", methods=["POST"])
    def analyze_reading_api():
        if 'audio_file' not in request.files:
            return jsonify({"error": "No audio file found"}), 400

        audio_file = request.files['audio_file']
        original_text = request.form.get('original_text')

        if not original_text:
            return jsonify({"error": "Original text is missing"}), 400

        try:
            # Read the audio bytes directly to send them inline
            audio_bytes = audio_file.read()

            model = genai.GenerativeModel(DEFAULT_GENAI_MODEL)

            # Send audio data inline with the prompt for transcription
            transcription_response = model.generate_content([
                "Transcribe the following audio.",
                {"mime_type": "audio/webm", "data": audio_bytes}
            ])
            transcribed_text = transcription_response.text

            analysis_prompt = f"""
            You are an expert English pronunciation and reading coach.
            A student was asked to read the following text:
            ---
            Original Text: "{original_text}"
            ---
            The student's reading was transcribed from audio as:
            ---
            Student's Transcription: "{transcribed_text}"
            ---
            Please analyze the student's performance. Compare the original text with the student's transcription to identify any errors (missed words, mispronounced words, extra words).

            Provide your feedback in a markdown format with the following sections:
            - **Overall Score**: A score out of 100 based on accuracy, fluency, and clarity.
            - **Feedback**: Specific, constructive feedback.
            - **Corrections**: The student's transcription with corrections.
            """

            analysis_response = model.generate_content(analysis_prompt)

            return jsonify({"analysis": analysis_response.text})

        except Exception as e:
            print(f"An error occurred: {e}")
            return jsonify({"error": str(e)}), 500

    return app


if __name__ == "__main__":
    app = create_enhanced_app()
    print("🚀 Enhanced Sahayak API with Parent-Teacher Meeting features starting...")
    print("📚 Available endpoints:")
    print("   GET  /api/students - List all students")
    print("   GET  /api/students/<id> - Get student details")
    print("   GET  /api/students/<id>/talking-points - Generate AI talking points")
    print("   GET  /api/students/<id>/download-agenda - Download meeting agenda")
    print("   POST /api/meeting-summary - Generate AI meeting summary")
    app.run(debug=True, port=5000)

# Create the Flask app instance
app = create_enhanced_app()

# Expose the Flask app as an HTTP function


@https_fn.on_request()
def sahayak(req: https_fn.Request) -> https_fn.Response:
    with app.request_context(req.environ):
        return app.full_dispatch_request()
