import platform
from typing import Dict, Optional
from input_processor import InputProcessor
from ml_predictor import MLPredictor

try:
    from fuzzy_matcher import FuzzyCommandMatcher
    FUZZY_AVAILABLE = True
except ImportError:
    FUZZY_AVAILABLE = False
    print("⚠️  Fuzzy matching not available (install rapidfuzz)")

try:
    from parameter_extractor import ParameterExtractor, CommandTemplateEngine
    DYNAMIC_PARAMS_AVAILABLE = True
except ImportError:
    DYNAMIC_PARAMS_AVAILABLE = False
    print("⚠️  Dynamic parameter extraction not available")

class IntelligenceEngine:
    def __init__(self, model_dir: str = ".", confidence_threshold: float = 0.6):
        self.input_processor = InputProcessor()
        self.ml_predictor = MLPredictor(model_dir)
        self.confidence_threshold = confidence_threshold
        self.os_type = platform.system()
        
        if FUZZY_AVAILABLE:
            try:
                self.fuzzy_matcher = FuzzyCommandMatcher()
                self.fuzzy_available = True
                print("✓ Fuzzy search enabled (typo tolerance active)")
            except Exception as e:
                self.fuzzy_matcher = None
                self.fuzzy_available = False
                print(f"⚠️  Fuzzy search disabled: {e}")
        else:
            self.fuzzy_matcher = None
            self.fuzzy_available = False
        
        if DYNAMIC_PARAMS_AVAILABLE:
            try:
                self.param_extractor = ParameterExtractor()
                self.template_engine = CommandTemplateEngine()
                self.dynamic_params_available = True
                print("✓ Dynamic parameter extraction enabled")
            except Exception as e:
                self.param_extractor = None
                self.template_engine = None
                self.dynamic_params_available = False
                print(f"⚠️  Dynamic parameters disabled: {e}")
        else:
            self.param_extractor = None
            self.template_engine = None
            self.dynamic_params_available = False
        
        self.ml_available = self.ml_predictor.load_model()
        if not self.ml_available:
            print("⚠️  ML model not available, will use rule-based matching only")
        
        if "Windows" in self.os_type:
            from windows_cmd import handle_nl_cmd as rule_matcher
        elif "Linux" in self.os_type:
            from linux_cmd import handle_nl_cmd as rule_matcher
        else:
            from windows_cmd import handle_nl_cmd as rule_matcher
        
        self.rule_matcher = rule_matcher
    
    def process_query(self, query: str, force_method: Optional[str] = None) -> Dict:
        processed = self.input_processor.process(query)
        
        if not processed['is_valid']:
            return {
                'success': False,
                'command': None,
                'method': 'none',
                'confidence': 0.0,
                'error': 'Invalid or empty query'
            }
        
        if self.ml_available and force_method != 'rule' and force_method != 'fuzzy':
            ml_result = self._try_ml_prediction(query, processed)
            
            if ml_result['success'] and ml_result['confidence'] >= self.confidence_threshold:
                return ml_result
            
            ml_backup = ml_result
        else:
            ml_backup = None
        
        if self.dynamic_params_available:
            template_result = self._try_template_generation(query, processed)
            
            if template_result and template_result.get('success') and template_result.get('confidence', 0) >= 0.90:
                return template_result
            
            template_backup = template_result if template_result else None
        else:
            template_backup = None
        
        if self.fuzzy_available and force_method != 'rule' and force_method != 'ml':
            fuzzy_result = self._try_fuzzy_search(query, processed)
            
            if fuzzy_result['success'] and fuzzy_result['confidence'] >= 75:
                return fuzzy_result
            
            fuzzy_backup = fuzzy_result
        else:
            fuzzy_backup = None
        
        if force_method != 'ml' and force_method != 'fuzzy':
            rule_result = self._try_rule_matching(query, processed)
            
            if rule_result['success']:
                return rule_result
        
        backups = [
            ml_backup,
            fuzzy_backup
        ]
        
        valid_backups = [b for b in backups if b and b.get('command')]
        if valid_backups:
            best_backup = max(valid_backups, key=lambda x: x.get('confidence', 0))
            best_backup['fallback'] = True
            best_backup['warning'] = f"Low confidence ({best_backup['confidence']:.1%}), please verify"
            return best_backup
        
        return {
            'success': False,
            'command': None,
            'method': 'none',
            'confidence': 0.0,
            'query': query,
            'processed': processed,
            'error': 'No matching command found. Try rephrasing or use --help for examples.'
        }
    
    def _try_ml_prediction(self, query: str, processed: Dict) -> Dict:
        try:
            result = self.ml_predictor.predict(query)
            
            if result.get('success'):
                result['method'] = 'ml'
                result['processed_input'] = processed
                result['query'] = query
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'command': None,
                'method': 'ml',
                'confidence': 0.0,
                'error': f"ML prediction failed: {str(e)}"
            }
    
    def _try_template_generation(self, query: str, processed: Dict) -> Optional[Dict]:
        if not self.dynamic_params_available:
            return None
        
        try:
            analysis = self.param_extractor.extract_command_intent_and_params(query)
            
            result = self.template_engine.generate_from_analysis(analysis)
            
            if result:
                result['processed_input'] = processed
                result['query'] = query
                result['analysis'] = analysis
                return result
            
            return None
            
        except Exception as e:
            return {
                'success': False,
                'command': None,
                'method': 'template',
                'confidence': 0.0,
                'error': f"Template generation failed: {str(e)}"
            }
    
    def _try_fuzzy_search(self, query: str, processed: Dict) -> Dict:
        if not self.fuzzy_available:
            return {
                'success': False,
                'command': None,
                'method': 'fuzzy',
                'confidence': 0.0,
                'error': 'Fuzzy search not available'
            }
        
        try:
            os_type = 'windows' if 'Windows' in self.os_type else 'linux'
            result = self.fuzzy_matcher.smart_search(query, os_type)
            
            if result['best_match']:
                best = result['best_match']
                
                return {
                    'success': True,
                    'command': best['command'],
                    'method': 'fuzzy' if best['source'] == 'fuzzy_match' else 'problem_diagnosis',
                    'confidence': result['confidence'] / 100.0,
                    'query': query,
                    'matched_query': best.get('matched_query'),
                    'explanation': best.get('explanation'),
                    'intent': best.get('intent', 'unknown'),
                    'processed_input': processed,
                    'fuzzy_matches': result.get('fuzzy_matches', []),
                    'problem_solutions': result.get('problem_solutions', [])
                }
            else:
                return {
                    'success': False,
                    'command': None,
                    'method': 'fuzzy',
                    'confidence': 0.0,
                    'error': 'No fuzzy matches found'
                }
                
        except Exception as e:
            return {
                'success': False,
                'command': None,
                'method': 'fuzzy',
                'confidence': 0.0,
                'error': f"Fuzzy search failed: {str(e)}"
            }
    
    def _try_rule_matching(self, query: str, processed: Dict) -> Dict:
        try:
            command = self.rule_matcher(query)
            
            is_fallback = command.startswith('echo')
            
            if not is_fallback:
                return {
                    'success': True,
                    'command': command,
                    'method': 'rule',
                    'confidence': 1.0,
                    'query': query,
                    'processed_input': processed
                }
            else:
                return {
                    'success': False,
                    'command': command,
                    'method': 'rule',
                    'confidence': 0.0,
                    'query': query,
                    'is_fallback': True
                }
                
        except Exception as e:
            return {
                'success': False,
                'command': None,
                'method': 'rule',
                'confidence': 0.0,
                'error': f"Rule matching failed: {str(e)}"
            }
    
    def get_suggestions(self, query: str, n: int = 3) -> list:
        suggestions = []
        
        if self.ml_available:
            ml_suggestions = self.ml_predictor.get_top_predictions(query, n)
            suggestions.extend(ml_suggestions)
        
        processed = self.input_processor.process(query)
        rule_result = self._try_rule_matching(query, processed)
        if rule_result['success']:
            suggestions.insert(0, {
                'command': rule_result['command'],
                'confidence': 1.0,
                'method': 'rule',
                'intent': 'rule_based'
            })
        
        return suggestions[:n]

def process_natural_language(query: str, model_dir: str = ".") -> Dict:
    engine = IntelligenceEngine(model_dir)
    return engine.process_query(query)

if __name__ == "__main__":
    print("=" * 60)
    print("INTELLIGENCE ENGINE TEST")
    print("=" * 60)
    
    engine = IntelligenceEngine()
    
    test_queries = [
        "list all files",
        "show system information",
        "kill chrome",
        "get my IP address",
        "clean temporary files",
        "some random text that won't match"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: '{query}'")
        print('-'*60)
        
        result = engine.process_query(query)
        
        print(f"Success: {result.get('success')}")
        print(f"Command: {result.get('command')}")
        print(f"Method: {result.get('method')}")
        print(f"Confidence: {result.get('confidence', 0):.2%}")
        
        if 'error' in result:
            print(f"Error: {result['error']}")
        
        if 'warning' in result:
            print(f"⚠️  {result['warning']}")
