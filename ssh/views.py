import json
import paramiko
from django.shortcuts import render
from django.http import JsonResponse
from .forms import loginForm
from .commands import cd, cat, edit

def index(request):
    context = {
        'form': loginForm()
    }
    return render(request, 'index.html', context)

def ssh_gui(request, command=None):
    if request.method == 'POST':
        if command:
            print(command)
            try:
                username = request.session.get('username')
                password = request.session.get('password')
                host = request.session.get('host')
                port = int(request.session.get('port', 22))  # Default port 22
                
                client = paramiko.SSHClient()
                client.load_system_host_keys()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(host, port, username, password)
                
                data = json.loads(request.body)
                pwd = data.get('pwd', '')

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
                
                else:
                    response_data = {'error': 'Unknown command'}
                
                client.close()
                return JsonResponse(response_data, safe=False)
                
            except paramiko.SSHException as e:
                return JsonResponse({'error': str(e)}, status=500)
            except KeyError as e:
                return JsonResponse({'error': f'Missing key: {str(e)}'}, status=400)
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON'}, status=400)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)

        form = loginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            host = form.cleaned_data['host']
            port = form.cleaned_data['port']
            
            request.session['username'] = username
            request.session['password'] = password
            request.session['host'] = host
            request.session['port'] = port

            context = {
                'username': username,
                'host': host,
                'port': port,
            }
            return render(request, 'ssh_gui.html', context)

    return render(request, 'ssh_gui.html')
