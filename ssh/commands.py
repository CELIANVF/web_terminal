def cd(pwd,next,connection,request):
    # Change directory
    print(f'cd {pwd}/{next} | ls')
    stdin, stdout, stderr = connection.exec_command(f'cd {pwd}/{next} | ls {pwd}/{next}')
    
    ls = stdout.read().decode()
    ls = ls.split('\n')
    ls = ls[1:-1]
    ls.append('..')
    print(ls)
    
    if next == '..':
        pwd = pwd.split('/')
        pwd = pwd[:-1]
        pwd = '/'.join(pwd)
        request.session['pwd'] = f'{pwd}'
    else:        
        request.session['pwd'] = f'{pwd}/{next}'
    data = {
        'files': ls,
        'pwd': request.session['pwd'],
    }

    return data
    
    