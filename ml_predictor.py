import os
import pickle
import platform
from typing import Dict, Tuple, Optional

class MLPredictor:
    def __init__(self, model_dir: str = "."):
        self.model_dir = model_dir
        self.model = None
        self.vectorizer = None
        self.intent_to_command = None
        self.os_type = platform.system().lower()
        self.is_loaded = False
        self.confidence_threshold = 0.6
        
    def load_model(self) -> bool:
        try:
            model_path = os.path.join(self.model_dir, 'nl2cmd_model.pkl')
            vectorizer_path = os.path.join(self.model_dir, 'tfidf_vectorizer.pkl')
            intent_map_path = os.path.join(self.model_dir, 'intent_to_command.pkl')
            
            if not all(os.path.exists(p) for p in [model_path, vectorizer_path, intent_map_path]):
                print("⚠️  ML model files not found. Run train_model.py first.")
                return False
            
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            with open(vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            
            with open(intent_map_path, 'rb') as f:
                self.intent_to_command = pickle.load(f)
            
            self.is_loaded = True
            print("✓ ML model loaded successfully")
            return True
            
        except Exception as e:
            print(f"Error loading ML model: {e}")
            return False
    
    def predict(self, query: str, os_type: Optional[str] = None) -> Dict:
        if not self.is_loaded:
            return {
                'success': False,
                'command': None,
                'confidence': 0.0,
                'intent': None,
                'method': 'ml',
                'error': 'Model not loaded'
            }
        
        try:
            target_os = os_type or self.os_type
            if 'windows' in target_os.lower():
                target_os = 'windows'
            elif 'linux' in target_os.lower():
                target_os = 'linux'
            else:
                target_os = 'windows'
            
            query_vector = self.vectorizer.transform([query.lower()])
            
            prediction = self.model.predict(query_vector)[0]
            probabilities = self.model.predict_proba(query_vector)[0]
            
            confidence = float(max(probabilities))
            
            intent = prediction
            
            command = self._get_command_for_intent(intent, target_os)
            
            is_confident = confidence >= self.confidence_threshold
            
            return {
                'success': is_confident,
                'command': command if is_confident else None,
                'confidence': confidence,
                'intent': intent,
                'method': 'ml',
                'os_type': target_os,
                'all_probabilities': dict(zip(self.model.classes_, probabilities))
            }
            
        except Exception as e:
            return {
                'success': False,
                'command': None,
                'confidence': 0.0,
                'intent': None,
                'method': 'ml',
                'error': str(e)
            }
    
    def _get_command_for_intent(self, intent: str, os_type: str) -> Optional[str]:
        if not self.intent_to_command:
            return None
        
        key = f"{os_type}_{intent}"
        if key in self.intent_to_command:
            return self.intent_to_command[key]
        
        if intent in self.intent_to_command:
            return self.intent_to_command[intent]
        
        return None
    
    def get_top_predictions(self, query: str, n: int = 3, os_type: Optional[str] = None) -> list:
        if not self.is_loaded:
            return []
        
        try:
            target_os = os_type or self.os_type
            if 'windows' in target_os.lower():
                target_os = 'windows'
            elif 'linux' in target_os.lower():
                target_os = 'linux'
            
            query_vector = self.vectorizer.transform([query.lower()])
            
            probabilities = self.model.predict_proba(query_vector)[0]
            
            top_indices = probabilities.argsort()[-n:][::-1]
            
            results = []
            for idx in top_indices:
                intent = self.model.classes_[idx]
                confidence = float(probabilities[idx])
                command = self._get_command_for_intent(intent, target_os)
                
                results.append({
                    'intent': intent,
                    'command': command,
                    'confidence': confidence,
                    'method': 'ml'
                })
            
            return results
            
        except Exception as e:
            print(f"Error getting top predictions: {e}")
            return []

def predict_command(query: str, model_dir: str = ".") -> Dict:
    predictor = MLPredictor(model_dir)
    if predictor.load_model():
        return predictor.predict(query)
    else:
        return {
            'success': False,
            'command': None,
            'confidence': 0.0,
            'intent': None,
            'method': 'ml',
            'error': 'Failed to load model'
        }

if __name__ == "__main__":
    print("=" * 60)
    print("ML PREDICTOR TEST")
    print("=" * 60)
    
    predictor = MLPredictor()
    if predictor.load_model():
        test_queries = [
            "list all files",
            "show system information",
            "kill chrome",
            "get my IP address",
            "clean temporary files"
        ]
        
        for query in test_queries:
            result = predictor.predict(query)
            print(f"\nQuery: '{query}'")
            print(f"Command: {result.get('command')}")
            print(f"Confidence: {result.get('confidence', 0):.2%}")
            print(f"Intent: {result.get('intent')}")
            print("-" * 60)
    else:
        print("\n⚠️  Model not found. Please run train_model.py first to create the ML model.")
