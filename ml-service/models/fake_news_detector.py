import pandas as pd
import numpy as np
import re
import time
import os
import joblib
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import TreebankWordTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import VotingClassifier

# Ensure NLTK stopwords are downloaded
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class FakeNewsDetector:
    def __init__(self):
        self.vectorizer = None
        self.model = None
        self.stop_words = set(stopwords.words('english'))
        self.tokenizer = TreebankWordTokenizer()
        self.model_path = 'models/trained_model.pkl'
        self.vectorizer_path = 'models/vectorizer.pkl'

        print("✅ Initializing FakeNewsDetector...")
        self.load_model()

    def preprocess_text(self, text):
        """
        Clean and preprocess text data.
        """
        if not isinstance(text, str):
            return ""
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        tokens = self.tokenizer.tokenize(text)
        tokens = [word for word in tokens if word not in self.stop_words]
        return ' '.join(tokens)

    def train_model(self, data_path=None):
        """
        Train the fake news detection model.
        """
        print("📦 Training fake news detection model...")

        if data_path is None:
            sample_data = self.create_sample_data()
        else:
            sample_data = pd.read_csv(data_path, encoding='ISO-8859-1', low_memory=False)

            # Limit to 10k samples max
            sample_data = sample_data.sample(n=min(10000, len(sample_data)), random_state=42)

        # Drop invalid rows
        sample_data.dropna(subset=['text', 'label'], inplace=True)
        sample_data = sample_data[sample_data['text'].apply(lambda x: isinstance(x, str))]

        # Preprocess text
        sample_data['cleaned_text'] = sample_data['text'].apply(self.preprocess_text)

        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            stop_words='english'
        )

        X = self.vectorizer.fit_transform(sample_data['cleaned_text'])
        y = sample_data['label']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Ensemble model
        lr = LogisticRegression(random_state=42)
        svm = SVC(probability=True, random_state=42)
        knn = KNeighborsClassifier(n_neighbors=5)

        self.model = VotingClassifier(estimators=[
            ('lr', lr), ('svm', svm), ('knn', knn)
        ], voting='soft')

        self.model.fit(X_train, y_train)

        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)

        print(f"✅ Training Accuracy: {train_score:.4f}")
        print(f"✅ Testing Accuracy: {test_score:.4f}")

        self.save_model()

        return {
            "train_accuracy": train_score,
            "test_accuracy": test_score
        }

    def create_sample_data(self):
        """
        Create sample training data for demonstration.
        """
        fake_news = [
            "Scientists discover that drinking water is actually harmful to your health",
            "Breaking: Aliens have landed in New York City and are demanding pizza",
            "Government announces that gravity will be turned off next Tuesday",
            "Local man discovers that vegetables are actually made of plastic",
            "Study shows that reading fake news makes you 200% smarter"
        ]
        real_news = [
            "Stock market shows steady growth in technology sector this quarter",
            "New research reveals promising results for cancer treatment",
            "City council approves budget for new public transportation system",
            "Weather forecast predicts mild temperatures for the upcoming week",
            "University announces new scholarship program for underprivileged students"
        ]

        data = []
        for text in fake_news:
            data.append({'text': text, 'label': 1})
        for text in real_news:
            data.append({'text': text, 'label': 0})

        return pd.DataFrame(data)

    def predict(self, text):
        """
        Predict if given text is fake news.
        """
        start_time = time.time()

        if self.model is None or self.vectorizer is None:
            print("⚠️ Model or vectorizer not found. Training model...")
            self.train_model()

        cleaned_text = self.preprocess_text(text)
        text_vector = self.vectorizer.transform([cleaned_text])
        prediction = self.model.predict(text_vector)[0]
        confidence = max(self.model.predict_proba(text_vector)[0])
        processing_time = time.time() - start_time

        return {
            "prediction": "fake" if prediction == 1 else "real",
            "confidence": float(confidence),
            "model_used": "ensemble_classifier",
            "processing_time": processing_time
        }

    def save_model(self):
        """Save trained model and vectorizer."""
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.vectorizer, self.vectorizer_path)
        print("💾 Model and vectorizer saved to 'models/'")

    def load_model(self):
        """Load pre-trained model and vectorizer."""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path):
                self.model = joblib.load(self.model_path)
                self.vectorizer = joblib.load(self.vectorizer_path)
                print("✅ Pre-trained model loaded successfully!")
            else:
                print("ℹ️ No pre-trained model found. Will train on first use.")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.model = None
            self.vectorizer = None