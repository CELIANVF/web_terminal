import re
import paramiko

# Dictionary to store client shells for each session
shell_sessions = {}

def open_persistent_shell(session):
    """
    Opens a persistent shell session using query parameters (GET) from the request.
    """
    print(f"Opening new shell session for user: {session}")
    username = session.get('username')
    password = session.get('password')
    host = session.get('host', None)
    port = session.get('port', 22) # Default port 22

    if not all([username, password, host]):
        raise ValueError("Missing SSH credentials or host information.")

    # Initialize the SSH client
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port, username, password)

    # Open an interactive shell
    shell = client.invoke_shell(term='dumb')

    return shell

def close_persistent_shell(session_key):
    """
    Closes the persistent shell session and removes it from the dictionary.
    """
    shell = shell_sessions.get(session_key)
    if shell:
        shell.close()
        del shell_sessions[session_key]


def read_shell_output(shell, buffer_size=1024, timeout=1):
    """
    Reads the output from the shell with a timeout to avoid blocking.
    Continuously reads from the shell until all output is received.
    Removes unwanted terminal control sequences.
    """
    output = ""
    shell.settimeout(timeout)
    
    while True:
        if shell.recv_ready():
            # Read the available data from the shell in chunks
            part = shell.recv(buffer_size).decode('utf-8')
            output += part
        else:
            break  # Exit if no more data is available to read

    # Remove unwanted terminal control sequences using regex
    clean_output = re.sub(r'\x1B\[[0-9;]*[a-zA-Z]', '', output)  # Matches escape sequences

    return clean_output


