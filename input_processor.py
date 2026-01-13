import re
from typing import Dict, List, Tuple

class InputProcessor:
    
    STOP_WORDS = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
        'to', 'was', 'will', 'with', 'i', 'you', 'we', 'they', 'can',
        'could', 'would', 'should', 'do', 'does', 'did', 'have', 'had'
    }
    
    ACTION_KEYWORDS = {
        'list', 'show', 'get', 'find', 'search', 'display', 'view',
        'kill', 'stop', 'terminate', 'end', 'close',
        'start', 'run', 'execute', 'launch', 'open',
        'delete', 'remove', 'erase', 'clear', 'clean',
        'copy', 'move', 'rename', 'change',
        'create', 'make', 'add', 'new',
        'install', 'update', 'upgrade', 'download',
        'check', 'verify', 'test', 'ping',
        'shutdown', 'reboot', 'restart', 'logout'
    }
    
    TARGET_KEYWORDS = {
        'file', 'files', 'directory', 'folder', 'path',
        'process', 'processes', 'task', 'service', 'services',
        'user', 'users', 'group', 'groups',
        'network', 'ip', 'port', 'ports', 'connection',
        'disk', 'memory', 'cpu', 'system', 'info', 'information',
        'package', 'program', 'application', 'app',
        'firewall', 'security', 'permission', 'permissions',
        'temp', 'temporary', 'cache', 'log', 'logs',
        'hidden', 'all', 'recursive'
    }
    
    @staticmethod
    def normalize_text(text: str) -> str:
        text = text.lower().strip()
        
        text = re.sub(r'[^\w\s-]', ' ', text)
        
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @staticmethod
    def extract_keywords(text: str) -> List[str]:
        normalized = InputProcessor.normalize_text(text)
        words = normalized.split()
        
        keywords = [w for w in words if w not in InputProcessor.STOP_WORDS]
        
        return keywords
    
    @staticmethod
    def categorize_keywords(keywords: List[str]) -> Dict[str, List[str]]:
        actions = [kw for kw in keywords if kw in InputProcessor.ACTION_KEYWORDS]
        targets = [kw for kw in keywords if kw in InputProcessor.TARGET_KEYWORDS]
        modifiers = [kw for kw in keywords if kw not in actions and kw not in targets]
        
        return {
            'actions': actions,
            'targets': targets,
            'modifiers': modifiers,
            'all_keywords': keywords
        }
    
    @staticmethod
    def extract_parameters(text: str) -> Dict[str, str]:
        params = {}
        
        filename_pattern = r'\b[\w-]+\.\w+\b'
        filenames = re.findall(filename_pattern, text)
        if filenames:
            params['filename'] = filenames[0]
        
        url_pattern = r'https?://[\w\.-]+(?:/[\w\.-]*)*'
        urls = re.findall(url_pattern, text)
        if urls:
            params['url'] = urls[0]
        
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ips = re.findall(ip_pattern, text)
        if ips:
            params['ip'] = ips[0]
        
        number_pattern = r'\b\d+\b'
        numbers = re.findall(number_pattern, text)
        if numbers:
            params['number'] = numbers[0]
        
        return params
    
    @staticmethod
    def process(text: str) -> Dict:
        if not text or not text.strip():
            return {
                'original': text,
                'normalized': '',
                'keywords': [],
                'categorized': {
                    'actions': [],
                    'targets': [],
                    'modifiers': [],
                    'all_keywords': []
                },
                'parameters': {},
                'is_valid': False
            }
        
        normalized = InputProcessor.normalize_text(text)
        keywords = InputProcessor.extract_keywords(text)
        categorized = InputProcessor.categorize_keywords(keywords)
        parameters = InputProcessor.extract_parameters(text)
        
        result = {
            'original': text,
            'normalized': normalized,
            'keywords': keywords,
            'categorized': categorized,
            'parameters': parameters,
            'is_valid': len(keywords) > 0
        }
        
        return result

def process_input(text: str) -> Dict:
    return InputProcessor.process(text)

if __name__ == "__main__":
    test_inputs = [
        "list all files",
        "show hidden files in directory",
        "kill chrome process",
        "get my IP address",
        "find file named test.txt",
        "shutdown the computer",
        "delete temporary files"
    ]
    
    print("=" * 60)
    print("INPUT PROCESSOR TEST")
    print("=" * 60)
    
    for test in test_inputs:
        result = process_input(test)
        print(f"\nInput: '{test}'")
        print(f"Normalized: '{result['normalized']}'")
        print(f"Keywords: {result['keywords']}")
        print(f"Actions: {result['categorized']['actions']}")
        print(f"Targets: {result['categorized']['targets']}")
        print(f"Parameters: {result['parameters']}")
        print("-" * 60)
