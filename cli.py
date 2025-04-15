#!/usr/bin/env python3
import argparse
from core.models.session import Session
from core.commands.ssh_command import SSHCommand
from core.commands.local_command import LocalCommand
from core.ai import get_ai_provider

def main():
    parser = argparse.ArgumentParser(description='RamiGPT - AI-powered privilege escalation tool')
    parser.add_argument('--host', help='Target host')
    parser.add_argument('--port', type=int, default=22, help='SSH port')
    parser.add_argument('--username', required=True, help='SSH username')
    parser.add_argument('--password', required=True, help='SSH password')
    parser.add_argument('--provider', default='openai', choices=['openai', 'deepseek'], help='AI provider')
    parser.add_argument('--max-requests', type=int, default=10, help='Max AI requests')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--scan', choices=['beroot', 'peas', 'all', 'none'],
                       default='all',
                       help='Run security scanners')
    parser.add_argument('--auto', action='store_true', 
                       help='Run full automated escalation')
    parser.add_argument('--local', action='store_true',
                       help='Run in local mode (no SSH)')
    parser.add_argument('--target', default='root',
                       help='Target user for escalation')
    parser.add_argument('--system', choices=['linux', 'windows'],
                          default='linux', help='Target system type')
    
    args = parser.parse_args()
    
    # Initialize components
    ai_provider = get_ai_provider(args.provider)
    # Validate arguments
    if not args.local and not args.host:
        parser.error("--host is required when using SSH mode")
    if args.local and (args.host or args.port != 22 or args.username or args.password):
        print("Warning: SSH arguments ignored in local mode")

    # Initialize command executor
    if args.local:
        command_executor = LocalCommand()
        print("[!] Running in local mode")
    else:
        command_executor = SSHCommand(
            host=args.host,
            port=args.port,
            username=args.username,
            password=args.password
        )
    
    session = Session(
        username=args.username,
        password=args.password,
        system=args.system,
        target=args.target,
        ai_provider=ai_provider,
        command_executor=command_executor,
        max_requests=args.max_requests,
    )
    
    if args.scan:
        if args.scan == 'all':
            session.auto_escalate()
        elif args.scan == 'none':
            print("[!] No scanners will be run.")
        else:
            session.run_scan(args.scan)
    else:
        session.auto_escalate()
    
    session.run()

if __name__ == "__main__":
    main()