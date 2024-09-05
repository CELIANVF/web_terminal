import http
from django.shortcuts import render
from .forms import loginForm
import paramiko
from .commands import *
import json
from django.http import JsonResponse

# Create your views here.
def index(request):
    context = {
        'form': loginForm()
    }
    return render(request, 'index.html', context)

def ssh_gui(request, command=None):
    # validate the form
    if request.method == 'POST':
        if command is not None:
            print(f'Command: {command}')
            if command == "cd":
                username = request.session['username']
                password = request.session['password']
                host = request.session['host']
                port = request.session['port']
                
                client = paramiko.SSHClient()
                client.load_system_host_keys()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(host, port, username, password)
                
                data = json.loads(request.body)
                
                print(data)
                pwd = data['pwd']
                next = data['cd']
                data = cd(pwd,next,client,request)
                

                return JsonResponse(data, safe=False)
            
        
        form = loginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            host = form.cleaned_data['host']
            port = form.cleaned_data['port']
            print(f'Username: {username}, Password: {password}, Host: {host}, Port: {port}')
            
            # connect to the ssh server
            client = paramiko.SSHClient()
            

            # Load system SSH known hosts
            client.load_system_host_keys()

            # Automatically add the host key if it's not in known hosts
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host, port, username, password)
            
            # check if the connection is successful
            stdin, stdout, stderr = client.exec_command('ls')
            
            
            ls = stdout.read().decode()
            ls = ls.split('\n')
            ls = ls[1:-1]
            ls.append('..')
            
            # get current directory
            stdin, stdout, stderr = client.exec_command('pwd')
            pwd = stdout.read().decode()
            pwd = pwd.strip()
            
            request.session['username'] = username
            request.session['password'] = password
            request.session['host'] = host
            request.session['port'] = port
            request.session['pwd'] = pwd
            
            
            print(pwd)
            print(ls)
            
            
            
            context = {
                'username': username,
                'host': host,
                'port': port,
                'files': ls,
                'pwd': pwd
            }
            return render(request, 'ssh_gui.html', context)
    
    
    return render(request, 'ssh_gui.html')

