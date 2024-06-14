import subprocess
import os
import sys
import time

# Paths to the directories containing the frontend and backend projects
PROJECT_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # Root directory of the project
FRONTEND_DIR = os.path.join(PROJECT_ROOT_DIR, 'client')
BACKEND_DIR = os.path.join(PROJECT_ROOT_DIR, 'api')

# Path to the setup script
SETUP_SCRIPT_PATH = os.path.join(PROJECT_ROOT_DIR, 'setup.ps1')

def is_python_installed():
    try:
        subprocess.run(["python", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

def is_node_installed():
    try:
        subprocess.run(["node", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

def are_python_dependencies_installed():
    try:
        requirements_path = r'requirements.txt'
        subprocess.run(["pip", "check", "-r", requirements_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

def are_node_dependencies_installed():
    try:
        package_json_path = os.path.join(FRONTEND_DIR, 'package.json')
        print(package_json_path + "--------------------------------------")
        if not os.path.exists(package_json_path):
            return False
        subprocess.run(["npm", "install", "--dry-run"], shell=True, cwd=FRONTEND_DIR, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

def run_setup_script():
    try:
        subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", SETUP_SCRIPT_PATH], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def start_flask_server():
    os.chdir(BACKEND_DIR)
    os.environ['FLASK_APP'] = 'server.py'  
    subprocess.Popen(['flask', 'run'])

def start_react_server():
    os.chdir(FRONTEND_DIR)
    subprocess.Popen(['npm', 'start'], shell=True)

if __name__ == "__main__":
    setup_needed = False

    if not is_python_installed():
        print("Python is not installed.")
        setup_needed = True

    if not is_node_installed():
        print("Node.js is not installed.")
        setup_needed = True

    if not are_python_dependencies_installed():
        print("Python dependencies are not installed.")
        setup_needed = True

    if not are_node_dependencies_installed():
        print("Node.js dependencies are not installed.")
        setup_needed = True

    if setup_needed:
        print("Running setup script...")
        if not run_setup_script():
            print("Setup script failed. Please check the setup.ps1 script and try again.")
            sys.exit(1)
    
    # Start Flask server
    start_flask_server()
    print("Starting Flask server...")

    # Give the Flask server some time to start
    time.sleep(5)
    
    # Start React server
    start_react_server()
    print("Starting React server...")
    
    # Change back to the project root directory
    os.chdir(PROJECT_ROOT_DIR)
