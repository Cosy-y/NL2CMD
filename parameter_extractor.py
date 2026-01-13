import re
from typing import Dict, List, Optional, Tuple
import platform

class ParameterExtractor:
    def __init__(self):
        self.os_type = platform.system()
        
        # Common parameter patterns
        self.patterns = {
            # File names (improved patterns) - now supports paths with \ and /
            'filename': [
                r'file\s+["\']([^"\']+)["\']',        # file "name.txt" or "path\name.txt"
                r'file\s+named?\s+["\']([^"\']+)["\']',
                r'file\s+called\s+["\']([^"\']+)["\']',
                r'file\s+named?\s+([\w\-_\.\\\/]+)',   # file named test.txt or path\test.txt
                r'file\s+called\s+([\w\-_\.\\\/]+)',
                r'([\w\-_]+\.\w+)\s+file',             # test.txt file
            ],
            
            # Folder/directory names (improved) - now supports paths
            'foldername': [
                r'folder\s+["\']([^"\']+)["\']',
                r'directory\s+["\']([^"\']+)["\']',
                r'folder\s+named?\s+["\']([^"\']+)["\']',
                r'folder\s+called\s+["\']([^"\']+)["\']',
                r'(?:folder|directory)\s+named?\s+([\w\-_]+)',
                r'(?:folder|directory)\s+called\s+([\w\-_]+)',
            ],
            
            # Process names (improved)
            'process': [
                r'process\s+["\']([^"\']+)["\']',
                r'program\s+["\']([^"\']+)["\']',
                r'application\s+["\']([^"\']+)["\']',
                r'(?:kill|stop|close|terminate)\s+(?:process\s+)?["\']?(\w+)["\']?(?:\s+process)?',
            ],
            
            # Paths
            'path': [
                r'(?:in|to|at)\s+["\']([A-Za-z]:[\\\/].+?)["\']',  # Windows path
                r'(?:in|to|at)\s+["\']([/~].+?)["\']',             # Linux path
                r'(?:in|to|at)\s+([A-Za-z]:[\\\/]\S+)',            # Unquoted Windows
                r'(?:in|to|at)\s+([/~]\S+)',                        # Unquoted Linux
            ],
            
            # Port numbers
            'port': [
                r'port\s+(\d+)',
                r'on\s+port\s+(\d+)',
                r':(\d+)',
            ],
            
            # IP addresses
            'ip': [
                r'(\d+\.\d+\.\d+\.\d+)',
            ],
            
            # Extensions
            'extension': [
                r'\.(\w+)\s+files?',
                r'files?\s+with\s+\.(\w+)',
                r'(\w+)\s+files?',
            ],
            
            # Numbers/counts
            'number': [
                r'(\d+)\s+(?:files?|items?|processes?)',
                r'top\s+(\d+)',
                r'last\s+(\d+)',
                r'first\s+(\d+)',
            ],
            
            # Text content
            'content': [
                r'with\s+content\s+["\'](.+?)["\']',
                r'containing\s+["\'](.+?)["\']',
                r'text\s+["\'](.+?)["\']',
            ],
        }
    
    def extract_all(self, query: str) -> Dict[str, any]:
        """
        Extract all parameters from query
        
        Args:
            query: Natural language query
            
        Returns:
            Dictionary of extracted parameters
        """
        params = {
            'query': query,
            'extracted': {}
        }
        
        # Try each parameter type
        for param_type, patterns in self.patterns.items():
            value = self._extract_parameter(query, patterns)
            if value:
                params['extracted'][param_type] = value
        
        # Special: detect multiple entities
        params['has_multiple'] = self._detect_multiple_entities(query)
        
        return params
    
    def _extract_parameter(self, query: str, patterns: List[str]) -> Optional[str]:
        """Extract parameter using regex patterns"""
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def _detect_multiple_entities(self, query: str) -> Dict[str, bool]:
        """Detect if query mentions multiple entities"""
        return {
            'file_and_folder': bool(re.search(r'(file|folder).*(?:and|with).*(?:file|folder)', query, re.IGNORECASE)),
            'multiple_files': bool(re.search(r'files', query, re.IGNORECASE)),
            'multiple_folders': bool(re.search(r'folders|directories', query, re.IGNORECASE)),
        }
    
    def extract_nested_operation(self, query: str) -> Optional[Dict]:
        """
        Extract nested operations (e.g., "create folder X with file Y inside")
        
        Returns:
            Dictionary with parent and child operations
        """
        query_lower = query.lower()
        
        # Pattern: folder with file inside (improved)
        match = re.search(
            r'(?:folder|directory)\s+(?:named?\s+|called\s+)?["\']?([\w\-_\.]+)["\']?\s+(?:with|containing|and)\s+(?:a\s+)?file\s+(?:named?\s+|called\s+)?["\']?([\w\-_\.]+)["\']?',
            query, re.IGNORECASE
        )
        if match:
            return {
                'type': 'nested',
                'parent': {
                    'type': 'folder',
                    'name': match.group(1)
                },
                'child': {
                    'type': 'file',
                    'name': match.group(2)
                }
            }
        
        # Pattern: file in folder (improved)
        match = re.search(
            r'file\s+(?:named?\s+|called\s+)?["\']?([\w\-_\.]+)["\']?\s+(?:in|inside)\s+(?:folder|directory)\s+(?:named?\s+|called\s+)?["\']?([\w\-_\.]+)["\']?',
            query, re.IGNORECASE
        )
        if match:
            return {
                'type': 'nested',
                'parent': {
                    'type': 'folder',
                    'name': match.group(2)
                },
                'child': {
                    'type': 'file',
                    'name': match.group(1)
                }
            }
        
        return None
    
    def extract_command_intent_and_params(self, query: str) -> Dict:
        """
        Extract command intent and parameters together
        
        Returns:
            Dictionary with intent, action, targets, and parameters
        """
        result = {
            'intent': None,
            'action': None,
            'targets': [],
            'parameters': self.extract_all(query),
            'nested': self.extract_nested_operation(query)
        }
        
        query_lower = query.lower()
        
        # Check for Git commands first (specific patterns)
        git_patterns = {
            'git_status': [r'\b(git\s+status|check\s+git\s+status|show\s+git\s+status|see\s+git\s+changes)\b'],
            'git_init': [r'\b(git\s+init|initialize\s+git|create\s+git\s+repo|start\s+git)\b'],
            'git_add_all': [r'\b(git\s+add\s+all|stage\s+all|add\s+everything\s+to\s+git|git\s+add\s+\.|add\s+all\s+files\s+to\s+git)\b'],
            'git_commit': [r'\b(commit\s+(the\s+)?changes|git\s+commit|make\s+a\s+commit|save\s+changes\s+to\s+git|commit\s+all)\b'],
            'git_push': [r'\b(git\s+push|push\s+to\s+github|push\s+changes|upload\s+to\s+github|push\s+to\s+remote)\b'],
            'git_pull': [r'\b(git\s+pull|pull\s+from\s+github|pull\s+changes|get\s+latest|sync\s+with\s+github)\b'],
            'git_clone': [r'\b(git\s+clone|clone\s+repo|download\s+repo|copy\s+repository)\b'],
            'git_create_branch': [r'\b(create\s+(a\s+)?(new\s+)?branch|make\s+(a\s+)?(new\s+)?branch|add\s+(a\s+)?branch|new\s+branch)\b'],
            'git_checkout': [r'\b(switch\s+branch|change\s+branch|checkout\s+branch|go\s+to\s+branch)\b'],
            'git_list_branches': [r'\b(list\s+branches|show\s+(all\s+)?branches|see\s+branches|git\s+branch$)\b'],
            'git_merge': [r'\b(merge\s+branch|git\s+merge|combine\s+branches)\b'],
            'git_log': [r'\b(git\s+log|show\s+commit\s+history|view\s+commit\s+log|see\s+git\s+history)\b'],
            'git_diff': [r'\b(git\s+diff|show\s+file\s+changes|see\s+differences|what\s+changed)\b'],
            'git_stash': [r'\b(git\s+stash|stash\s+changes|save\s+work\s+in\s+progress)\b'],
            'git_fetch': [r'\b(git\s+fetch|fetch\s+from\s+remote|get\s+remote\s+changes)\b'],
            'git_list_remotes': [r'\b(list\s+remotes|show\s+remote\s+repositories|git\s+remote\s+-v)\b'],
        }
        
        for git_intent, patterns in git_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    result['intent'] = git_intent
                    result['action'] = 'git'
                    result['targets'] = ['git']
                    return result
        
        # Detect action verbs
        actions = {
            'create': ['create', 'make', 'new', 'add', 'generate'],
            'delete': ['delete', 'remove', 'del', 'rm', 'erase'],
            'rename': ['rename', 'move', 'mv'],
            'copy': ['copy', 'cp', 'duplicate'],
            'list': ['list', 'show', 'display', 'ls', 'dir'],
            'find': ['find', 'search', 'locate'],
            'kill': ['kill', 'stop', 'terminate', 'close'],
            'start': ['start', 'run', 'launch', 'open'],
            'modify': ['edit', 'modify', 'change', 'update'],
        }
        
        for intent, verbs in actions.items():
            for verb in verbs:
                if re.search(rf'\b{verb}\b', query_lower):
                    result['intent'] = intent
                    result['action'] = verb
                    break
            if result['intent']:
                break
        
        # Detect targets
        targets = {
            'file': ['file', 'document', 'doc'],
            'folder': ['folder', 'directory', 'dir'],
            'process': ['process', 'program', 'application', 'app'],
            'service': ['service', 'daemon'],
            'user': ['user', 'account'],
        }
        
        for target_type, keywords in targets.items():
            for keyword in keywords:
                if re.search(rf'\b{keyword}\b', query_lower):
                    result['targets'].append(target_type)
                    break
        
        return result


class CommandTemplateEngine:
    """Generate commands from templates with parameter substitution"""
    
    def __init__(self):
        self.os_type = platform.system()
        
        # Command templates with placeholders
        self.templates = {
            'windows': {
                'create_file': [
                    'echo. > {filename}',
                    'type nul > {filename}',
                    'copy nul {filename}',
                ],
                'create_file_with_content': [
                    'echo {content} > {filename}',
                ],
                'create_folder': [
                    'mkdir {foldername}',
                    'md {foldername}',
                ],
                'create_nested': [
                    'mkdir {foldername} && echo. > {foldername}\\{filename}',
                    'mkdir {foldername} && type nul > {foldername}\\{filename}',
                ],
                'delete_file': [
                    'del {filename}',
                    'del /f {filename}',
                ],
                'delete_folder': [
                    'rmdir {foldername}',
                    'rd /s /q {foldername}',
                ],
                'rename_file': [
                    'ren {old_name} {new_name}',
                    'rename {old_name} {new_name}',
                ],
                'copy_file': [
                    'copy {source} {destination}',
                ],
                'kill_process': [
                    'taskkill /IM {process}.exe /F',
                    'taskkill /IM {process} /F',
                ],
                'find_files': [
                    'dir /s /b {pattern}',
                    'where /r . {pattern}',
                ],
                'list_folder': [
                    'dir {path}',
                    'dir /b {path}',
                ],
                # Git commands (cross-platform)
                'git_status': ['git status'],
                'git_init': ['git init'],
                'git_add_all': ['git add .'],
                'git_add_file': ['git add {filename}'],
                'git_commit': ['git commit -m "{message}"'],
                'git_push': ['git push'],
                'git_push_origin': ['git push origin {branch}'],
                'git_pull': ['git pull'],
                'git_clone': ['git clone {url}'],
                'git_create_branch': ['git branch {branchname}'],
                'git_checkout': ['git checkout {branchname}'],
                'git_checkout_new': ['git checkout -b {branchname}'],
                'git_list_branches': ['git branch'],
                'git_delete_branch': ['git branch -d {branchname}'],
                'git_merge': ['git merge {branchname}'],
                'git_log': ['git log'],
                'git_log_short': ['git log --oneline'],
                'git_diff': ['git diff'],
                'git_stash': ['git stash'],
                'git_stash_pop': ['git stash pop'],
                'git_stash_list': ['git stash list'],
                'git_fetch': ['git fetch'],
                'git_add_remote': ['git remote add origin {url}'],
                'git_list_remotes': ['git remote -v'],
                'git_tag': ['git tag {tagname}'],
                'git_list_tags': ['git tag'],
                'git_push_tags': ['git push --tags'],
                'git_config_name': ['git config --global user.name "{name}"'],
                'git_config_email': ['git config --global user.email "{email}"'],
                'git_config_list': ['git config --list'],
            },
            'linux': {
                'create_file': [
                    'touch {filename}',
                    '> {filename}',
                ],
                'create_file_with_content': [
                    'echo "{content}" > {filename}',
                ],
                'create_folder': [
                    'mkdir {foldername}',
                    'mkdir -p {foldername}',
                ],
                'create_nested': [
                    'mkdir -p {foldername} && touch {foldername}/{filename}',
                ],
                'delete_file': [
                    'rm {filename}',
                    'rm -f {filename}',
                ],
                'delete_folder': [
                    'rmdir {foldername}',
                    'rm -rf {foldername}',
                ],
                'rename_file': [
                    'mv {old_name} {new_name}',
                ],
                'copy_file': [
                    'cp {source} {destination}',
                ],
                'kill_process': [
                    'pkill {process}',
                    'killall {process}',
                ],
                'find_files': [
                    'find . -name "{pattern}"',
                    'locate {pattern}',
                ],
                'list_folder': [
                    'ls {path}',
                    'ls -la {path}',
                ],
                # Git commands (cross-platform)
                'git_status': ['git status'],
                'git_init': ['git init'],
                'git_add_all': ['git add .'],
                'git_add_file': ['git add {filename}'],
                'git_commit': ['git commit -m "{message}"'],
                'git_push': ['git push'],
                'git_push_origin': ['git push origin {branch}'],
                'git_pull': ['git pull'],
                'git_clone': ['git clone {url}'],
                'git_create_branch': ['git branch {branchname}'],
                'git_checkout': ['git checkout {branchname}'],
                'git_checkout_new': ['git checkout -b {branchname}'],
                'git_list_branches': ['git branch'],
                'git_delete_branch': ['git branch -d {branchname}'],
                'git_merge': ['git merge {branchname}'],
                'git_log': ['git log'],
                'git_log_short': ['git log --oneline'],
                'git_diff': ['git diff'],
                'git_stash': ['git stash'],
                'git_stash_pop': ['git stash pop'],
                'git_stash_list': ['git stash list'],
                'git_fetch': ['git fetch'],
                'git_add_remote': ['git remote add origin {url}'],
                'git_list_remotes': ['git remote -v'],
                'git_tag': ['git tag {tagname}'],
                'git_list_tags': ['git tag'],
                'git_push_tags': ['git push --tags'],
                'git_config_name': ['git config --global user.name "{name}"'],
                'git_config_email': ['git config --global user.email "{email}"'],
                'git_config_list': ['git config --list'],
            }
        }
    
    def generate_command(self, intent: str, params: Dict, os_type: str = None) -> Optional[str]:
        """
        Generate command from template and parameters
        
        Args:
            intent: Command intent (e.g., 'create_file')
            params: Extracted parameters
            os_type: 'windows' or 'linux' (defaults to system OS)
            
        Returns:
            Generated command or None
        """
        if not os_type:
            os_type = 'windows' if 'Windows' in self.os_type else 'linux'
        
        # Get template
        templates = self.templates.get(os_type, {}).get(intent)
        if not templates:
            return None
        
        # Use first template (or select based on params)
        template = templates[0]
        
        # Extract parameters
        extracted = params.get('extracted', {})
        
        # Git command defaults for missing parameters
        git_defaults = {
            'message': 'Update',
            'branchname': 'new-branch',
            'filename': '.',
            'url': '',
            'branch': 'main',
            'tagname': 'v1.0',
            'name': 'Your Name',
            'email': 'your.email@example.com',
        }
        
        # Merge defaults for Git commands
        if intent.startswith('git_'):
            for key, value in git_defaults.items():
                if key not in extracted:
                    extracted[key] = value
        
        # Try to fill template
        try:
            command = template.format(**extracted)
            return command
        except KeyError as e:
            # Missing required parameter
            return None
    
    def generate_from_analysis(self, analysis: Dict) -> Optional[Dict]:
        """
        Generate command from full analysis
        
        Args:
            analysis: Result from extract_command_intent_and_params
            
        Returns:
            Dictionary with command and metadata
        """
        intent = analysis.get('intent')
        targets = analysis.get('targets', [])
        params = analysis.get('parameters', {})
        nested = analysis.get('nested')
        
        if not intent:
            return None
        
        # For Git commands, the intent is already the full template key
        if intent.startswith('git_'):
            template_key = intent
        # Build template key for regular commands
        elif nested:
            template_key = 'create_nested'
        elif intent and targets:
            template_key = f"{intent}_{targets[0]}"
        else:
            return None
        
        # Generate command
        command = self.generate_command(template_key, params)
        
        if command:
            return {
                'success': True,
                'command': command,
                'method': 'template',
                'intent': intent,
                'targets': targets,
                'parameters': params.get('extracted', {}),
                'nested': nested,
                'confidence': 0.95  # High confidence for template matches
            }
        
        return None


def test_parameter_extraction():
    """Test parameter extraction with various queries"""
    print("="*70)
    print("DYNAMIC PARAMETER EXTRACTION TEST")
    print("="*70)
    
    extractor = ParameterExtractor()
    template_engine = CommandTemplateEngine()
    
    test_queries = [
        "create a file named test.txt",
        'create a folder called "MyFolder"',
        "create folder ProjectFiles with file readme.md inside",
        "create file config.json in folder settings",
        "delete file old_data.txt",
        "kill process chrome",
        "rename file old.txt to new.txt",
        "find files with .py extension",
        "create a file named notes.txt with content 'Hello World'",
        "make a directory called TestFolder",
        "create folder Documents and file notes.txt inside it",
    ]
    
    for query in test_queries:
        print(f"\n{'='*70}")
        print(f"Query: '{query}'")
        print('-'*70)
        
        # Extract parameters
        analysis = extractor.extract_command_intent_and_params(query)
        
        print(f"Intent: {analysis['intent']}")
        print(f"Action: {analysis['action']}")
        print(f"Targets: {analysis['targets']}")
        print(f"Parameters: {analysis['parameters']['extracted']}")
        
        if analysis['nested']:
            print(f"Nested Operation: {analysis['nested']}")
        
        # Generate command
        result = template_engine.generate_from_analysis(analysis)
        
        if result and result['success']:
            print(f"\n✓ Generated Command: {result['command']}")
            print(f"  Confidence: {result['confidence']:.0%}")
        else:
            print(f"\n✗ Could not generate command")


if __name__ == "__main__":
    test_parameter_extraction()
