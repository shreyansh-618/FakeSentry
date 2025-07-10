from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import joblib
import pandas as pd
from models.fake_news_detector import FakeNewsDetector

load_dotenv()

app = Flask(__name__)
CORS(app)

detector = FakeNewsDetector()

@app.route('/health', methods=['GET'])
def health_check():
    """HEALTH CHECK ENDPOINT"""
    return jsonify({"status": "healthy", "service": "ML Fake News Detection"})

@app.route('/predict', methods=['POST'])
def predict_news():
    """PREDICT IF NEWS IS FAKE OR REAL
    EXPECTED INPUT: {"text" : "news article content"}
    """
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "Missing 'text' field in request"}), 400
        news_text = data['text']
        
        if not hasattr(detector, 'model') or detector.model is None:
            return jsonify({"error": "Model not loaded or trained yet"}), 500
        
        if not news_text.strip():
            return jsonify({"error": "Empty text provided"}), 400
        result = detector.predict(news_text)
        
        return jsonify({
            "prediction": result['prediction'],
            "confidence": result['confidence'],
            "model_used": result['model_used'],
            "processing_time": result['processing_time']
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/retrain', methods=['POST'])
def retrain_model():
    """ENDPOINT TO RETRAIN THE MODEL WITH NEW DATA"""
    try:
        return jsonify({"message": "Model retraining initiated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    port = int(os.getenv('ML_SERVICE_PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)