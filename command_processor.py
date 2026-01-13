import subprocess
import pyperclip
from safety import confirm_risky_action
from intelligence_engine import IntelligenceEngine
from output_handler import OutputHandler
from multi_command_processor import MultiCommandProcessor

def safe_input(prompt):
    try:
        return input(prompt).strip().lower()
    except EOFError:
        print("Input ended (EOF). Skipping user interaction.")
        return "n"

_engine = None
_output_handler = None
_multi_processor = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = IntelligenceEngine()
    return _engine

def get_output_handler():
    global _output_handler
    if _output_handler is None:
        _output_handler = OutputHandler(use_colors=True, verbose=False)
    return _output_handler

def get_multi_processor():
    global _multi_processor
    if _multi_processor is None:
        _multi_processor = MultiCommandProcessor(get_engine())
    return _multi_processor

def process_command(nl_cmd, handle_nl_cmd=None):
    engine = get_engine()
    output_handler = get_output_handler()
    multi_processor = get_multi_processor()
    
    if multi_processor.is_multi_command(nl_cmd):
        print("🔗 Detected multi-command query. Processing each command...\n")
        result = multi_processor.process_multi_command(nl_cmd)
        
        print(multi_processor.format_output(result))
        
        if not result.get('success'):
            print("\n❌ Unable to process multi-command query.")
            return result
        
        cli_cmd = result.get('chained_command', '')
        
        if not confirm_risky_action(cli_cmd, action_context="execute"):
            result['execution_cancelled'] = True
            return result
        
        confirm = safe_input("\nDo you want to execute this command chain? (y/n): ")
        if confirm == "y":
            try:
                exec_result = subprocess.run(cli_cmd, shell=True, capture_output=True, text=True)
                print("\n--- Command Output ---")
                print(exec_result.stdout)
                if exec_result.stderr:
                    print("\n--- Command Error ---")
                    print(exec_result.stderr)
                result['executed'] = True
                result['exec_output'] = exec_result.stdout
            except Exception as e:
                print(f"Error executing command: {e}")
                result['execution_error'] = str(e)
        else:
            print("Command not executed.")
            result['executed'] = False
        
        if not confirm_risky_action(cli_cmd, action_context="copy"):
            return result
        
        copy_confirm = safe_input("Do you want to copy this command chain to the clipboard? (y/n): ")
        if copy_confirm == "y":
            pyperclip.copy(cli_cmd)
            print("Command chain copied to clipboard.")
            result['copied'] = True
        else:
            print("Command not copied.")
            result['copied'] = False
        
        return result
    
    result = engine.process_query(nl_cmd)
    
    output_handler.print_result(result)
    
    if not result.get('success') or not result.get('command'):
        print("\n❌ Unable to convert query to command.")
        return result
    
    cli_cmd = result['command']
    
    if not confirm_risky_action(cli_cmd, action_context="execute"):
        result['execution_cancelled'] = True
        return result
    
    confirm = safe_input("\nDo you want to execute this command? (y/n): ")
    if confirm == "y":
        try:
            exec_result = subprocess.run(cli_cmd, shell=True, capture_output=True, text=True)
            print("\n--- Command Output ---")
            print(exec_result.stdout)
            if exec_result.stderr:
                print("\n--- Command Error ---")
                print(exec_result.stderr)
            result['executed'] = True
            result['exec_output'] = exec_result.stdout
        except Exception as e:
            print(f"Error executing command: {e}")
            result['execution_error'] = str(e)
    else:
        print("Command not executed.")
        result['executed'] = False
    
    if not confirm_risky_action(cli_cmd, action_context="copy"):
        return result
    
    copy_confirm = safe_input("Do you want to copy this command to the clipboard? (y/n): ")
    if copy_confirm == "y":
        pyperclip.copy(cli_cmd)
        print("Command copied to clipboard.")
        result['copied'] = True
    else:
        print("Command not copied.")
        result['copied'] = False
    
    return result
