from flask import Flask, jsonify, request, send_file, send_from_directory
import google.genai as genai
import json
import os
from dotenv import load_dotenv

load_dotenv()


API_KEY = os.environ.get('GOOGLE_GENAI_API_KEY',
                         'TODO')
if not API_KEY:
    raise ValueError(
        "API key not found. Please set the GOOGLE_GENAI_API_KEY environment variable.")

ai = genai.Client(api_key=API_KEY)
app = Flask(__name__)


@app.route("/")
def index():
    return send_file('web/index.html')


@app.route("/api/generate", methods=["POST"])
def generate_api():
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
            response = ai.models.generate_content_stream(
                model=req_body.get("model"), contents=contents)

            def stream():
                for chunk in response:
                    yield 'data: %s\n\n' % json.dumps({"text": chunk.text})

            return stream(), {'Content-Type': 'text/event-stream'}

        except Exception as e:
            return jsonify({"error": str(e)})


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('web', path)


if __name__ == "__main__":
    app.run(port=int(os.environ.get('PORT', 5000)), debug=True)
