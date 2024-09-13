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
            const fileName = file[8]; // Assuming file name is at index 8

            const tdIcon = document.createElement('td');
            const icon = document.createElement('i');

            // Determine the file type and set appropriate icon class
            if (file[0][0] === 'd') { // Directory
                icon.classList.add('fas', 'fa-folder');
                tr.onclick = () => ssh_gui(fileName);
                tr.classList.add('directory');
            } else if (file[0][0] === 'l') { // Symlink
                icon.classList.add('fas', 'fa-link');
                tr.onclick = () => ssh_gui(fileName);
                tr.classList.add('directory');
            } else { // Regular file
                icon.classList.add('fas', 'fa-file');
                tr.onclick = () => file_edit(fileName);
                tr.classList.add('file');
            }

            // Add icon to the first column
            tdIcon.appendChild(icon);
            tr.appendChild(tdIcon);

            // Add file name and other details in other columns
            Object.values(file).forEach((element, index) => {
                const td = document.createElement('td');
                if (index !== 8) { // Skip file name as it's already handled
                    td.innerHTML = element;
                } else {
                    td.innerHTML = fileName; // File name
                }
                tr.appendChild(td);
            });

            filelist.appendChild(tr);
        });

        document.getElementById('pwd').innerHTML = newPwd;

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


// Establish WebSocket connection
const socket = new WebSocket('ws://127.0.0.1:8000/ws/terminal/');

socket.onopen = function(e) {
    console.log("WebSocket connection established.");
};

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log("Message from server:", data.output);
    
    // Append the received output to the terminal <pre> element
    const terminal = document.getElementById("terminal");
    terminal.textContent += data.output; // textContent to keep it non-editable
    terminal.scrollTop = terminal.scrollHeight; // Auto scroll to the bottom
};

socket.onerror = function(e) {
    console.error("WebSocket error:", e);
};

socket.onclose = function(e) {
    console.log("WebSocket connection closed:", e);
};

// Send the command when pressing "Enter"
document.getElementById("command-input").addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
        e.preventDefault();
        const command = e.target.value.trim();  // Get the entered command
        console.log("Command entered:", command);
        
        sendCommand(command);
        e.target.value = "";  // Clear the input field after sending
    }
});

// Function to send the command to the WebSocket server
function sendCommand(command) {
    socket.send(JSON.stringify({ command: command }));
}
