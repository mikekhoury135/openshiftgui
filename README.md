# OpenShift GUI

A user-friendly desktop application for OpenShift CLI that runs on Windows 11 as a portable executable with no installation required.

## For Users

### Quick Start

1. Download and extract the `OpenShiftGUI-Portable.zip` file
2. Place the OpenShift CLI (`oc.exe`) in the included `oc-cli` folder or anywhere on your system
3. Run `OpenShiftGUI.exe` 
4. In the application, go to Settings > Preferences and configure the path to your `oc.exe` file
5. Connect to your OpenShift cluster and start exploring!

### Features

- No installation required - runs as a standalone executable
- Easy configuration of OpenShift CLI path - no admin access needed
- Secure credential management for cluster connections
- Intuitive interface for browsing namespaces and pods
- View detailed pod information, health status and logs
- Light and dark theme options

### Working with OpenShift GUI

#### Connecting to a Cluster

1. Enter your cluster details in the Cluster Configuration tab:
   - Cluster Name (for your reference)
   - Server URL
   - Username
   - Password
2. Click "Login" to connect
3. Optionally, save the connection for future use

#### Exploring Your Cluster

1. After connecting, go to the "Namespaces" tab and select a namespace
2. View pods in the "Pods" tab
3. Click on any pod to see its details, health information, and logs

## For Developers

### Requirements

- Windows 11
- Python 3.8 or higher
- Required Python packages (see requirements.txt)

### Building from Source

1. Clone this repository
2. Run the build script to create the executable:
   ```
   build.bat
   ```
3. Create the portable distribution package:
   ```
   create_portable_package.bat
   ```
4. The portable application package will be created in the `OpenShiftGUI-Portable` folder

### Project Structure

- `main.py` - Main application entry point
- `app/` - Application modules
  - `main_window.py` - Main application window
  - `openshift_client.py` - OpenShift CLI wrapper
  - `settings.py` - Application settings management
  - `widgets/` - UI components
- `build.bat` - Script to build the standalone executable
- `create_portable_package.bat` - Script to create the portable distribution package

## Security Note

Credentials are stored securely using the Windows Credential Manager.

## License

MIT

# OpenShift GUI (Web Edition)

A user-friendly web interface for the OpenShift CLI (`oc.exe`) that runs locally on your machine.

## For Users

### Requirements

- Windows (Tested on 11, should work on 10)
- Python 3.8 or higher installed and added to your PATH.
- OpenShift CLI (`oc.exe`) downloaded.

### Quick Start

1.  **Download/Clone:** Get the application files (e.g., download as ZIP and extract, or clone the repository).
2.  **Open Terminal:** Open a PowerShell terminal in the application's main directory (e.g., `c:\\Users\\mikek\\openshiftgui`).
3.  **Install Dependencies:** Run the following command to install required Python packages:
    ```powershell
    # Optional but recommended: Create and activate a virtual environment
    # python -m venv venv
    # .\venv\Scripts\Activate.ps1

    pip install -r requirements.txt
    ```
4.  **Run the Server:** Start the local web server:
    ```powershell
    python server.py
    ```
5.  **Access in Browser:** Open your web browser and navigate to:
    [http://127.0.0.1:5000](http://127.0.0.1:5000)
6.  **Configure `oc.exe` Path:**

    *   The application will try to find `oc.exe` automatically (in PATH or a local `oc-cli` folder).
    *   If needed, use the "Settings" section in the web interface to enter the full path to your `oc.exe` file and click "Save Path".
7.  **Connect:** Use the "Cluster Connection" section to log in to your OpenShift cluster.
8.  **Explore:** Browse namespaces and pods using the interface.

### Features

- Runs locally - no data leaves your machine except to your cluster.
- Web-based interface accessible from your browser.
- Easy configuration of OpenShift CLI path via the UI.
- Secure credential management for cluster connections (using `keyring` and Windows Credential Manager).
- Browse namespaces and pods.
- (Future: View pod details, logs, etc.)

## For Developers

### Project Structure

- `server.py`: Main Flask application, API endpoints.
- `requirements.txt`: Python dependencies.
- `app/`: Application modules
  - `openshift_client.py`: Wrapper for executing `oc` commands.
  - `templates/`: HTML files (e.g., `index.html`).
  - `static/`: CSS and JavaScript files.
- `README.md`: This file.
- `SECURITY_ASSESSMENT.md`: Security details.

### Running in Debug Mode

The server runs in debug mode by default (`debug=True` in `server.py`), which provides auto-reloading when code changes and more detailed error messages in the browser.

## Security Note

- The web server only listens on `127.0.0.1` (localhost), meaning it's only accessible from your own machine.
- Cluster passwords, when used with the login function, are passed directly to `oc login`. Secure storage via `keyring` is available in the client but not fully integrated into the login flow yet.
- Review `SECURITY_ASSESSMENT.md` for more details.

## License

MIT