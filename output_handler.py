from typing import Dict, Optional
import platform

class OutputHandler:
    
    # Color codes for terminal output
    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
    }
    
    # Method badges
    BADGES = {
        'ml': '🤖 ML',
        'rule': '📋 RULE',
        'hybrid': '🔀 HYBRID',
        'none': '❌ NONE'
    }
    
    def __init__(self, use_colors: bool = True, verbose: bool = False):
        """
        Initialize output handler
        
        Args:
            use_colors: Whether to use colored output
            verbose: Show detailed information
        """
        self.use_colors = use_colors
        self.verbose = verbose
        self.os_type = platform.system()
    
    def format_result(self, result: Dict) -> str:
        """
        Format command result for display
        
        Args:
            result: Result dictionary from intelligence engine
            
        Returns:
            Formatted string
        """
        lines = []
        
        # Header
        lines.append(self._format_header())
        
        # Query
        if 'query' in result:
            lines.append(self._format_query(result['query']))
        
        # Method used
        method = result.get('method', 'none')
        confidence = result.get('confidence', 0.0)
        lines.append(self._format_method(method, confidence))
        
        # Command
        if result.get('success'):
            lines.append(self._format_command(result['command'], success=True))
            
            # Show intent if available
            if self.verbose and 'intent' in result:
                lines.append(self._format_field('Intent', result['intent']))
            
            # Show OS type if available
            if self.verbose and 'os_type' in result:
                lines.append(self._format_field('OS', result['os_type']))
        else:
            error_msg = result.get('error', 'No command found')
            lines.append(self._format_error(error_msg))
        
        # Warning if present
        if 'warning' in result:
            lines.append(self._format_warning(result['warning']))
        
        # Fallback notice
        if result.get('fallback'):
            lines.append(self._colorize('⚠️  Using low-confidence prediction', 'yellow'))
        
        # Separator
        lines.append(self._separator())
        
        return '\n'.join(lines)
    
    def format_suggestions(self, suggestions: list) -> str:
        """
        Format multiple suggestions
        
        Args:
            suggestions: List of suggestion dictionaries
            
        Returns:
            Formatted string
        """
        if not suggestions:
            return "No suggestions available"
        
        lines = []
        lines.append(self._colorize("\n💡 Suggestions:", 'cyan'))
        
        for i, suggestion in enumerate(suggestions, 1):
            method = suggestion.get('method', 'unknown')
            confidence = suggestion.get('confidence', 0.0)
            command = suggestion.get('command', 'N/A')
            
            badge = self.BADGES.get(method, method.upper())
            conf_str = f"{confidence:.0%}" if confidence > 0 else "N/A"
            
            line = f"{i}. [{badge}] {command} ({conf_str})"
            lines.append(self._colorize(line, 'cyan'))
        
        return '\n'.join(lines)
    
    def _format_header(self) -> str:
        """Format header"""
        return self._colorize("═" * 60, 'blue')
    
    def _separator(self) -> str:
        """Format separator"""
        return self._colorize("─" * 60, 'blue')
    
    def _format_query(self, query: str) -> str:
        """Format query display"""
        return self._colorize(f"Query: ", 'cyan') + self._colorize(f"'{query}'", 'bold')
    
    def _format_method(self, method: str, confidence: float) -> str:
        """Format method badge"""
        badge = self.BADGES.get(method, method.upper())
        conf_str = f" ({confidence:.0%} confidence)" if confidence > 0 else ""
        
        color = 'green' if method == 'ml' and confidence >= 0.6 else 'yellow' if method == 'ml' else 'blue'
        
        return self._colorize(f"Method: {badge}{conf_str}", color)
    
    def _format_command(self, command: str, success: bool = True) -> str:
        """Format command output"""
        if success:
            prefix = self._colorize("✓ Command: ", 'green')
            cmd = self._colorize(command, 'bold')
        else:
            prefix = self._colorize("✗ Command: ", 'red')
            cmd = command
        
        return prefix + cmd
    
    def _format_error(self, error: str) -> str:
        """Format error message"""
        return self._colorize(f"✗ Error: {error}", 'red')
    
    def _format_warning(self, warning: str) -> str:
        """Format warning message"""
        return self._colorize(f"⚠️  Warning: {warning}", 'yellow')
    
    def _format_field(self, name: str, value: str) -> str:
        """Format a general field"""
        return self._colorize(f"{name}: ", 'cyan') + str(value)
    
    def _colorize(self, text: str, color: str) -> str:
        """
        Apply color to text
        
        Args:
            text: Text to colorize
            color: Color name
            
        Returns:
            Colored text (if colors enabled)
        """
        if not self.use_colors:
            return text
        
        color_code = self.COLORS.get(color, '')
        reset_code = self.COLORS['reset']
        
        return f"{color_code}{text}{reset_code}"
    
    def print_result(self, result: Dict):
        """
        Print formatted result
        
        Args:
            result: Result dictionary
        """
        print(self.format_result(result))
    
    def print_suggestions(self, suggestions: list):
        """
        Print formatted suggestions
        
        Args:
            suggestions: List of suggestions
        """
        print(self.format_suggestions(suggestions))


def format_output(result: Dict, use_colors: bool = True, verbose: bool = False) -> str:
    """
    Convenience function to format output
    
    Args:
        result: Result dictionary
        use_colors: Use colored output
        verbose: Show detailed info
        
    Returns:
        Formatted string
    """
    handler = OutputHandler(use_colors, verbose)
    return handler.format_result(result)


if __name__ == "__main__":
    # Test the output handler
    print("OUTPUT HANDLER TEST\n")
    
    handler = OutputHandler(use_colors=True, verbose=True)
    
    # Test successful ML result
    test_result_ml = {
        'success': True,
        'query': 'list all files',
        'command': 'dir',
        'method': 'ml',
        'confidence': 0.95,
        'intent': 'list_files',
        'os_type': 'windows'
    }
    
    handler.print_result(test_result_ml)
    print()
    
    # Test successful rule result
    test_result_rule = {
        'success': True,
        'query': 'show hidden files',
        'command': 'dir /a',
        'method': 'rule',
        'confidence': 1.0
    }
    
    handler.print_result(test_result_rule)
    print()
    
    # Test low confidence with warning
    test_result_warning = {
        'success': True,
        'query': 'do something weird',
        'command': 'echo test',
        'method': 'ml',
        'confidence': 0.45,
        'fallback': True,
        'warning': 'Low confidence, please verify'
    }
    
    handler.print_result(test_result_warning)
    print()
    
    # Test failure
    test_result_fail = {
        'success': False,
        'query': 'completely invalid input',
        'method': 'none',
        'confidence': 0.0,
        'error': 'No matching command found'
    }
    
    handler.print_result(test_result_fail)
    print()
    
    # Test suggestions
    test_suggestions = [
        {'command': 'dir', 'confidence': 0.95, 'method': 'ml'},
        {'command': 'ls -la', 'confidence': 0.75, 'method': 'rule'},
        {'command': 'Get-ChildItem', 'confidence': 0.60, 'method': 'ml'}
    ]
    
    handler.print_suggestions(test_suggestions)
