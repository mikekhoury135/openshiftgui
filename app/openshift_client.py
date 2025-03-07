#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import json
import os
import keyring
from pathlib import Path
import yaml

from .settings import Settings

class OpenShiftClient:
    def __init__(self):
        self.current_context = None
        self.current_namespace = None
        self.settings = Settings()
    
    def _get_oc_command(self):
        """Get the oc command with the proper path"""
        oc_path = self.settings.get_oc_path()
        if oc_path:
            return oc_path
        return "oc"  # Default to using PATH if no custom path
    
    def login(self, server_url, username, password):
        """Login to OpenShift cluster using provided credentials"""
        try:
            oc = self._get_oc_command()
            cmd = [oc, "login", server_url, "-u", username, "-p", password, "--insecure-skip-tls-verify=true"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # If login successful, save the credentials securely
            if "Login successful" in result.stdout:
                # Use the system's credential store to save the password
                service_name = f"openshift_gui_{server_url}"
                keyring.set_password(service_name, username, password)
                
                # Set current context
                self.current_context = server_url
                return True, result.stdout
            
            return False, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr
        except FileNotFoundError:
            return False, f"OpenShift CLI not found. Please configure the path in Settings."
    
    def get_namespaces(self):
        """Get list of namespaces from current context"""
        try:
            oc = self._get_oc_command()
            cmd = [oc, "get", "namespaces", "-o", "json"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            json_data = json.loads(result.stdout)
            namespaces = [item["metadata"]["name"] for item in json_data["items"]]
            return True, namespaces
        except subprocess.CalledProcessError as e:
            return False, e.stderr
        except FileNotFoundError:
            return False, f"OpenShift CLI not found. Please configure the path in Settings."
    
    def set_namespace(self, namespace):
        """Set the current namespace"""
        try:
            oc = self._get_oc_command()
            cmd = [oc, "project", namespace]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.current_namespace = namespace
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr
        except FileNotFoundError:
            return False, f"OpenShift CLI not found. Please configure the path in Settings."
    
    def get_pods(self, namespace=None):
        """Get list of pods from specified namespace or current namespace"""
        try:
            ns = namespace if namespace else self.current_namespace
            if not ns:
                return False, "No namespace selected"
            
            oc = self._get_oc_command()
            cmd = [oc, "get", "pods", "-n", ns, "-o", "json"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return True, json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            return False, e.stderr
        except FileNotFoundError:
            return False, f"OpenShift CLI not found. Please configure the path in Settings."
    
    def get_pod_details(self, pod_name, namespace=None):
        """Get detailed information about a specific pod"""
        try:
            ns = namespace if namespace else self.current_namespace
            if not ns:
                return False, "No namespace selected"
            
            oc = self._get_oc_command()
            cmd = [oc, "describe", "pod", pod_name, "-n", ns]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr
        except FileNotFoundError:
            return False, f"OpenShift CLI not found. Please configure the path in Settings."
    
    def get_pod_logs(self, pod_name, container_name=None, namespace=None):
        """Get logs for a pod or specific container in a pod"""
        try:
            ns = namespace if namespace else self.current_namespace
            if not ns:
                return False, "No namespace selected"
            
            oc = self._get_oc_command()
            cmd = [oc, "logs", pod_name, "-n", ns]
            if container_name:
                cmd.extend(["-c", container_name])
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr
        except FileNotFoundError:
            return False, f"OpenShift CLI not found. Please configure the path in Settings."
    
    def get_saved_clusters(self):
        """Get list of saved cluster configurations"""
        config_dir = Path.home() / ".openshift_gui"
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / "clusters.yml"
        
        if not config_file.exists():
            return []
        
        with open(config_file, "r") as f:
            try:
                clusters = yaml.safe_load(f) or []
                return clusters
            except Exception:
                return []
    
    def save_cluster(self, name, url, username):
        """Save cluster configuration (without password)"""
        config_dir = Path.home() / ".openshift_gui"
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / "clusters.yml"
        
        # Load existing clusters
        if config_file.exists():
            with open(config_file, "r") as f:
                try:
                    clusters = yaml.safe_load(f) or []
                except Exception:
                    clusters = []
        else:
            clusters = []
        
        # Update or add new cluster
        for i, cluster in enumerate(clusters):
            if cluster.get("name") == name:
                clusters[i] = {"name": name, "url": url, "username": username}
                break
        else:
            clusters.append({"name": name, "url": url, "username": username})
        
        # Save back to file
        with open(config_file, "w") as f:
            yaml.dump(clusters, f)
        
        return True
    
    def is_oc_installed(self):
        """Check if OpenShift CLI (oc) is installed"""
        try:
            oc = self._get_oc_command()
            subprocess.run([oc, "version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False