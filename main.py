#!/usr/bin/env python3

from command_processor import process_command
import argparse
import platform
import sys

def print_banner():
    banner = """
╔═══════════════════════════════════════════════════════════╗
║              NL2CMD - Natural Language to CLI             ║
║                   Hybrid ML + Rule Engine                 ║
╚═══════════════════════════════════════════════════════════╝
"""
    print(banner)

def main():
    parser = argparse.ArgumentParser(
        description="Natural language to command line interface converter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  nl2cmd "list all files"
  nl2cmd "show system information" 
  nl2cmd -i                          # Start REPL mode
  nl2cmd --train                     # Train ML model
        """
    )
    
    parser.add_argument(
        "nl_cmd", 
        nargs="?", 
        type=str, 
        help="Natural language command to convert to CLI command"
    )
    
    parser.add_argument(
        "-i", "--repl", 
        action="store_true", 
        help="Start in interactive REPL mode"
    )
    
    parser.add_argument(
        "--train",
        action="store_true",
        help="Train the ML model from training data"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="NL2CMD v3.0 (Advanced ML + Fuzzy Search)"
    )

    args = parser.parse_args()
    
    if args.train:
        print("Training ML model...")
        try:
            import train_model
            train_model.main()
        except Exception as e:
            print(f"Error during training: {e}")
            sys.exit(1)
        return
    
    print_banner()
    
    os_name = platform.system()
    print(f"Detected OS: {os_name}")
    print(f"Mode: {'REPL' if args.repl else 'Single Command'}\n")
    
    if args.repl:
        print("Starting REPL mode...")
        print("Commands:")
        print("  - 'exit' or 'quit' to exit")
        print("  - 'help' for assistance")
        print()
        
        last_query = None
        last_command = None
        
        while True:
            try:
                user_input = input("n2c> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ("exit", "quit"):
                    print("\n👋 Exiting REPL mode. Goodbye!")
                    break
                
                if user_input.lower() == "help":
                    print_help()
                    continue
                
                print()
                result = process_command(user_input)
                print()
                
                last_query = user_input
                last_command = result.get('command') if isinstance(result, dict) else None
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Exiting REPL mode.")
                break
            except EOFError:
                print("\n\n👋 EOF received. Exiting REPL mode.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
    
    else:
        if not args.nl_cmd:
            print("❌ No command provided. Use -h for help or -i for REPL mode.")
            return
        
        print(f"Processing: '{args.nl_cmd}'\n")
        process_command(args.nl_cmd)

def print_help():
    help_text = """
╔═══════════════════════════════════════════════════════════╗
║                       NL2CMD HELP                         ║
╠═══════════════════════════════════════════════════════════╣
║ Commands:                                                 ║
║   exit, quit  - Exit REPL mode                           ║
║   help        - Show this help message                   ║
║                                                           ║
║ Examples:                                                 ║
║   list all files                                         ║
║   show system information                                ║
║   kill chrome                                            ║
║   get my IP address                                      ║
║   clean temporary files                                  ║
║   shutdown computer                                      ║
╚═══════════════════════════════════════════════════════════╝
"""
    print(help_text)

    

