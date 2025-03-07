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