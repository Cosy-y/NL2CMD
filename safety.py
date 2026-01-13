from typing import Dict, List, Tuple, Optional

RISK_CRITICAL = "CRITICAL"
RISK_HIGH = "HIGH"
RISK_MEDIUM = "MEDIUM"
RISK_LOW = "LOW"

RISKY_PATTERNS = {
    "del /s": {
        "severity": RISK_CRITICAL,
        "explanation": "Recursively deletes files - can destroy entire directories",
        "alternative": "Use 'del <specific_file>' to delete one file at a time"
    },
    "rm -rf /": {
        "severity": RISK_CRITICAL,
        "explanation": "DESTROYS ENTIRE SYSTEM - Deletes all files on system",
        "alternative": "Never run this command! Specify exact directory instead"
    },
    "rm -rf": {
        "severity": RISK_CRITICAL,
        "explanation": "Forcefully deletes directory tree - no confirmation",
        "alternative": "Use 'rm -r' for confirmation prompts or specify exact path"
    },
    "format": {
        "severity": RISK_CRITICAL,
        "explanation": "Formats/erases entire disk partition",
        "alternative": "Double-check drive letter before formatting"
    },
    "mkfs": {
        "severity": RISK_CRITICAL,
        "explanation": "Creates new filesystem - erases all data on partition",
        "alternative": "Ensure correct device is specified (e.g., /dev/sdb1 not /dev/sda1)"
    },
    "dd": {
        "severity": RISK_CRITICAL,
        "explanation": "Low-level disk copy - can overwrite wrong drive",
        "alternative": "Triple-check 'if' and 'of' parameters before running"
    },
    
    "shutdown": {
        "severity": RISK_HIGH,
        "explanation": "Shuts down the system",
        "alternative": "Save all work before executing"
    },
    "reboot": {
        "severity": RISK_HIGH,
        "explanation": "Restarts the system immediately",
        "alternative": "Use 'shutdown -r +5' to delay 5 minutes"
    },
    "systemctl stop": {
        "severity": RISK_HIGH,
        "explanation": "Stops system service - may affect system functionality",
        "alternative": "Use 'systemctl restart' to restart instead of stopping"
    },
    "net user": {
        "severity": RISK_HIGH,
        "explanation": "Modifies user accounts - can lock you out",
        "alternative": "Be careful when changing passwords or disabling accounts"
    },
    "chmod 777": {
        "severity": RISK_HIGH,
        "explanation": "Gives full permissions to everyone - security risk",
        "alternative": "Use minimal permissions needed (e.g., chmod 755)"
    },
    
    "del": {
        "severity": RISK_MEDIUM,
        "explanation": "Deletes files - cannot be undone easily",
        "alternative": "Move to recycle bin first or backup important files"
    },
    "rm ": {
        "severity": RISK_MEDIUM,
        "explanation": "Removes files permanently",
        "alternative": "Use 'mv file ~/.Trash' to move to trash instead"
    },
    "kill -9": {
        "severity": RISK_MEDIUM,
        "explanation": "Force kills process without cleanup",
        "alternative": "Try 'kill <pid>' first (allows graceful shutdown)"
    },
    "pkill": {
        "severity": RISK_MEDIUM,
        "explanation": "Kills processes by name - may affect multiple processes",
        "alternative": "Check processes with 'ps aux | grep <name>' first"
    },
    "chown -R": {
        "severity": RISK_MEDIUM,
        "explanation": "Recursively changes file ownership",
        "alternative": "Specify exact directory to avoid unintended changes"
    },
    
    # LOW - Requires caution
    "firewall": {
        "severity": RISK_LOW,
        "explanation": "Modifies firewall settings",
        "alternative": "Backup firewall rules before making changes"
    },
    "ufw": {
        "severity": RISK_LOW,
        "explanation": "Changes firewall configuration",
        "alternative": "Test rules before applying permanently"
    },
    "diskpart": {
        "severity": RISK_LOW,
        "explanation": "Disk partition management tool",
        "alternative": "Use carefully - can affect disk structure"
    },
}

def analyze_command_risk(command: str) -> Dict:
    cmd_lower = command.lower()
    matches = []
    highest_severity = None
    severity_order = [RISK_CRITICAL, RISK_HIGH, RISK_MEDIUM, RISK_LOW]
    
    for pattern, info in RISKY_PATTERNS.items():
        if pattern in cmd_lower:
            matches.append({
                'keyword': pattern,
                'severity': info['severity'],
                'explanation': info['explanation'],
                'alternative': info['alternative']
            })
            
            if highest_severity is None:
                highest_severity = info['severity']
            elif severity_order.index(info['severity']) < severity_order.index(highest_severity):
                highest_severity = info['severity']
    
    return {
        'is_risky': len(matches) > 0,
        'severity': highest_severity,
        'matches': matches,
        'risk_count': len(matches)
    }


def get_severity_color(severity: str) -> str:
    """Get color code for severity level"""
    colors = {
        RISK_CRITICAL: "\033[91m",  # Bright red
        RISK_HIGH: "\033[31m",       # Red
        RISK_MEDIUM: "\033[33m",     # Yellow
        RISK_LOW: "\033[93m",        # Bright yellow
    }
    return colors.get(severity, "")


def reset_color() -> str:
    """Reset terminal color"""
    return "\033[0m"


def confirm_risky_action(command: str, action_context: str = "execute") -> bool:
    """
    Enhanced risky command confirmation with detailed warnings
    
    Args:
        command: Command to check
        action_context: Context (e.g., "execute", "copy")
        
    Returns:
        True if user confirms, False otherwise
    """
    risk_info = analyze_command_risk(command)
    
    if not risk_info['is_risky']:
        return True
    
    severity = risk_info['severity']
    color = get_severity_color(severity)
    reset = reset_color()
    
    # Display warning header
    print(f"\n{'='*70}")
    print(f"{color}⚠️  RISK LEVEL: {severity}{reset}")
    print(f"{'='*70}")
    
    # Display each risk
    for i, match in enumerate(risk_info['matches'], 1):
        print(f"\n{color}Risk #{i}: '{match['keyword']}'{reset}")
        print(f"  📋 Explanation: {match['explanation']}")
        print(f"  💡 Alternative: {match['alternative']}")
    
    print(f"\n{'='*70}")
    print(f"Command to {action_context}: {command}")
    print(f"{'='*70}")
    
    # Get confirmation based on severity
    if severity == RISK_CRITICAL:
        print(f"\n{color}🚨 CRITICAL WARNING: This command can DESTROY DATA or SYSTEM{reset}")
        confirmation = input(f"Type the FULL command to confirm (or 'cancel' to abort): ").strip()
        
        if confirmation == command:
            # Double confirmation for critical
            final = input(f"\n{color}FINAL CONFIRMATION - Type 'I UNDERSTAND THE RISK': {reset}").strip()
            if final == "I UNDERSTAND THE RISK":
                print(f"\n{color}⚠️  Proceeding with CRITICAL command...{reset}")
                return True
        
        print(f"\n✓ Command cancelled for safety")
        return False
    
    elif severity == RISK_HIGH:
        print(f"\n{color}⚠️  HIGH RISK: This command makes system-wide changes{reset}")
        confirmation = input(f"Type 'yes' to proceed or anything else to cancel: ").strip().lower()
        
        if confirmation == "yes":
            return True
        
        print(f"\n✓ Command cancelled")
        return False
    
    else:  # MEDIUM or LOW
        confirmation = input(f"\nProceed? (yes/no): ").strip().lower()
        
        if confirmation == "yes":
            return True
        
        print(f"\n✓ Command cancelled")
        return False


def is_risky_command(command: str) -> bool:
    """
    Check if command is risky
    
    Args:
        command: Command to check
        
    Returns:
        True if risky, False otherwise
    """
    risk_info = analyze_command_risk(command)
    return risk_info['is_risky']


def get_risky_keywords_in_command(command: str) -> List[str]:
    """
    Get list of risky keywords found in command
    
    Args:
        command: Command to check
        
    Returns:
        List of risky keywords found
    """
    risk_info = analyze_command_risk(command)
    return [match['keyword'] for match in risk_info['matches']]


def get_command_safety_report(command: str) -> str:
    """
    Generate detailed safety report for command
    
    Args:
        command: Command to analyze
        
    Returns:
        Formatted safety report string
    """
    risk_info = analyze_command_risk(command)
    
    if not risk_info['is_risky']:
        return "✓ This command appears safe to execute"
    
    report = []
    report.append(f"\n{'='*70}")
    report.append(f"SAFETY REPORT: {command}")
    report.append(f"{'='*70}")
    report.append(f"Risk Level: {risk_info['severity']}")
    report.append(f"Risky Patterns Found: {risk_info['risk_count']}")
    report.append("")
    
    for i, match in enumerate(risk_info['matches'], 1):
        report.append(f"{i}. {match['keyword']} ({match['severity']})")
        report.append(f"   {match['explanation']}")
        report.append(f"   Alternative: {match['alternative']}")
        report.append("")
    
    return "\n".join(report)
