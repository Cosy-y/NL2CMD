import re
from typing import List, Dict, Tuple, Optional
from intelligence_engine import IntelligenceEngine

class MultiCommandProcessor:
    COMMAND_SEPARATORS = [
        r'\s+and\s+then\s+',
        r'\s+then\s+',
        r'\s+and\s+',
        r'\s+also\s+',
        r'\s+after\s+that\s+',
        r'\s+next\s+',
        r'[,;]\s+',
    ]
    
    # Patterns that indicate multiple commands
    MULTI_COMMAND_INDICATORS = [
        'and then',
        'then',
        'and',
        'also',
        'after that',
        'next',
    ]
    
    def __init__(self, intelligence_engine: Optional[IntelligenceEngine] = None):
        """
        Initialize multi-command processor
        
        Args:
            intelligence_engine: Intelligence engine for processing individual commands
        """
        self.engine = intelligence_engine or IntelligenceEngine()
    
    def is_multi_command(self, query: str) -> bool:
        """
        Detect if a query contains multiple commands
        
        Args:
            query: Natural language query
            
        Returns:
            True if query appears to contain multiple commands
        """
        query_lower = query.lower()
        
        # Check for multiple action verbs
        action_verbs = ['create', 'make', 'delete', 'remove', 'copy', 'move', 
                       'list', 'show', 'find', 'kill', 'stop', 'start', 'run',
                       'open', 'close', 'install', 'update', 'rename', 'change']
        
        # Count total occurrences of action verbs
        words = query_lower.split()
        action_count = sum(words.count(verb) for verb in action_verbs)
        
        # If we have 2+ action verbs AND a conjunction, it's likely multi-command
        has_conjunction = any(indicator in query_lower for indicator in self.MULTI_COMMAND_INDICATORS)
        
        return action_count >= 2 and has_conjunction
    
    def split_commands(self, query: str) -> List[str]:
        """
        Split a query into individual commands
        
        Args:
            query: Natural language query containing multiple commands
            
        Returns:
            List of individual command strings
        """
        # Try each separator pattern
        for separator_pattern in self.COMMAND_SEPARATORS:
            parts = re.split(separator_pattern, query, flags=re.IGNORECASE)
            if len(parts) > 1:
                # Clean up the parts
                commands = [part.strip() for part in parts if part.strip()]
                return commands
        
        # If no separator found, return original query as single command
        return [query]
    
    def extract_context_references(self, query: str, previous_commands: List[Dict]) -> str:
        """
        Detect and resolve context references like "inside the folder", "in it", etc.
        
        Args:
            query: Current command query
            previous_commands: List of previously processed commands
            
        Returns:
            Modified query with context resolved
        """
        if not previous_commands:
            return query
        
        # Get the last folder/directory that was created or referenced
        last_folder = None
        for cmd in reversed(previous_commands):
            cmd_text = cmd.get('command', '').lower()
            
            # Check if it's a mkdir/create folder command
            if 'mkdir' in cmd_text or 'md ' in cmd_text:
                # Extract folder name from mkdir command
                # Patterns: mkdir foldername, mkdir "folder name", md foldername
                match = re.search(r'(?:mkdir|md)\s+([^\s&|;]+)', cmd.get('command', ''))
                if match:
                    last_folder = match.group(1).strip('"').strip("'")
                    break
        
        if not last_folder:
            return query
        
        # Check for context references
        context_patterns = [
            r'\binside\s+(?:the\s+)?folder\b',
            r'\bin\s+(?:the\s+)?folder\b',
            r'\binside\s+it\b',
            r'\bin\s+it\b',
            r'\binside\s+that\s+folder\b',
            r'\bin\s+that\s+folder\b',
            r'\binside\s+there\b',
        ]
        
        has_context_ref = any(re.search(pattern, query.lower()) for pattern in context_patterns)
        
        if has_context_ref:
            # Instead of removing the context phrase, replace it with the actual path
            # Look for the filename pattern
            filename_patterns = [
                (r'(file\s+named?\s+)([^\s]+)(\s+inside\s+(?:the\s+)?folder)', r'\1{folder}\\\2'),
                (r'(file\s+named?\s+)([^\s]+)(\s+in\s+(?:the\s+)?folder)', r'\1{folder}\\\2'),
                (r'(file\s+named?\s+)([^\s]+)(\s+inside\s+it)', r'\1{folder}\\\2'),
                (r'(file\s+named?\s+)([^\s]+)(\s+in\s+it)', r'\1{folder}\\\2'),
                (r'(file\s+called\s+)([^\s]+)(\s+inside\s+(?:the\s+)?folder)', r'\1{folder}\\\2'),
                (r'(file\s+called\s+)([^\s]+)(\s+in\s+(?:the\s+)?folder)', r'\1{folder}\\\2'),
                (r'(file\s+called\s+)([^\s]+)(\s+inside\s+it)', r'\1{folder}\\\2'),
                (r'(file\s+called\s+)([^\s]+)(\s+in\s+it)', r'\1{folder}\\\2'),
            ]
            
            modified_query = query
            for pattern, replacement in filename_patterns:
                replacement_str = replacement.replace('{folder}', last_folder)
                modified_query = re.sub(pattern, replacement_str, modified_query, flags=re.IGNORECASE)
                if modified_query != query:
                    break
            
            return modified_query
        
        return query
    
    def process_multi_command(self, query: str) -> Dict:
        """
        Process a multi-command query
        
        Args:
            query: Natural language query containing multiple commands
            
        Returns:
            Dictionary with command chain information
        """
        if not self.is_multi_command(query):
            # Single command - process normally
            result = self.engine.process_query(query)
            result['is_multi_command'] = False
            result['command_count'] = 1
            return result
        
        # Split into individual commands
        individual_commands = self.split_commands(query)
        
        # Process each command
        processed_commands = []
        all_successful = True
        
        for i, cmd_query in enumerate(individual_commands, 1):
            # Apply context resolution for commands after the first one
            if i > 1:
                cmd_query = self.extract_context_references(cmd_query, processed_commands)
            
            result = self.engine.process_query(cmd_query)
            
            if result.get('success'):
                processed_commands.append({
                    'order': i,
                    'query': cmd_query,
                    'command': result.get('command'),
                    'method': result.get('method'),
                    'confidence': result.get('confidence'),
                    'success': True
                })
            else:
                processed_commands.append({
                    'order': i,
                    'query': cmd_query,
                    'command': None,
                    'method': None,
                    'confidence': 0,
                    'success': False,
                    'error': result.get('error', 'Unknown error')
                })
                all_successful = False
        
        # Build chained command
        if all_successful:
            # Get OS-specific command separator
            import platform
            if "Windows" in platform.system():
                # Windows uses && for chaining
                separator = " && "
            else:
                # Linux/Mac uses &&
                separator = " && "
            
            chained_command = separator.join([cmd['command'] for cmd in processed_commands])
        else:
            chained_command = None
        
        return {
            'success': all_successful,
            'is_multi_command': True,
            'command_count': len(individual_commands),
            'individual_commands': processed_commands,
            'chained_command': chained_command,
            'method': 'multi_command',
            'confidence': min([cmd['confidence'] for cmd in processed_commands]) if all_successful else 0,
            'query': query
        }
    
    def format_output(self, result: Dict) -> str:
        """
        Format multi-command result for display
        
        Args:
            result: Result from process_multi_command
            
        Returns:
            Formatted string for display
        """
        if not result.get('is_multi_command'):
            return f"Command: {result.get('command', 'N/A')}"
        
        lines = []
        lines.append(f"Multi-Command Chain ({result['command_count']} commands)")
        lines.append("=" * 60)
        
        for cmd in result['individual_commands']:
            status = "✓" if cmd['success'] else "✗"
            lines.append(f"{status} Step {cmd['order']}: {cmd['query']}")
            if cmd['success']:
                lines.append(f"   → {cmd['command']}")
                lines.append(f"   Method: {cmd['method']} | Confidence: {cmd['confidence']:.0%}")
            else:
                lines.append(f"   Error: {cmd.get('error', 'Unknown')}")
            lines.append("")
        
        if result['success']:
            lines.append("Chained Command:")
            lines.append(f"→ {result['chained_command']}")
        else:
            lines.append("⚠️  Cannot chain - some commands failed")
        
        return "\n".join(lines)


def detect_and_process_multi_command(query: str, engine: Optional[IntelligenceEngine] = None) -> Dict:
    """
    Convenience function to detect and process multi-commands
    
    Args:
        query: Natural language query
        engine: Optional intelligence engine instance
        
    Returns:
        Processed result (single or multi-command)
    """
    processor = MultiCommandProcessor(engine)
    return processor.process_multi_command(query)


if __name__ == "__main__":
    # Test the multi-command processor
    print("=" * 70)
    print("MULTI-COMMAND PROCESSOR TEST")
    print("=" * 70)
    
    test_queries = [
        "create a folder named test",  # Single command
        "create a folder named tanish and create a file named readme.txt",  # Multi-command
        "list all files and then show system info",  # Multi-command
        "delete temp files and clear cache",  # Multi-command
        "make a directory called projects and then create a file called index.html",  # Multi-command
    ]
    
    processor = MultiCommandProcessor()
    
    for query in test_queries:
        print(f"\n{'=' * 70}")
        print(f"Query: '{query}'")
        print(f"{'=' * 70}")
        
        result = processor.process_multi_command(query)
        print(processor.format_output(result))
        print()
