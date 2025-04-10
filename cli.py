#!/usr/bin/env python3
import argparse
from core.models.session import Session
from core.commands.ssh_command import SSHCommand
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
    
    args = parser.parse_args()
    
    # Initialize components
    ai_provider = get_ai_provider(args.provider)
    command_executor = SSHCommand(
        host=args.host,
        port=args.port,
        username=args.username,
        password=args.password
    )
    
    session = Session(
        username=args.username,
        password=args.password,
        system="Linux",
        target_user="root",
        ai_provider=ai_provider,
        command_executor=command_executor,
        max_requests=args.max_requests
    )
    
    session.run()

if __name__ == "__main__":
    main()