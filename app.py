from flask import Flask, request, Response, jsonify
import speech_recognition as sr
import os
from googletrans import Translator
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
translator = Translator()  # Initialize the translator

# Function to recognize Bangla speech from an audio file
def recognize_speech(file_path, language_code='bn-BD'):
    wav_file = file_path # Convert file to WAV if necessary
    print("wav file here :" + wav_file)
    r = sr.Recognizer()  # Initialize recognizer

    # Load the audio file
    with sr.AudioFile(wav_file) as source:
        audio_data = r.record(source)

    # Recognize the speech using Google Web Speech API
    try:
        text = r.recognize_google(audio_data, language=language_code)
        print("Recognized text:", text)
        return text
    except sr.UnknownValueError:
        return "Google Speech Recognition could not understand the audio"
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"

# Function to translate text from Bangla to Chinese
def translate_bangla_to_chinese(bangla_text):
    translated = translator.translate(bangla_text, src='bn', dest='zh-cn')
    return translated.text

# Function to translate text from Chinese to Bangla
def translate_chinese_to_bangla(chinese_text):
    translated = translator.translate(chinese_text, src='zh-cn', dest='bn')
    return translated.text

# Route to handle POST request for Bangla to Chinese translation
@app.route('/bangla_voice_to_chinese_voice', methods=['POST'])
def bangla_voice_to_chinese_voice():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        file_path = os.path.join('./uploads', file.filename)
        file.save(file_path)

        # Recognize Bangla speech
        recognized_text = recognize_speech(file_path, language_code='bn-BD')
        
        # Translate recognized Bangla text to Chinese
        chinese_text = translate_bangla_to_chinese(recognized_text)

        # Delete the file after processing
        os.remove(file_path)

        # Return the Chinese translation
        response = Response(chinese_text, content_type='application/json')
        return response, 200

# Route to handle POST request for Chinese to Bangla translation
@app.route('/chinese_voice_to_bangla', methods=['POST'])
def chinese_voice_to_bangla():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        file_path = os.path.join('./uploads', file.filename)
        file.save(file_path)

        # Recognize Chinese speech
        recognized_text = recognize_speech(file_path, language_code='zh-cn')
        
        # Translate recognized Chinese text to Bangla
        bangla_text = translate_chinese_to_bangla(recognized_text)

        # Delete the file after processing
        os.remove(file_path)

        # Return the Bangla translation
        response = Response(bangla_text, content_type='application/json')
        return response, 200

if __name__ == '__main__':
    os.makedirs('./uploads', exist_ok=True)  # Create uploads directory if it doesn't exist
    app.run(debug=True)
