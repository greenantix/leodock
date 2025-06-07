#!/usr/bin/env python3
"""
Unix-style LLM Communication Commands for LeoDock
Implements talk, write, wall, and screen commands for LLM interaction
"""

import requests
import json
import sys
import time
import argparse
from chat_history_manager import ChatHistoryManager

class LLMCommands:
    def __init__(self):
        self.base_url = "http://127.0.0.1:1234/v1"
        self.chat_manager = ChatHistoryManager()
        self.active_sessions = {}
        self.message_queue = []
        
    def llm_talk(self, target_llm, message, interactive=False):
        """Interactive chat with specified LLM (like unix 'talk' command)"""
        print(f"🗣️  Starting talk session with {target_llm.upper()}")
        print(f"Type your messages. Type 'quit' or 'exit' to end session.")
        print("=" * 50)
        
        session_id = f"talk_session_{int(time.time())}"
        conversation_count = 0
        
        if not interactive:
            # Single message mode
            response = self._send_to_llm(target_llm, message)
            print(f"{target_llm.upper()}: {response}")
            
            self.chat_manager.store_conversation(
                prompt=f"Talk to {target_llm}: {message}",
                response=response,
                session_id=session_id,
                llm_analysis={"command": "llm_talk", "target": target_llm},
                metadata={"command_type": "talk", "interactive": False}
            )
            return
        
        # Interactive mode
        try:
            while True:
                user_input = input(f"\nYou → {target_llm.upper()}: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print(f"🔚 Talk session with {target_llm.upper()} ended")
                    break
                
                if not user_input:
                    continue
                
                response = self._send_to_llm(target_llm, user_input)
                print(f"{target_llm.upper()} → You: {response}")
                
                # Store conversation
                self.chat_manager.store_conversation(
                    prompt=f"Talk to {target_llm}: {user_input}",
                    response=response,
                    session_id=session_id,
                    llm_analysis={"command": "llm_talk", "target": target_llm, "conversation_number": conversation_count},
                    metadata={"command_type": "talk", "interactive": True}
                )
                conversation_count += 1
                
        except KeyboardInterrupt:
            print(f"\n🔚 Talk session with {target_llm.upper()} interrupted")
    
    def llm_write(self, target_llm, message, urgent=False):
        """Send one-way message to LLM (like unix 'write' command)"""
        priority = "URGENT" if urgent else "normal"
        print(f"📝 Writing {priority} message to {target_llm.upper()}")
        
        response = self._send_to_llm(target_llm, message)
        
        print(f"✉️  Message sent to {target_llm.upper()}")
        print(f"📨 {target_llm.upper()} responded: {response}")
        
        self.chat_manager.store_conversation(
            prompt=f"Write to {target_llm}: {message}",
            response=response,
            session_id=f"write_{int(time.time())}",
            llm_analysis={"command": "llm_write", "target": target_llm, "urgent": urgent},
            metadata={"command_type": "write", "priority": priority}
        )
    
    def llm_wall(self, message):
        """Broadcast message to all LLMs (like unix 'wall' command)"""
        print(f"📢 Broadcasting message to ALL LLMs")
        print(f"📨 Message: {message}")
        print("=" * 50)
        
        llms = ["leo", "archie"]
        responses = {}
        session_id = f"wall_{int(time.time())}"
        
        for llm in llms:
            try:
                response = self._send_to_llm(llm, f"Broadcast message: {message}")
                responses[llm] = response
                print(f"📻 {llm.upper()}: {response}")
                
                # Store each response
                self.chat_manager.store_conversation(
                    prompt=f"Wall broadcast: {message}",
                    response=response,
                    session_id=session_id,
                    llm_analysis={"command": "llm_wall", "target": llm, "broadcast": True},
                    metadata={"command_type": "wall", "broadcast_id": session_id}
                )
                
            except Exception as e:
                print(f"❌ Failed to reach {llm.upper()}: {e}")
                responses[llm] = f"Error: {e}"
        
        print(f"\n📊 Broadcast complete. {len([r for r in responses.values() if not r.startswith('Error')])} LLMs responded.")
        return responses
    
    def llm_screen(self, session_name="default"):
        """Shared working session with LLMs (like unix 'screen' command)"""
        print(f"🖥️  Starting shared screen session: {session_name}")
        print(f"Multiple LLMs can collaborate in this session")
        print(f"Commands: @leo <message>, @archie <message>, @all <message>, 'detach' to exit")
        print("=" * 60)
        
        session_id = f"screen_{session_name}_{int(time.time())}"
        
        try:
            while True:
                user_input = input(f"\n[{session_name}] > ").strip()
                
                if user_input.lower() in ['detach', 'exit', 'quit']:
                    print(f"🔚 Detached from screen session: {session_name}")
                    break
                
                if not user_input:
                    continue
                
                # Parse screen commands
                if user_input.startswith('@'):
                    parts = user_input.split(' ', 1)
                    if len(parts) < 2:
                        print("Usage: @llm <message> or @all <message>")
                        continue
                    
                    target = parts[0][1:].lower()  # Remove @
                    message = parts[1]
                    
                    if target == "all":
                        self.llm_wall(f"Screen session {session_name}: {message}")
                    elif target in ["leo", "archie"]:
                        response = self._send_to_llm(target, f"Screen session: {message}")
                        print(f"🖥️  {target.upper()}: {response}")
                        
                        self.chat_manager.store_conversation(
                            prompt=f"Screen {session_name} to {target}: {message}",
                            response=response,
                            session_id=session_id,
                            llm_analysis={"command": "llm_screen", "target": target, "session": session_name},
                            metadata={"command_type": "screen", "session_name": session_name}
                        )
                    else:
                        print(f"Unknown LLM: {target}. Available: leo, archie, all")
                else:
                    print("In screen session, use @llm <message> to communicate")
                    
        except KeyboardInterrupt:
            print(f"\n🔚 Screen session {session_name} interrupted")
    
    def _send_to_llm(self, llm_name, message):
        """Send message to specified LLM"""
        llm_name = llm_name.lower()
        
        if llm_name == "leo":
            return self._send_to_leo(message)
        elif llm_name == "archie":
            return self._send_to_archie(message)
        else:
            return f"Unknown LLM: {llm_name}"
    
    def _send_to_leo(self, message):
        """Send message to Leo (chat LLM)"""
        try:
            response = requests.post(f"{self.base_url}/chat/completions", 
                json={
                    "model": "meta-llama-3.1-8b-instruct",
                    "messages": [
                        {"role": "system", "content": "You are Leo in LeoDock. Respond helpfully and concisely to messages from Claude Code."},
                        {"role": "user", "content": message}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 300
                })
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            return f"Leo error: HTTP {response.status_code}"
        except Exception as e:
            return f"Leo error: {str(e)}"
    
    def _send_to_archie(self, message):
        """Send message to Archie (embedding LLM) - simulate response"""
        try:
            response = requests.post(f"{self.base_url}/embeddings",
                json={
                    "model": "text-embedding-nomic-embed-text-v1.5-embedding",
                    "input": message
                })
            
            if response.status_code == 200:
                embedding = response.json()['data'][0]['embedding']
                return f"Generated {len(embedding)}D embedding for your message. Semantic analysis complete."
            return f"Archie error: HTTP {response.status_code}"
        except Exception as e:
            return f"Archie error: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="Unix-style LLM Communication Commands")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # llm_talk command
    talk_parser = subparsers.add_parser('talk', help='Interactive chat with LLM')
    talk_parser.add_argument('llm', choices=['leo', 'archie'], help='Target LLM')
    talk_parser.add_argument('message', nargs='?', help='Message to send (optional for interactive mode)')
    talk_parser.add_argument('-i', '--interactive', action='store_true', help='Start interactive session')
    
    # llm_write command
    write_parser = subparsers.add_parser('write', help='Send one-way message to LLM')
    write_parser.add_argument('llm', choices=['leo', 'archie'], help='Target LLM')
    write_parser.add_argument('message', help='Message to send')
    write_parser.add_argument('-u', '--urgent', action='store_true', help='Mark as urgent')
    
    # llm_wall command
    wall_parser = subparsers.add_parser('wall', help='Broadcast message to all LLMs')
    wall_parser.add_argument('message', help='Message to broadcast')
    
    # llm_screen command
    screen_parser = subparsers.add_parser('screen', help='Shared working session with LLMs')
    screen_parser.add_argument('session', nargs='?', default='default', help='Session name')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    llm_commands = LLMCommands()
    
    try:
        if args.command == 'talk':
            if args.message:
                llm_commands.llm_talk(args.llm, args.message, interactive=args.interactive)
            else:
                llm_commands.llm_talk(args.llm, "", interactive=True)
        
        elif args.command == 'write':
            llm_commands.llm_write(args.llm, args.message, urgent=args.urgent)
        
        elif args.command == 'wall':
            llm_commands.llm_wall(args.message)
        
        elif args.command == 'screen':
            llm_commands.llm_screen(args.session)
            
    except Exception as e:
        print(f"❌ Command error: {e}")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Demo mode
        print("🚀 LLM Commands Demo")
        print("=" * 40)
        
        llm_commands = LLMCommands()
        
        # Demo write command
        print("\n1. Testing llm_write command:")
        llm_commands.llm_write("leo", "Hello Leo! This is a test of the write command.")
        
        # Demo wall command
        print("\n2. Testing llm_wall command:")
        llm_commands.llm_wall("Testing broadcast to all LLMs in LeoDock!")
        
        print("\n✅ Demo complete!")
        print("\nUsage examples:")
        print("  python llm_commands.py talk leo 'Hello Leo!'")
        print("  python llm_commands.py write archie 'Generate embedding for this text'")
        print("  python llm_commands.py wall 'Broadcast message'")
        print("  python llm_commands.py screen mysession")
    else:
        main()