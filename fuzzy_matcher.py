import json
from typing import List, Dict, Tuple, Optional
from rapidfuzz import fuzz, process
import re

class FuzzyCommandMatcher:
    def __init__(self, training_data_path: str = 'training_data_enhanced.json'):
        self.training_data = self._load_training_data(training_data_path)
        self.query_index = self._build_query_index()
        
        # Problem-to-solution mappings
        self.problem_solutions = self._build_problem_solutions()
        
    def _load_training_data(self, path: str) -> Dict:
        """Load training data"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'windows': [], 'linux': []}
    
    def _build_query_index(self) -> Dict[str, Dict]:
        """Build searchable index of all queries"""
        index = {}
        
        for os_type in ['windows', 'linux']:
            for item in self.training_data.get(os_type, []):
                query = item['query'].lower()
                if query not in index:
                    index[query] = {
                        'command': item['command'],
                        'intent': item['intent'],
                        'os': os_type
                    }
        
        return index
    
    def _build_problem_solutions(self) -> Dict:
        """Build intelligent problem-to-solution mappings"""
        return {
            # Network problems
            'network': {
                'keywords': ['network', 'internet', 'connection', 'wifi', 'lan', 'ethernet', 'offline', 'not working', 'no connection'],
                'windows': [
                    {'problem': 'internet not working', 'solution': 'ipconfig /release && ipconfig /renew && ipconfig /flushdns', 'explanation': 'Reset network connection and flush DNS'},
                    {'problem': 'wifi not connecting', 'solution': 'netsh wlan show networks', 'explanation': 'Show available WiFi networks'},
                    {'problem': 'check network status', 'solution': 'netsh interface show interface', 'explanation': 'Display network adapter status'},
                    {'problem': 'network is slow', 'solution': 'netstat -ano', 'explanation': 'Check active connections'},
                ],
                'linux': [
                    {'problem': 'internet not working', 'solution': 'sudo systemctl restart NetworkManager', 'explanation': 'Restart network service'},
                    {'problem': 'check network', 'solution': 'ping -c 4 8.8.8.8 && ip addr show', 'explanation': 'Test connection and show IP'},
                    {'problem': 'wifi not connecting', 'solution': 'nmcli device wifi list', 'explanation': 'List WiFi networks'},
                ]
            },
            
            # System errors
            'system_error': {
                'keywords': ['error', 'corrupt', 'broken', 'damaged', 'crash', 'fail', 'not responding', 'missing', 'dll', 'system file'],
                'windows': [
                    {'problem': 'system files corrupted', 'solution': 'sfc /scannow', 'explanation': 'Scan and repair system files'},
                    {'problem': 'missing dll', 'solution': 'sfc /scannow && DISM /Online /Cleanup-Image /RestoreHealth', 'explanation': 'Repair system files and image'},
                    {'problem': 'windows update error', 'solution': 'net stop wuauserv && del /f/s/q %windir%\\SoftwareDistribution\\* && net start wuauserv', 'explanation': 'Reset Windows Update'},
                    {'problem': 'disk errors', 'solution': 'chkdsk C: /f /r', 'explanation': 'Check and repair disk errors'},
                    {'problem': 'hard drive error', 'solution': 'chkdsk C: /f /r', 'explanation': 'Check and repair disk errors'},
                ],
                'linux': [
                    {'problem': 'system error', 'solution': 'journalctl -xe | tail -50', 'explanation': 'View recent system errors'},
                    {'problem': 'package broken', 'solution': 'sudo apt --fix-broken install', 'explanation': 'Fix broken packages'},
                    {'problem': 'disk errors', 'solution': 'sudo fsck -y /dev/sda1', 'explanation': 'Check filesystem'},
                ]
            },
            
            # Performance issues
            'performance': {
                'keywords': ['slow', 'freeze', 'lag', 'hang', 'stuck', 'cpu', 'memory', 'ram'],
                'windows': [
                    {'problem': 'computer slow', 'solution': 'tasklist /V && wmic cpu get loadpercentage', 'explanation': 'Check process and CPU usage'},
                    {'problem': 'high cpu usage', 'solution': 'powershell "Get-Process | Sort-Object CPU -Descending | Select-Object -First 10"', 'explanation': 'Show top CPU processes'},
                    {'problem': 'memory full', 'solution': 'systeminfo | findstr /C:"Available Physical Memory"', 'explanation': 'Check available RAM'},
                    {'problem': 'disk full', 'solution': 'wmic logicaldisk get size,freespace,caption', 'explanation': 'Check disk space'},
                ],
                'linux': [
                    {'problem': 'system slow', 'solution': 'top -bn1 | head -20', 'explanation': 'Show system resource usage'},
                    {'problem': 'high cpu', 'solution': 'ps aux --sort=-%cpu | head -10', 'explanation': 'Top CPU processes'},
                    {'problem': 'memory full', 'solution': 'free -h && ps aux --sort=-%mem | head -10', 'explanation': 'Check memory and top processes'},
                    {'problem': 'disk full', 'solution': 'df -h && du -sh /* | sort -rh | head -10', 'explanation': 'Check disk usage'},
                ]
            },
            
            # Application problems
            'application': {
                'keywords': ['app', 'program', 'application', 'not opening', 'wont start', 'frozen'],
                'windows': [
                    {'problem': 'app not responding', 'solution': 'taskkill /IM <process>.exe /F', 'explanation': 'Force close application'},
                    {'problem': 'program wont start', 'solution': 'tasklist /FI "IMAGENAME eq <process>.exe"', 'explanation': 'Check if program is running'},
                ],
                'linux': [
                    {'problem': 'app frozen', 'solution': 'pkill -9 <process>', 'explanation': 'Force kill process'},
                    {'problem': 'check if running', 'solution': 'ps aux | grep <process>', 'explanation': 'Find running process'},
                ]
            },
            
            # Security issues
            'security': {
                'keywords': ['virus', 'malware', 'hack', 'security', 'suspicious', 'unauthorized'],
                'windows': [
                    {'problem': 'suspicious activity', 'solution': 'netstat -ano && tasklist /V', 'explanation': 'Check active connections and processes'},
                    {'problem': 'check open ports', 'solution': 'netstat -ano | findstr LISTENING', 'explanation': 'Show listening ports'},
                ],
                'linux': [
                    {'problem': 'suspicious activity', 'solution': 'netstat -tulpn && ps aux --sort=-%cpu', 'explanation': 'Check connections and processes'},
                    {'problem': 'unauthorized access', 'solution': 'last -a && who', 'explanation': 'Check login history'},
                ]
            },
            
            # Boot/startup issues
            'boot': {
                'keywords': ['boot', 'startup', 'wont start', 'black screen', 'grub'],
                'windows': [
                    {'problem': 'boot error', 'solution': 'bootrec /fixmbr && bootrec /fixboot && bootrec /rebuildbcd', 'explanation': 'Repair boot configuration'},
                ],
                'linux': [
                    {'problem': 'grub error', 'solution': 'sudo update-grub && sudo grub-install /dev/sda', 'explanation': 'Repair GRUB bootloader'},
                ]
            }
        }
    
    def fuzzy_search(self, query: str, threshold: int = 70, limit: int = 5) -> List[Tuple[str, int, Dict]]:
        """
        Perform fuzzy search with typo tolerance
        
        Args:
            query: User query (can have spelling mistakes)
            threshold: Minimum similarity score (0-100)
            limit: Max results to return
            
        Returns:
            List of (matched_query, score, command_info) tuples
        """
        query = query.lower().strip()
        
        # Get all possible queries
        all_queries = list(self.query_index.keys())
        
        # Use rapidfuzz for fast fuzzy matching
        matches = process.extract(
            query, 
            all_queries, 
            scorer=fuzz.WRatio,  # Weighted ratio for better results
            limit=limit,
            score_cutoff=threshold
        )
        
        results = []
        for match, score, _ in matches:
            command_info = self.query_index[match]
            results.append((match, score, command_info))
        
        return results
    
    def diagnose_problem(self, query: str, os_type: str = 'windows') -> List[Dict]:
        """
        Intelligent problem diagnosis - map error descriptions to solutions
        
        Args:
            query: Problem description
            os_type: Operating system
            
        Returns:
            List of solution dictionaries
        """
        query_lower = query.lower()
        solutions = []
        
        # Check each problem category
        for category, data in self.problem_solutions.items():
            # Check if query matches category keywords
            keyword_matches = sum(1 for kw in data['keywords'] if kw in query_lower)
            
            if keyword_matches > 0:
                # Add relevant solutions for this OS
                os_solutions = data.get(os_type, [])
                for sol in os_solutions:
                    # Calculate relevance score
                    problem_words = sol['problem'].lower().split()
                    query_words = query_lower.split()
                    overlap = len(set(problem_words) & set(query_words))
                    
                    if overlap > 0:
                        solutions.append({
                            'command': sol['solution'],
                            'explanation': sol['explanation'],
                            'category': category,
                            'relevance': overlap + keyword_matches,
                            'problem': sol['problem']
                        })
        
        # Sort by relevance
        solutions.sort(key=lambda x: x['relevance'], reverse=True)
        
        return solutions[:3]  # Top 3 solutions
    
    def smart_search(self, query: str, os_type: str = 'windows') -> Dict:
        """
        Combined intelligent search:
        1. Try exact/fuzzy match
        2. Try problem diagnosis
        3. Return best results
        """
        results = {
            'fuzzy_matches': [],
            'problem_solutions': [],
            'best_match': None,
            'confidence': 0
        }
        
        # 1. Fuzzy search
        fuzzy_results = self.fuzzy_search(query, threshold=60, limit=5)
        results['fuzzy_matches'] = fuzzy_results
        
        # 2. Problem diagnosis
        problem_solutions = self.diagnose_problem(query, os_type)
        results['problem_solutions'] = problem_solutions
        
        # 3. Determine best match (IMPROVED LOGIC)
        # Prioritize problem diagnosis when it finds good solutions
        if problem_solutions and problem_solutions[0]['relevance'] >= 2:
            # Problem diagnosis found relevant solutions
            problem_confidence = min(90, 75 + problem_solutions[0]['relevance'] * 5)
            
            # Use problem diagnosis if it's more relevant than fuzzy
            if not fuzzy_results or problem_confidence >= fuzzy_results[0][1]:
                results['best_match'] = {
                    'command': problem_solutions[0]['command'],
                    'explanation': problem_solutions[0]['explanation'],
                    'source': 'problem_diagnosis',
                    'category': problem_solutions[0]['category'],
                    'problem': problem_solutions[0]['problem']
                }
                results['confidence'] = problem_confidence
                return results
        
        # Otherwise use fuzzy match if high confidence
        if fuzzy_results and fuzzy_results[0][1] >= 85:
            # High confidence fuzzy match
            matched_query, score, cmd_info = fuzzy_results[0]
            results['best_match'] = {
                'command': cmd_info['command'],
                'intent': cmd_info['intent'],
                'source': 'fuzzy_match',
                'matched_query': matched_query,
                'os': cmd_info['os']
            }
            results['confidence'] = score
        elif problem_solutions:
            # Use problem diagnosis as fallback
            results['best_match'] = {
                'command': problem_solutions[0]['command'],
                'explanation': problem_solutions[0]['explanation'],
                'source': 'problem_diagnosis',
                'category': problem_solutions[0]['category']
            }
            results['confidence'] = 75 + problem_solutions[0]['relevance'] * 5
        elif fuzzy_results:
            # Lower confidence fuzzy match
            matched_query, score, cmd_info = fuzzy_results[0]
            results['best_match'] = {
                'command': cmd_info['command'],
                'intent': cmd_info['intent'],
                'source': 'fuzzy_match',
                'matched_query': matched_query,
                'os': cmd_info['os']
            }
            results['confidence'] = score
        
        return results


def test_fuzzy_search():
    """Test fuzzy search with typos"""
    matcher = FuzzyCommandMatcher()
    
    print("="*70)
    print("FUZZY SEARCH TEST - Handling Spelling Mistakes")
    print("="*70)
    
    test_queries = [
        "lst all fils",  # typos: list all files
        "shw systm infrmation",  # typos: show system information  
        "kil chrom",  # typos: kill chrome
        "chck disk spce",  # typos: check disk space
        "intrnet not wrking",  # problem: internet not working
        "sistem files corupted",  # problem: system files corrupted
        "computr is slo",  # problem: computer is slow
        "high cpu usge",  # problem: high cpu usage
    ]
    
    for query in test_queries:
        print(f"\n{'='*70}")
        print(f"Query (with typos): '{query}'")
        print('-'*70)
        
        results = matcher.smart_search(query)
        
        if results['best_match']:
            best = results['best_match']
            print(f"✓ BEST MATCH ({results['confidence']:.0f}% confidence)")
            print(f"  Command: {best['command']}")
            print(f"  Source: {best['source']}")
            if 'explanation' in best:
                print(f"  Explanation: {best['explanation']}")
            if 'matched_query' in best:
                print(f"  Matched: '{best['matched_query']}'")
        
        if results['problem_solutions']:
            print(f"\n💡 Problem Solutions Found:")
            for i, sol in enumerate(results['problem_solutions'][:3], 1):
                print(f"  {i}. {sol['explanation']}")
                print(f"     Command: {sol['command']}")


if __name__ == "__main__":
    test_fuzzy_search()
