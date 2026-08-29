import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import re

# ✅ FIXED: Define extract_url_features FIRST
def extract_url_features(url):
    """Extract features for ML training"""
    features = {}
    
    # All 13 features your model TO BE expects
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

# ✅ FIXED: urls (plural) + more data
def create_sample_dataset():
    """Create complete training dataset"""
    urls = [
        # Safe URLs (label 0)
        'https://google.com', 'https://github.com', 'https://stackoverflow.com',
        'https://amazon.com', 'https://microsoft.com', 'https://facebook.com',
        # Phishing URLs (label 1)
        'http://192.168.1.1.login-bank.com', 'https://paypal-login.tk/verify',
        'http://bit.ly/suspicious', 'https://secure-bank.ml/update-account',
        'https://login-bank-secure.gq/verify', 'http://free-bank.cf/account'
    ]
    
    labels = [0,0,0,0,0,0, 1,1,1,1,1,1]
    
    features_list = []
    for url, label in zip(urls, labels):
        feats = extract_url_features(url)
        feats['label'] = label
        features_list.append(feats)
    
    return pd.DataFrame(features_list)

# ✅ Train model
def train_model():
    print("🎓 Training Phishing Detection Model...")
    
    df = create_sample_dataset()
    print(f"📊 Dataset: {len(df)} samples")
    print(df.head())
    
    # All feature columns
    feature_cols = ['url_length', 'domain_length', 'has_ip', 'https', 'suspicious_keywords',
                   'subdomain_count', 'dot_count', 'slash_count', 'has_query', 
                   'shortener', 'free_tld', 'double_slash', 'numeric_domain']
    
    X = df[feature_cols].fillna(0)
    y = df['label']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # Train Random Forest
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n✅ Model Accuracy: {accuracy:.3f}")
    print("\n📈 Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save model
    joblib.dump(model, 'phishing_model.pkl')
    print("\n💾 Model saved: phishing_model.pkl")
    
    return model

if __name__ == '__main__':
    train_model()
    print("\n🎉 Training COMPLETE! Use phishing_model.pkl in app.py")