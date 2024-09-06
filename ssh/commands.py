import paramiko
import base64
import os
import shlex

def create_ssh_client(host, port, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port=port, username=username, password=password)
    return client

def copy_file_to_local(username, password, host, remote_file_path, local_directory):
    try:
        # Setup SSH connection
        ssh = create_ssh_client(host, 22, username, password)
        
        # Compress the file by encoding it to base64 before copying
        ssh.exec_command(f'cat {remote_file_path} | base64 | tr -d "\\n" > {remote_file_path}.base64')
        
        # Create SFTP session for file transfer
        sftp = paramiko.SFTPClient.from_transport(ssh.get_transport())
        
        # Define local file path
        local_file_path = os.path.join(local_directory, os.path.basename(remote_file_path + '.base64'))
        
        # Copy the base64 file from remote to local
        sftp.get(remote_file_path + '.base64', local_file_path)
        
        # Clean up: remove base64 file on the server
        ssh.exec_command(f'rm {remote_file_path}.base64')
        
        sftp.close()
        ssh.close()


        print(f"File {remote_file_path} successfully copied to {local_file_path}")
    
    except Exception as e:
        print(f"Error: {e}")


def cd(pwd, next_dir, connection, request):
    try:
        command = f'cd {shlex.quote(pwd + "/" + next_dir)} && ls -la {shlex.quote(pwd + "/" + next_dir)}'
        print(command)
        stdin, stdout, stderr = connection.exec_command(command)

        ls = stdout.read().decode().split('\n')
        # print(ls)
        ls = [line.split() for line in ls[1:-1]]

        if next_dir == '.':
            request.session['pwd'] = pwd
        elif next_dir == '..':
            pwd_parts = pwd.rstrip('/').split('/')
            request.session['pwd'] = '/'.join(pwd_parts[:-1])
        else:
            request.session['pwd'] = f'{pwd}/{next_dir}'

        data = {
            'files': ls,
            'pwd': request.session['pwd'],
        }

        return data

    except Exception as e:
        return {'error': str(e)}


def cat(pwd, file, connection, request):
    try:
        file_path = shlex.quote(f'{pwd}/{file}')
        file_extension = file.split('.')[-1].lower()

        if file_extension in ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'ico', 'svg', 'webp']:
            # print(f"Copying file {file_path} to local")

            # Create a temp directory if it does not exist
            if not os.path.exists('./temp'):
                os.makedirs('./temp')

            copy_file_to_local(request.session.get('username'), request.session.get('password'), 
                               request.session.get('host'), file_path, './temp')

            print(f"File {file} copied to local")
            
            content = None
            local_file_path = os.path.join('./temp', os.path.basename(file_path + '.base64'))
            with open(local_file_path, 'r') as f:
                content = f.read()
                
            
                
            content = f'data:image/{file_extension};base64,{content}'
            
            # remove the file
            os.remove(local_file_path)

        else:
            command = f'cat {file_path}'
            stdin, stdout, stderr = connection.exec_command(command)
            content = stdout.read().decode()

        data = {
            'content': content,
            'pwd': pwd,
        }

        return data

    except Exception as e:
        return {'error': str(e)}


def edit(pwd, file, connection, content, request):
    try:
        file_path = shlex.quote(f'{pwd}/{file}')
        escaped_content = content.replace("'", "'\\''").replace('"', '\\"')
        command = f'echo "{escaped_content}" > {file_path}'
        stdin, stdout, stderr = connection.exec_command(command)

        # Check for errors
        error = stderr.read().decode()
        if error:
            return {'error': error}

        data = {
            'content': escaped_content,
            'pwd': pwd,
        }

        return data

    except Exception as e:
        return {'error': str(e)}
