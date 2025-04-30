document.addEventListener('DOMContentLoaded', () => {
    console.log("OpenShift GUI Web Loaded");

    const statusDiv = document.getElementById('status');
    const loginButton = document.getElementById('login-button');
    const loginStatusDiv = document.getElementById('login-status');
    const namespaceSelect = document.getElementById('namespace-select');
    const namespaceStatusDiv = document.getElementById('namespace-status');
    const podStatusDiv = document.getElementById('pod-status');
    const podTable = document.getElementById('pod-table');
    const podTableBody = podTable.querySelector('tbody');
    const ocPathInput = document.getElementById('oc_path');
    const saveOcPathButton = document.getElementById('save-oc-path-button');
    const ocPathStatusDiv = document.getElementById('oc-path-status');

    // Check server status and get initial oc_path on load
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            let statusText = '';
            if (data.status === 'running') {
                statusText = 'Backend server is running. ';
                statusDiv.className = 'success';
            } else {
                statusText = 'Backend server connection failed. ';
                statusDiv.className = 'error';
            }
            // Display oc path info
            if (data.oc_path) {
                statusText += ` | Using oc path: ${data.oc_path}`;
                ocPathInput.value = data.oc_path; // Pre-fill the input
                if (!data.oc_found && data.oc_path !== 'oc') {
                    statusText += ' (Warning: Path not found!)';
                    statusDiv.className = 'error'; // Make status red if path invalid
                }
            } else {
                statusText += ' | oc path not configured.';
            }
            statusDiv.textContent = statusText;
        })
        .catch(error => {
            console.error('Error checking status:', error);
            statusDiv.textContent = 'Error connecting to backend server.';
            statusDiv.className = 'error';
        });

    // Save oc path action
    saveOcPathButton.addEventListener('click', () => {
        const newPath = ocPathInput.value.trim();
        if (!newPath) {
            ocPathStatusDiv.textContent = 'Please enter a path.';
            ocPathStatusDiv.className = 'error';
            return;
        }

        ocPathStatusDiv.textContent = 'Saving path...';
        ocPathStatusDiv.className = '';

        fetch('/api/ocpath', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ oc_path: newPath })
        })
        .then(response => response.json())
        .then(data => {
            ocPathStatusDiv.textContent = data.message;
            ocPathStatusDiv.className = data.success ? 'success' : 'error';
            if (data.success) {
                // Optionally re-fetch status to update the main status line
                fetch('/api/status').then(r => r.json()).then(d => {
                    statusDiv.textContent = `Backend server is running. | Using oc path: ${d.oc_path}`;
                    if (!d.oc_found && d.oc_path !== 'oc') {
                         statusDiv.textContent += ' (Warning: Path not found!)';
                         statusDiv.className = 'error';
                    } else {
                         statusDiv.className = 'success';
                    }
                });
            }
        })
        .catch(error => {
            console.error('Error saving oc path:', error);
            ocPathStatusDiv.textContent = 'Error saving path. Check server connection.';
            ocPathStatusDiv.className = 'error';
        });
    });

    // Login action
    loginButton.addEventListener('click', () => {
        const serverUrl = document.getElementById('server_url').value;
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        loginStatusDiv.textContent = 'Logging in...';
        loginStatusDiv.className = '';

        fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ server_url: serverUrl, username: username, password: password })
        })
        .then(response => response.json())
        .then(data => {
            loginStatusDiv.textContent = data.message;
            loginStatusDiv.className = data.success ? 'success' : 'error';
            if (data.success) {
                fetchNamespaces(); // Fetch namespaces after successful login
            }
        })
        .catch(error => {
            console.error('Login error:', error);
            loginStatusDiv.textContent = 'Login failed. Check server connection.';
            loginStatusDiv.className = 'error';
        });
    });

    // Fetch namespaces
    function fetchNamespaces() {
        namespaceStatusDiv.textContent = 'Fetching namespaces...';
        fetch('/api/namespaces')
            .then(response => response.json())
            .then(data => {
                namespaceSelect.innerHTML = '<option value="">-- Select --</option>'; // Clear existing options
                if (data.namespaces && data.namespaces.length > 0) {
                    data.namespaces.forEach(ns => {
                        const option = document.createElement('option');
                        option.value = ns;
                        option.textContent = ns;
                        namespaceSelect.appendChild(option);
                    });
                    namespaceStatusDiv.textContent = 'Namespaces loaded.';
                } else {
                    namespaceStatusDiv.textContent = 'No namespaces found or error fetching.';
                }
            })
            .catch(error => {
                console.error('Error fetching namespaces:', error);
                namespaceStatusDiv.textContent = 'Error fetching namespaces.';
            });
    }

    // Fetch pods when namespace changes
    namespaceSelect.addEventListener('change', () => {
        const selectedNamespace = namespaceSelect.value;
        podTableBody.innerHTML = ''; // Clear previous pods
        podTable.style.display = 'none';

        if (!selectedNamespace) {
            podStatusDiv.textContent = 'Select a namespace to view pods.';
            return;
        }

        podStatusDiv.textContent = `Fetching pods for namespace "${selectedNamespace}"...`;

        fetch(`/api/pods/${selectedNamespace}`)
            .then(response => response.json())
            .then(data => {
                if (data.pods && data.pods.length > 0) {
                    data.pods.forEach(pod => {
                        const row = podTableBody.insertRow();
                        row.insertCell().textContent = pod.name;
                        row.insertCell().textContent = pod.status;
                        row.insertCell().textContent = pod.restarts;
                        row.insertCell().textContent = pod.age;
                    });
                    podTable.style.display = 'table';
                    podStatusDiv.textContent = ''; // Clear status message
                } else {
                    podStatusDiv.textContent = `No pods found in namespace "${selectedNamespace}".`;
                }
            })
            .catch(error => {
                console.error('Error fetching pods:', error);
                podStatusDiv.textContent = `Error fetching pods for namespace "${selectedNamespace}".`;
            });
    });

    // Initial fetch if needed (e.g., if already logged in via session - not implemented yet)
    // fetchNamespaces();

}); // End DOMContentLoaded
