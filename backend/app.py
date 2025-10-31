# conda activate tfenv 
# curl -X POST -F "file=@/Users/perspectfaiz/Desktop/Apple.jpg" http://127.0.0.1:5000/predict

from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
import cv2
import os
from dotenv import load_dotenv

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

# -----------------------------
# Configuration
# -----------------------------
MODEL_PATH = "model/model.h5"
FLASK_HOST = os.getenv('FLASK_HOST', '127.0.0.1')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

# -----------------------------
# Initialize Flask app
# -----------------------------
app = Flask(__name__)
CORS(app)

# -----------------------------
# Load the trained model
# -----------------------------
model = tf.keras.models.load_model(MODEL_PATH)
print("✅ Model loaded successfully from:", MODEL_PATH)

# -----------------------------
# Class Names (must match your training dataset)
# -----------------------------
disease_names = [
    'Apple___Apple_scab',
    'Apple___Black_rot',
    'Apple___Cedar_apple_rust',
    'Apple___healthy',
    'Blueberry___healthy',
    'Cherry_(including_sour)___Powdery_mildew',
    'Cherry_(including_sour)___healthy',
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
    'Corn_(maize)___Common_rust_',
    'Corn_(maize)___Northern_Leaf_Blight',
    'Corn_(maize)___healthy',
    'Grape___Black_rot',
    'Grape___Esca_(Black_Measles)',
    'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
    'Grape___healthy',
    'Orange___Haunglongbing_(Citrus_greening)',
    'Peach___Bacterial_spot',
    'Peach___healthy',
    'Pepper,_bell___Bacterial_spot',
    'Pepper,_bell___healthy',
    'Potato___Early_blight',
    'Potato___Late_blight',
    'Potato___healthy',
    'Raspberry___healthy',
    'Soybean___healthy',
    'Squash___Powdery_mildew',
    'Strawberry___Leaf_scorch',
    'Strawberry___healthy',
    'Tomato___Bacterial_spot',
    'Tomato___Early_blight',
    'Tomato___Late_blight',
    'Tomato___Leaf_Mold',
    'Tomato___Septoria_leaf_spot',
    'Tomato___Spider_mites Two-spotted_spider_mite',
    'Tomato___Target_Spot',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
    'Tomato___Tomato_mosaic_virus',
    'Tomato___healthy'
]


# -----------------------------
# Routes
# -----------------------------
@app.route('/')
def home():
    return "Flask backend (memory-based) is running!, send a POST request to /predict to predict the disease, for example: curl -X POST -F 'file=@/Users/userName/Desktop/Apple.jpg' http://PORT/predict" 


@app.route('/predict', methods=['POST'])
def predict():
    # Check for uploaded file
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'})

    try:
        # ----------------------------------------
        # Memory-based image reading (no disk use)
        # ----------------------------------------
        file_bytes = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({'error': 'Invalid image file'})

        # Convert to RGB and resize
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(img, (128, 128))

        # Convert to array and batchify
        input_arr = np.expand_dims(img_resized, axis=0)

        # Predict
        predictions = model.predict(input_arr)
        result_index = int(np.argmax(predictions[0]))
        confidence = round(float(np.max(predictions[0])) * 100, 2)
        predicted_label = disease_names[result_index] if result_index < len(disease_names) else "Unknown"

        print(f"Prediction index: {result_index}, Label: {predicted_label}, Confidence: {confidence}")

        return jsonify({
            'predicted_index': result_index,
            'predicted_disease': predicted_label,
            'confidence': confidence
        })

    except Exception as e:
        print("Error during prediction:", str(e))
        return jsonify({'error': str(e)})


# -----------------------------
# Main Entry
# -----------------------------
if __name__ == '__main__':
    print(f"🚀 Starting Flask server on {FLASK_HOST}:{FLASK_PORT} (debug={FLASK_DEBUG})")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
