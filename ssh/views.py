import json
import paramiko
from django.shortcuts import render
from django.http import JsonResponse
from .forms import loginForm
from .commands import cd, cat, edit
from .ssh_utils import open_persistent_shell


def index(request):
    context = {
        'form': loginForm()
    }
    return render(request, 'index.html', context)




def ssh_gui(request, command=None):
    # if request.method == 'POST':
        # Start a persistent shell if not already active
        # if 'start_shell' in request.POST:
        #     shell = open_persistent_shell(request)
        #     return JsonResponse({'status': 'Shell session started.'})

        # Handle terminal command execution
    if command:
        # Handle specific file commands (cd, cat, save)
        username = request.session.get('username')
        password = request.session.get('password')
        host = request.session.get('host')
        port = int(request.session.get('port', 22))  # Default port 22

        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, port, username, password)

        data = json.loads(request.body)
        pwd = data.get('pwd', '')  # Current working directory

        if command == "cd":
            next_dir = data.get('cd')
            response_data = cd(pwd, next_dir, client, request)

        elif command == "cat":
            file = data.get('file')
            response_data = cat(pwd, file, client, request)

        elif command == "save":
            file_content = data.get('content')
            filename = data.get('filename')
            response_data = edit(pwd, filename, client, file_content, request)

        client.close()
        return JsonResponse(response_data)

    # Handle login form and setup SSH connection
    form = loginForm(request.POST)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        host = form.cleaned_data['host']
        port = form.cleaned_data['port']

        # Save login data in session
        request.session['username'] = username
        request.session['password'] = password
        request.session['host'] = host
        request.session['port'] = port

        context = {
            'username': username,
            'host': host,
            'port': port,
        }
        
        # run persistent shell
        # open_persistent_shell(request)
        
        
        return render(request, 'ssh_gui.html', context)

    return render(request, 'ssh_gui.html')
