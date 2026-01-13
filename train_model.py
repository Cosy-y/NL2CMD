import json
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import numpy as np

def load_training_data(filepath: str = 'training_data_enhanced.json'):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading training data: {e}")
        # Try fallback to original
        try:
            with open('training_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except:
            return None

def prepare_dataset(data):
    """
    Prepare training dataset from JSON data
    
    Returns:
        queries: List of natural language queries
        intents: List of intent labels
        intent_to_command: Mapping of intent to command for each OS
    """
    queries = []
    intents = []
    intent_to_command = {}
    
    # Process Windows commands
    for item in data.get('windows', []):
        query = item['query']
        intent = item['intent']
        command = item['command']
        
        queries.append(query)
        intents.append(intent)
        
        # Store intent to command mapping
        key = f"windows_{intent}"
        if key not in intent_to_command:
            intent_to_command[key] = command
    
    # Process Linux commands
    for item in data.get('linux', []):
        query = item['query']
        intent = item['intent']
        command = item['command']
        
        queries.append(query)
        intents.append(intent)
        
        # Store intent to command mapping
        key = f"linux_{intent}"
        if key not in intent_to_command:
            intent_to_command[key] = command
    
    # Process Git commands (cross-platform)
    for item in data.get('git', []):
        query = item['query']
        intent = item['intent']
        command = item['command']
        
        queries.append(query)
        intents.append(intent)
        
        # Store intent to command mapping for both platforms
        # Git commands work on both Windows and Linux
        for platform in ['windows', 'linux']:
            key = f"{platform}_{intent}"
            if key not in intent_to_command:
                intent_to_command[key] = command
    
    print(f"✓ Loaded {len(queries)} training examples")
    print(f"✓ Found {len(set(intents))} unique intents")
    
    return queries, intents, intent_to_command

def train_model(queries, intents):
    """
    Train TF-IDF + Random Forest model
    
    Returns:
        model: Trained RandomForestClassifier
        vectorizer: Fitted TfidfVectorizer
        metrics: Training metrics
    """
    print("\n" + "="*60)
    print("TRAINING ML MODEL")
    print("="*60)
    
    # Filter out intents with only 1 example (can't stratify)
    from collections import Counter
    intent_counts = Counter(intents)
    single_instance_intents = {intent for intent, count in intent_counts.items() if count == 1}
    
    if single_instance_intents:
        print(f"\n⚠️  Found {len(single_instance_intents)} intents with only 1 example")
        print("   These will be included in training but not used for stratification")
    
    # Split data (without stratification if there are single-instance intents)
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            queries, intents, test_size=0.2, random_state=42, stratify=intents
        )
    except ValueError:
        # Fallback: split without stratification
        print("   Using non-stratified split...")
        X_train, X_test, y_train, y_test = train_test_split(
            queries, intents, test_size=0.2, random_state=42
        )
    
    print(f"\nTraining samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")
    
    # Create TF-IDF vectorizer
    print("\n1. Creating TF-IDF vectorizer...")
    vectorizer = TfidfVectorizer(
        max_features=500,
        ngram_range=(1, 2),  # Use unigrams and bigrams
        min_df=1,
        max_df=0.95,
        lowercase=True,
        stop_words='english'
    )
    
    # Fit and transform training data
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    
    print(f"   ✓ Vocabulary size: {len(vectorizer.vocabulary_)}")
    print(f"   ✓ Feature matrix shape: {X_train_tfidf.shape}")
    
    # Train Random Forest
    print("\n2. Training Random Forest classifier...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train_tfidf, y_train)
    print("   ✓ Model trained successfully")
    
    # Evaluate model
    print("\n3. Evaluating model...")
    y_pred = model.predict(X_test_tfidf)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n   Accuracy: {accuracy:.2%}")
    print(f"   Total test samples: {len(y_test)}")
    print(f"   Correct predictions: {sum(y_test == y_pred)}")
    print(f"   Incorrect predictions: {sum(y_test != y_pred)}")
    
    # Detailed classification report
    print("\n" + "="*60)
    print("CLASSIFICATION REPORT")
    print("="*60)
    report = classification_report(y_test, y_pred, zero_division=0)
    print(report)
    
    metrics = {
        'accuracy': accuracy,
        'n_train': len(X_train),
        'n_test': len(X_test),
        'n_features': X_train_tfidf.shape[1],
        'n_intents': len(set(intents))
    }
    
    return model, vectorizer, metrics

def save_model(model, vectorizer, intent_to_command, output_dir='.'):
    """Save trained model and components"""
    print("\n" + "="*60)
    print("SAVING MODEL")
    print("="*60)
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Save model
    model_path = os.path.join(output_dir, 'nl2cmd_model.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"✓ Model saved to: {model_path}")
    
    # Save vectorizer
    vectorizer_path = os.path.join(output_dir, 'tfidf_vectorizer.pkl')
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)
    print(f"✓ Vectorizer saved to: {vectorizer_path}")
    
    # Save intent mapping
    intent_map_path = os.path.join(output_dir, 'intent_to_command.pkl')
    with open(intent_map_path, 'wb') as f:
        pickle.dump(intent_to_command, f)
    print(f"✓ Intent mapping saved to: {intent_map_path}")
    
    print("\n✅ All model files saved successfully!")

def main():
    """Main training function"""
    print("="*60)
    print("NL2CMD MODEL TRAINER")
    print("="*60)
    
    # Load training data
    print("\nLoading training data...")
    data = load_training_data('training_data_enhanced.json')
    if not data:
        print("❌ Failed to load training data!")
        return
    
    # Prepare dataset
    queries, intents, intent_to_command = prepare_dataset(data)
    
    if len(queries) == 0:
        print("❌ No training data found!")
        return
    
    # Train model
    model, vectorizer, metrics = train_model(queries, intents)
    
    # Save model
    save_model(model, vectorizer, intent_to_command)
    
    print("\n" + "="*60)
    print("TRAINING SUMMARY")
    print("="*60)
    print(f"Training samples: {metrics['n_train']}")
    print(f"Test samples: {metrics['n_test']}")
    print(f"Unique intents: {metrics['n_intents']}")
    print(f"Features: {metrics['n_features']}")
    print(f"Accuracy: {metrics['accuracy']:.2%}")
    print("\n✅ Model training complete!")
    print("\nYou can now use ml_predictor.py to make predictions.")

if __name__ == "__main__":
    main()
