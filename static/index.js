document.addEventListener("DOMContentLoaded", () => ssh_gui(''));



async function ssh_gui(file) {
    try {
        const pwd = document.getElementById("pwd").innerHTML;
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        const response = await fetch('./cd/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
            body: JSON.stringify({ pwd, cd: file })
        });

        if (!response.ok) throw new Error('Network response was not ok ' + response.statusText);
        const data = await response.json();
        const files = data.files;
        const newPwd = data.pwd;
        const filelist = document.getElementById('filelist');
        console.log(data);

        filelist.innerHTML = ''; // Clear existing list

        files.forEach(file => {
            const tr = document.createElement('tr');
            if (file[0][0] === 'd' || file[0][0] === 'l') {
                tr.onclick = () => ssh_gui(file[8]);
                tr.classList.add('directory');
            } else {
                tr.onclick = () => file_edit(file[8]);
                tr.classList.add('file');
            }

            Object.values(file).forEach(element => {
                const td = document.createElement('td');
                td.innerHTML = element;
                tr.appendChild(td);
            });

            filelist.appendChild(tr);
        });

        document.getElementById('pwd').innerHTML = newPwd || '/';

    } catch (error) {
        console.error('There was a problem with the fetch operation:', error);
    }
}

async function file_edit(file, editor) {
    try {
        const pwd = document.getElementById('pwd').innerHTML;
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        const response = await fetch('./cat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({ pwd, file })
        });

        if (!response.ok) throw new Error('Network response was not ok ' + response.statusText);

        const data = await response.json();
        const content = data["content"];
        const ext = file.split('.').pop().toLowerCase(); // Use lowerCase for case-insensitivity

        if (['png', 'jpg', 'jpeg', 'gif', 'bmp', 'ico', 'webp'].includes(ext)) {
            const image = new Image();
            image.src = content;
            image.style.height = '100%';

            const file_view = document.getElementById('file_view');
            file_view.innerHTML = '';
            file_view.appendChild(image);

            document.getElementById('modal-00').style.display = 'flex';
            return;
        }

        textarea = document.createElement('textarea');
        textarea.id = 'output';
        textarea.style.height = '100%';
        textarea.style.width = '100%';
        textarea.style.resize = 'none';
        textarea.style.border = 'none';
        textarea.style.padding = '10px';
        textarea.style.fontFamily = 'monospace';
        textarea.style.fontSize = '16px';
        textarea.style.color = 'black';
        textarea.style.backgroundColor = 'white';
        textarea.style.overflow = 'auto';
        textarea.style.whiteSpace = 'pre-wrap';
        textarea.style.wordWrap = 'break-word';
        textarea.style.lineHeight = '1.5';
        textarea.style.boxSizing = 'border-box';
        textarea.style.borderRadius = '5px';

        const file_view = document.getElementById('file_view');
        file_view.innerHTML = '';
        file_view.appendChild(textarea);


        // Initialize CodeMirror editor
        const editor = CodeMirror.fromTextArea(textarea, {
            lineNumbers: true,
            mode: "htmlmixed", // Change mode if needed
            theme: "dracula",
            matchBrackets: true
        });
        editor.setValue(content);
        document.getElementById('filename').value = file;
        document.getElementById('modal-00').style.display = 'flex';

    } catch (error) {
        console.error('There was a problem with the fetch operation:', error);
    }
}

function close_modal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

async function save() {
    try {
        const content = editor.getValue();
        const filename = document.getElementById('filename').value;
        const pwd = document.getElementById('pwd').innerHTML;
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        const response = await fetch('./save/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({ pwd, filename, content })
        });

        if (!response.ok) throw new Error('Network response was not ok ' + response.statusText);
        close_modal('modal-00');

    } catch (error) {
        console.error('There was a problem with the fetch operation:', error);
    }
}
