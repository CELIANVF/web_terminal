import asyncio
import json
import re
from channels.generic.websocket import AsyncWebsocketConsumer
import paramiko
from .ssh_utils import open_persistent_shell, close_persistent_shell

# Dictionary to store active shell sessions per user/session
shell_sessions = {}
streaming_tasks = {}  # Dictionary to keep track of streaming tasks

class TerminalConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        session = self.scope["session"]
        if not session:
            await self.send(text_data=json.dumps({"error": "No session data"}))
            return

        session_key = session.session_key
        if not session_key:
            await self.send(text_data=json.dumps({"error": "No session key"}))
            return

        # Get the existing shell session
        shell = shell_sessions.get(session_key)
        if not shell:
            # If no active shell session exists, open a new one using session data
            try:
                shell = open_persistent_shell(session)
                shell_sessions[session_key] = shell
                # Start streaming the shell output
                streaming_task = asyncio.create_task(self.stream_shell_output(shell, session_key))
                streaming_tasks[session_key] = streaming_task
            except ValueError as e:
                await self.send(text_data=json.dumps({"error": str(e)}))
                return
        # Accept the WebSocket connection
        
        
        await self.accept()

    async def disconnect(self, close_code):
        # Ensure to close the shell session properly when the WebSocket disconnects
        session_key = self.scope["session"].session_key
        if session_key and session_key in shell_sessions:
            close_persistent_shell(shell_sessions[session_key])
            del shell_sessions[session_key]
            # Cancel the streaming task if it exists
            if session_key in streaming_tasks:
                streaming_tasks[session_key].cancel()
                del streaming_tasks[session_key]

    async def receive(self, text_data):
        # Receive and process the WebSocket message
        data = json.loads(text_data)
        command = data.get('command', '')

        await self.execute_ssh_command(command)

    async def execute_ssh_command(self, command):
        session = self.scope["session"]
        if not session:
            await self.send(text_data=json.dumps({"error": "No session data"}))
            return

        session_key = session.session_key
        if not session_key:
            await self.send(text_data=json.dumps({"error": "No session key"}))
            return

        # Get the existing shell session
        shell = shell_sessions.get(session_key)
        if not shell:
            # If no active shell session exists, open a new one using session data
            try:
                shell = open_persistent_shell(session)
                shell_sessions[session_key] = shell
                # Start streaming the shell output
                streaming_task = asyncio.create_task(self.stream_shell_output(shell, session_key))
                streaming_tasks[session_key] = streaming_task
            except ValueError as e:
                await self.send(text_data=json.dumps({"error": str(e)}))
                return

        # Send the command to the shell
        shell.send(command + '\n')

    async def stream_shell_output(self, shell, session_key, buffer_size=1024, timeout=1):
        shell.settimeout(timeout)
        try:
            while True:
                if shell.recv_ready():
                    output = shell.recv(buffer_size).decode('utf-8')
                    clean_output = re.sub(r'\x1B\[[0-9;]*[a-zA-Z]', '', output)
                    await self.send(text_data=json.dumps({"output": clean_output}))
                else:
                    await asyncio.sleep(0.1)  # Small delay to avoid busy-waiting
        except asyncio.CancelledError:
            # Handle the cancellation of the task (when session disconnects)
            print(f"Streaming task for session {session_key} cancelled.")
        except Exception as e:
            await self.send(text_data=json.dumps({"error": f"Error reading output: {str(e)}"}))
