from flask import Flask, render_template, request, jsonify, Response
import cv2
import dlib
import numpy as np
import requests

app = Flask(_name_)

# LanguageTool API for grammar checking
LANGUAGETOOL_URL = "https://api.languagetool.org/v2/check"

# Dlib face detector and landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

eye_status = "Neutral"
tracking_enabled = False  # Toggle for eye tracking

def detect_eye_movement():
    global eye_status, tracking_enabled
    cap = cv2.VideoCapture(0)

    while tracking_enabled:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        for face in faces:
            landmarks = predictor(gray, face)

            left_eye_x = (landmarks.part(36).x + landmarks.part(39).x) // 2
            right_eye_x = (landmarks.part(42).x + landmarks.part(45).x) // 2
            screen_center_x = frame.shape[1] // 2

            # Detect Convergence & Divergence
            if left_eye_x < screen_center_x and right_eye_x > screen_center_x:
                eye_status = "Converging (Focused)"
            elif left_eye_x > screen_center_x and right_eye_x < screen_center_x:
                eye_status = "Diverging (Looking Away)"
            else:
                eye_status = "Neutral"

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/start_eye_tracking', methods=['POST'])
def start_eye_tracking():
    global tracking_enabled
    tracking_enabled = True
    return jsonify({"message": "Eye tracking started"})

@app.route('/stop_eye_tracking', methods=['POST'])
def stop_eye_tracking():
    global tracking_enabled
    tracking_enabled = False
    return jsonify({"message": "Eye tracking stopped"})

@app.route('/video_feed')
def video_feed():
    return Response(detect_eye_movement(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_eye_status')
def get_eye_status():
    return jsonify({"eye_status": eye_status})

@app.route('/check_grammar', methods=["POST"])
def check_grammar():
    text = request.json.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    params = {"text": text, "language": "en-US"}
    response = requests.post(LANGUAGETOOL_URL, data=params)
    data = response.json()

    corrections = [
        {"message": match["message"], "replacement": match["replacements"][0]["value"]}
        for match in data.get("matches", []) if match["replacements"]
    ]

    # Judgment based on the number of mistakes
    num_mistakes = len(corrections)
    if num_mistakes == 0:
        judgment = "✅ Excellent! No mistakes detected."
    elif num_mistakes <= 2:
        judgment = "⚠ Good, but a few minor mistakes."
    else:
        judgment = "❌ Needs Improvement! Several grammar mistakes found."

    return jsonify({"text": text, "corrections": corrections, "judgment": judgment})

if __name__ == "_main_":
    app.run(debug=True)
# from flask import Flask, render_template, request, jsonify, Response
# import cv2
# import dlib
# import numpy as np
# import requests

# app = Flask(_name_)

# # LanguageTool API for grammar checking
# LANGUAGETOOL_URL = "https://api.languagetool.org/v2/check"

# # Dlib face detector and landmark predictor
# detector = dlib.get_frontal_face_detector()
# predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# eye_status = "Neutral"
# tracking_enabled = False  # Toggle for eye tracking

# def detect_eye_movement():
#     global eye_status, tracking_enabled
#     cap = cv2.VideoCapture(0)

#     while tracking_enabled:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         faces = detector(gray)

#         for face in faces:
#             landmarks = predictor(gray, face)

#             left_eye_x = (landmarks.part(36).x + landmarks.part(39).x) // 2
#             right_eye_x = (landmarks.part(42).x + landmarks.part(45).x) // 2

#             # Detect Convergence & Divergence
#             if left_eye_x > right_eye_x:  # Eyes moving inward (converging)
#                 eye_status = "Converging (Focused)"
#             elif left_eye_x < right_eye_x:  # Eyes moving outward (diverging)
#                 eye_status = "Diverging (Looking Away)"
#             else:
#                 eye_status = "Neutral"

#         _, buffer = cv2.imencode('.jpg', frame)
#         frame_bytes = buffer.tobytes()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

#     cap.release()

# @app.route('/')
# def index():
#     return render_template("index.html")

# @app.route('/start_eye_tracking', methods=['POST'])
# def start_eye_tracking():
#     global tracking_enabled
#     tracking_enabled = True
#     return jsonify({"message": "Eye tracking started"})

# @app.route('/stop_eye_tracking', methods=['POST'])
# def stop_eye_tracking():
#     global tracking_enabled
#     tracking_enabled = False
#     return jsonify({"message": "Eye tracking stopped"})

# @app.route('/video_feed')
# def video_feed():
#     return Response(detect_eye_movement(), mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/get_eye_status')
# def get_eye_status():
#     return jsonify({"eye_status": eye_status})

# @app.route('/check_grammar', methods=["POST"])
# def check_grammar():
#     text = request.json.get("text", "")
#     if not text:
#         return jsonify({"error": "No text provided"}), 400

#     params = {"text": text, "language": "en-US"}
#     response = requests.post(LANGUAGETOOL_URL, data=params)
#     data = response.json()

#     corrections = [
#         {"message": match["message"], "replacement": match["replacements"][0]["value"]}
#         for match in data.get("matches", []) if match["replacements"]
#     ]

#     # Judgment based on the number of mistakes
#     num_mistakes = len(corrections)
#     if num_mistakes == 0:
#         judgment = "✅ Excellent! No mistakes detected."
#     elif num_mistakes <= 2:
#         judgment = "⚠ Good, but a few minor mistakes."
#     else:
#         judgment = "❌ Needs Improvement! Several grammar mistakes found."

#     return jsonify({"text": text, "corrections": corrections, "judgment": judgment})

# if _name_ == "_main_":
#     app.run(debug=True)
