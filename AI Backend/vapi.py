from flask import Flask, request, jsonify
from vapi_python import Vapi
from dotenv import load_dotenv
import google.generativeai as genai
import os

load_dotenv()

app = Flask(__name__)
# Set the API key for Gemini
genai.configure(api_key=os.environ["API_KEY"])
vapi = Vapi(api_key='3661f60f-c3ea-4dfd-acf5-f4d302258e7a')

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    print(request.json.get("pdf_path"))
    # Path to the uploaded PDF file
    pdf_path = request.json.get("pdf_path")
    
    if not pdf_path:
        return jsonify({"error": "No PDF path provided"}), 400

    # Process the PDF and generate summary
    media = pathlib.Path(__file__).parents[1] / "third_party"
    model = genai.GenerativeModel("gemini-1.5-flash")
    sample_pdf = genai.upload_file(media / pdf_path)
    response = model.generate_content(["Give me a summary of this pdf file. Split it into two sections (each with 2 sentences). One section is 'Motivation' and the other is 'Background'", sample_pdf])

    # Return the generated summary
    return jsonify({"summary": response.text})


assistant = {
    'firstMessage': 'Would you like to start?',
    'context': 'You are an AI assistant that explains research papers concisely and in a easy to understand way. Your task is to provide clear and concise explanations at a high level of academic papers the user is interested in as if you were explaining the paper to an elementary school student with no prior knowledge of the topics.',
    'model': {
        'provider': 'groq',
        'model': 'llama-3.1-405b-reasoning',
        'knowledgeBase': {
            "provider": "canonical",
            "fileIds": ["8c4d6d2d-6cbd-4ca7-a54b-56791cffba7f"]
        },
    },
    'voice': {
        'provider': 'cartesia',
        'voiceId': '638efaaa-4d0c-442e-b701-3fae16aad012'
    },
    'interruptionsEnabled': False,
    'recordingEnabled': True,
    'endCallMessage': 'Thank you'
}

@app.route('/api/start-voicebot', methods=['POST'])
def start_voicebot():
    vapi.start(assistant=assistant)
    return jsonify({"message": "Voicebot started"}), 200

@app.route('/api/stop-voicebot', methods=['POST'])
def stop_voicebot():
    vapi.stop()
    return jsonify({"message": "Voicebot stopped"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)