#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import json
import os
import keyring
import yaml

class OpenShiftClient:
    def __init__(self, oc_path=None):
        """Initialize the client. oc_path can be set later."""
        self._oc_path = oc_path or self.find_oc_path()
        self.current_cluster_url = None
        self.current_username = None
        print(f"Using oc path: {self._oc_path}")

    def set_oc_path(self, path):
        """Set the path to the oc executable."""
        if os.path.exists(path) and os.path.isfile(path):
            self._oc_path = path
            print(f"Set oc path to: {self._oc_path}")
            return True, "oc path updated successfully."
        else:
            print(f"Error: oc path not found or invalid: {path}")
            return False, f"oc path not found or invalid: {path}"

    def get_oc_path(self):
        """Get the currently configured oc path."""
        return self._oc_path

    def find_oc_path(self):
        """Attempt to find oc.exe in common locations or PATH."""
        # Check if oc is in PATH
        try:
            result = subprocess.run(['where', 'oc'], capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            paths = result.stdout.strip().split('\n')
            if paths:
                print(f"Found oc in PATH: {paths[0]}")
                return paths[0]
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass # Not found in PATH

        # Check common relative path (for portable package)
        relative_path = os.path.join(os.path.dirname(__file__), '..\', '..\', 'oc-cli', 'oc.exe')
        if os.path.exists(relative_path):
            print(f"Found oc in relative path: {relative_path}")
            return os.path.abspath(relative_path)

        print("Warning: oc.exe not found automatically. Please configure the path.")
        return "oc" # Default to just 'oc' hoping it's in PATH

    def _run_command(self, command_args, input_data=None):
        """Run an oc command and return the result."""
        if not self._oc_path or not os.path.exists(self._oc_path):
             # Try finding it again if the path seems invalid
             self._oc_path = self.find_oc_path()
             if not self._oc_path or (self._oc_path != "oc" and not os.path.exists(self._oc_path)):
                 return False, "oc executable path is not configured or invalid.", ""

        command = [self._oc_path] + command_args
        try:
            print(f"Running command: {' '.join(command)}")
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                input=input_data,
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW # Prevent console window flashing
            )
            return True, process.stdout.strip(), process.stderr.strip()
        except FileNotFoundError:
             print(f"Error: oc command not found at '{self._oc_path}'. Make sure it's installed and the path is correct.")
             return False, f"Error: oc command not found at '{self._oc_path}'. Make sure it's installed and the path is correct.", ""
        except subprocess.CalledProcessError as e:
            error_message = e.stderr.strip() or e.stdout.strip() or f"Command failed with exit code {e.returncode}"
            print(f"Command failed: {' '.join(command)}\nError: {error_message}")
            return False, error_message, e.stderr.strip()
        except Exception as e:
            error_message = f"An unexpected error occurred: {e}"
            print(f"Command failed: {' '.join(command)}\nError: {error_message}")
            return False, error_message, str(e)

    def login(self, server_url, username, password):
        """Login to the OpenShift cluster."""
        # Use keyring to securely store/retrieve password if needed, or handle directly
        # For simplicity here, we pass password directly to login command
        success, output, error = self._run_command([
            'login',
            server_url,
            f'--username={username}',
            f'--password={password}',
            '--insecure-skip-tls-verify=true' # Common for dev environments, consider removing for prod
        ])
        if success:
            self.current_cluster_url = server_url
            self.current_username = username
            # Optionally save credentials using keyring here if desired
            return True, f"Successfully logged into {server_url}"
        else:
            return False, f"Login failed: {output}"

    def get_namespaces(self):
        """Get a list of namespaces the user has access to."""
        success, output, error = self._run_command(['get', 'projects', '-o', 'jsonpath={.items[*].metadata.name}'])
        if success:
            return output.split() # Returns a list of names
        else:
            print(f"Error getting namespaces: {output}")
            return [] # Return empty list on error

    def get_pods(self, namespace):
        """Get pods in a specific namespace."""
        success, output, error = self._run_command([
            'get', 'pods',
            '-n', namespace,
            '-o', 'json'
        ])
        if success:
            try:
                data = json.loads(output)
                pods_info = []
                for item in data.get('items', []):
                    name = item.get('metadata', {}).get('name', 'N/A')
                    status = item.get('status', {}).get('phase', 'Unknown')
                    restarts = 0
                    container_statuses = item.get('status', {}).get('containerStatuses', [])
                    if container_statuses:
                        restarts = sum(cs.get('restartCount', 0) for cs in container_statuses)
                    # Calculate age (simplified)
                    creation_timestamp = item.get('metadata', {}).get('creationTimestamp', None)
                    age = "N/A"
                    if creation_timestamp:
                        # Basic age calculation - can be improved
                        from datetime import datetime, timezone
                        try:
                            created = datetime.fromisoformat(creation_timestamp.replace('Z', '+00:00'))
                            now = datetime.now(timezone.utc)
                            delta = now - created
                            if delta.days > 0:
                                age = f"{delta.days}d"
                            elif delta.seconds > 3600:
                                age = f"{delta.seconds // 3600}h"
                            elif delta.seconds > 60:
                                age = f"{delta.seconds // 60}m"
                            else:
                                age = f"{delta.seconds}s"
                        except ValueError:
                            pass # Handle potential parsing errors

                    pods_info.append({
                        "name": name,
                        "status": status,
                        "restarts": restarts,
                        "age": age
                    })
                return pods_info
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON output for pods: {e}")
                return []
        else:
            print(f"Error getting pods in namespace {namespace}: {output}")
            return []

    # --- Methods below are not yet integrated into the web UI ---

    def get_pod_logs(self, namespace, pod_name, previous=False):
        """Get logs for a specific pod."""
        command = ['logs', pod_name, '-n', namespace]
        if previous:
            command.append('--previous')
        success, output, error = self._run_command(command)
        return output if success else f"Error getting logs: {output}"

    def get_pod_details(self, namespace, pod_name):
        """Get detailed information (YAML) for a specific pod."""
        success, output, error = self._run_command(['get', 'pod', pod_name, '-n', namespace, '-o', 'yaml'])
        if success:
            try:
                # Return as a Python dict/list for easier handling, or raw YAML string
                return yaml.safe_load(output)
            except yaml.YAMLError as e:
                print(f"Error parsing pod details YAML: {e}")
                return {"error": "Failed to parse pod details YAML"}
        else:
            return {"error": f"Failed to get pod details: {output}"}

    def save_cluster_config(self, name, server_url, username):
        """Placeholder for saving cluster config (needs web-friendly storage)."""
        # This needs to be implemented using a file or other storage
        print(f"[Placeholder] Save config: {name}, {server_url}, {username}")
        pass

    def load_cluster_configs(self):
        """Placeholder for loading cluster configs."""
        # This needs to be implemented using a file or other storage
        print("[Placeholder] Load configs")
        return {}

    def delete_cluster_config(self, name):
        """Placeholder for deleting cluster config."""
        # This needs to be implemented using a file or other storage
        print(f"[Placeholder] Delete config: {name}")
        pass

    def store_password(self, service_name, username, password):
        """Store password securely using keyring."""
        try:
            keyring.set_password(service_name, username, password)
            print(f"Stored password for {username} at {service_name}")
            return True
        except Exception as e:
            print(f"Error storing password: {e}")
            return False

    def get_password(self, service_name, username):
        """Retrieve password securely using keyring."""
        try:
            return keyring.get_password(service_name, username)
        except Exception as e:
            print(f"Error retrieving password: {e}")
            return None

    def delete_password(self, service_name, username):
        """Delete password from secure storage."""
        try:
            keyring.delete_password(service_name, username)
            print(f"Deleted password for {username} at {service_name}")
            return True
        except Exception as e:
            # Handle case where password might not exist
            if "No password found" in str(e):
                print(f"No password found for {username} at {service_name} to delete.")
                return True
            print(f"Error deleting password: {e}")
            return False