"""
Enhanced Intelligent Ticket Intent Classifier and Routing Engine
Classifies customer incoming messages into correct categories and routes them to appropriate teams,
reducing transfer friction and speeding up first-response time.
"""

import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

TEAM_ROUTING_MAP = {
    'Delivery & Shipping': 'Logistics',
    'Returns & Refunds': 'Returns Desk',
    'Billing & Payments': 'Billing',
    'Warranty & Repair': 'Escalations & Warranty (Tier 2)',
    'Charging & Battery': 'Escalations & Warranty (Tier 2)',
    'Connectivity': 'Chat/Voice Frontline (Tier 1)',
    'Audio Quality': 'Chat/Voice Frontline (Tier 1)',
    'App & Firmware': 'Chat/Voice Frontline (Tier 1)',
    'Account & Login': 'Chat Frontline (Tier 1)',
    'Product Enquiry': 'Chat Frontline (Tier 1)',
    'Other': 'Chat Frontline (Tier 1)'
}

KEYWORD_RULES = [
    (r'\b(pair|pairing|disconnect|disconnects|stutter|stutters|bluetooth drop|unpair|won\'t pair|not pairing)\b', 'Connectivity'),
    (r'\b(charge|charging|battery|drain|draining|case not charging|won\'t turn on|dead on arrival|doa)\b', 'Charging & Battery'),
    (r'\b(firmware|app|update stuck|app crash|sync failed)\b', 'App & Firmware'),
    (r'\b(distort|crackl|static|sound low|mic low|volume low|one ear mute|crackling)\b', 'Audio Quality'),
    (r'\b(refund|return|pickup|qc|rto|money back)\b', 'Returns & Refunds'),
    (r'\b(courier|tracking|deliv|ship|dispatch|transit|where is my order|not delivered)\b', 'Delivery & Shipping'),
    (r'\b(card charged|double charged|duplicate payment|invoice|deducted twice|payment failed)\b', 'Billing & Payments'),
    (r'\b(warranty claim|broken|hardware fault|damaged in box|physical defect)\b', 'Warranty & Repair'),
    (r'\b(login|otp|password|account reset|cannot login)\b', 'Account & Login')
]

def clean_text(text):
    if pd.isnull(text):
        return ""
    text = str(text).lower()
    text = re.sub(r'\[ivr transcript\]', ' ', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

class TicketClassifier:
    def __init__(self):
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                ngram_range=(1, 2),
                max_features=6000,
                stop_words='english',
                sublinear_tf=True
            )),
            ('clf', LogisticRegression(
                max_iter=1000,
                class_weight='balanced',
                C=2.5,
                random_state=42
            ))
        ])
        self.is_trained = False
        self.classes_ = []

    def train(self, tickets_df):
        valid = tickets_df.dropna(subset=['customer_message', 'category']).copy()
        valid['cleaned_msg'] = valid['customer_message'].apply(clean_text)
        valid = valid[valid['cleaned_msg'].str.len() > 3]
        
        X = valid['cleaned_msg']
        y = valid['category']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        self.pipeline.fit(X_train, y_train)
        self.is_trained = True
        self.classes_ = list(self.pipeline.classes_)
        
        y_pred = self.pipeline.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)
        
        return {
            'accuracy': acc,
            'report': report,
            'test_size': len(y_test),
            'train_size': len(y_train),
            'X_test': X_test,
            'y_test': y_test,
            'y_pred': y_pred
        }

    def predict(self, text):
        if not self.is_trained:
            raise ValueError("Model is not trained yet.")
        c_text = clean_text(text)
        if len(c_text) < 2:
            return {
                'category': 'Other',
                'team': TEAM_ROUTING_MAP['Other'],
                'confidence': 0.0
            }
            
        # Check rule match
        rule_cat = None
        for pattern, cat in KEYWORD_RULES:
            if re.search(pattern, c_text):
                rule_cat = cat
                break

        probs = self.pipeline.predict_proba([c_text])[0]
        max_prob_idx = np.argmax(probs)
        ml_cat = self.pipeline.classes_[max_prob_idx]
        conf = float(probs[max_prob_idx])
        
        final_cat = ml_cat
        if rule_cat is not None:
            # If rule fires, unless ML has >0.85 confidence on something else, favor rule
            if conf < 0.85 or ml_cat == 'Other' or ml_cat == 'Product Enquiry':
                final_cat = rule_cat
                conf = max(conf, 0.85)
            
        return {
            'category': final_cat,
            'team': TEAM_ROUTING_MAP.get(final_cat, 'Chat Frontline'),
            'confidence': conf
        }

if __name__ == '__main__':
    from data_loader import load_and_preprocess_data
    data = load_and_preprocess_data()
    clf = TicketClassifier()
    eval_res = clf.train(data['tickets'])
    print(f"Classifier trained successfully! Test Accuracy: {eval_res['accuracy']:.4f}")
    sample_text = "pairing is not working with my phone, bluetooth disconnects"
    print(f"Prediction for '{sample_text}':", clf.predict(sample_text))
