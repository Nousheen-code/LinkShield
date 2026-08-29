from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import re
import numpy as np

app = Flask(__name__)
CORS(app)

# Load trained model
try:
    model = joblib.load('phishing_model.pkl')
    print("✅ Trained model loaded!")
except:
    print("⚠️ No trained model - using fallback")
    model = None

def extract_url_features(url): # Same as training
    features = {}
    features['url_length'] = len(url)
    features['domain_length'] = len(re.sub(r'https?://|www\.', '', url).split('/')[0])
    features['has_ip'] = 1 if re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', url) else 0
    features['https'] = 1 if url.startswith('https') else 0
    features['suspicious_keywords'] = sum(1 for k in ['login','bank','verify','paypal','account'] if k in url.lower())
    features['subdomain_count'] = len(re.sub(r'https?://www\.', '', url).split('.')[:-2])
    features['dot_count'] = url.count('.')
    features['slash_count'] = url.count('/')
    features['has_query'] = 1 if '?' in url else 0
    features['shortener'] = 1 if any(s in url.lower() for s in ['bit.ly','tinyurl','t.co']) else 0
    features['free_tld'] = 1 if any(t in url.lower() for t in ['.tk','.ml','.ga','.cf']) else 0
    features['double_slash'] = 1 if '//' in url[8:] else 0
    features['numeric_domain'] = 1 if re.search(r'\d+\.\d+', url) else 0
    return features

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    url = data.get('url', '')
    
    features_dict = extract_url_features(url)
    feature_cols = ['url_length', 'domain_length', 'has_ip', 'https', 'suspicious_keywords',
                   'subdomain_count', 'dot_count', 'slash_count', 'has_query', 
                   'shortener', 'free_tld', 'double_slash', 'numeric_domain']
    feature_vector = np.array([features_dict[col] for col in feature_cols]).reshape(1, -1)
    
    if model:
        pred = model.predict(feature_vector)[0]
        conf = model.predict_proba(feature_vector)[0].max()
    else:
        score = sum(feature_vector[0][i] * 0.08 for i in range(len(feature_vector[0])))
        pred = 1 if score > 0.5 else 0
        conf = score if pred == 1 else 1-score
    
    return jsonify({
        'prediction': int(pred),
        'confidence': round(float(conf * 100), 1),
        'features': {k: v for k, v in features_dict.items()}
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)