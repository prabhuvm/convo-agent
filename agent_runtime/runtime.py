import json
import os
import sys
import zipfile
import tempfile
import importlib
import subprocess
import shutil
import boto3
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

S3_PATH_PREFIX = "s3://social-agent-app/app-zip/"
# Set up AWS region (optional if your EC2 instance is in the same region as your S3 bucket)
aws_region = os.getenv("AWS_REGION")

# Create S3 client without explicit credentials
if aws_region:
    s3_client = boto3.client('s3', region_name=aws_region)
else:
    s3_client = boto3.client('s3')

app = Flask(__name__)


def list_directory_contents(path):
    print("Agent dir and contents: ", path)
    contents = os.listdir(path)
    for item in contents:
        print(item)
def download_and_extract_agent(s3_path):
    bucket_name, key = s3_path.replace("s3://", "").split("/", 1)

    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
        s3_client.download_fileobj(bucket_name, key, temp_file)
        temp_file_path = temp_file.name

    extract_dir = tempfile.mkdtemp()

    with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    os.unlink(temp_file_path)

    return extract_dir

def load_agent(agent_dir):
    venv_dir = os.path.join(agent_dir, 'venv')
    if os.path.exists(venv_dir):
        # Use the packed venv
        activate_this = os.path.join(venv_dir, 'bin', 'activate_this.py')
        exec(open(activate_this).read(), {'__file__': activate_this})

        # Get the Python executable from the agent's venv
        if sys.platform == 'win32':
            python_executable = os.path.join(venv_dir, 'Scripts', 'python.exe')
        else:
            python_executable = os.path.join(venv_dir, 'bin', 'python')
    else:
        # If no venv, use the current Python interpreter
        python_executable = sys.executable

        # Install dependencies from requirements.txt
        requirements_file = os.path.join(agent_dir, 'requirements.txt')
        if os.path.exists(requirements_file):
            subprocess.run([python_executable, "-m", "pip", "install", "-r", requirements_file], check=True)

    # Add the agent directory to the Python path
    sys.path.insert(0, agent_dir)

    try:
        # Use importlib.util.spec_from_file_location to load the module
        spec = importlib.util.spec_from_file_location("agent", os.path.join(agent_dir, "agent.py"))
        agent_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agent_module)

        agent_class = getattr(agent_module, 'Agent')
        return agent_class()
    except Exception as e:
        print(f"Error loading agent: {str(e)}")
        return None
    finally:
        # Remove the agent directory from the Python path
        sys.path.pop(0)

        # Deactivate the agent's venv if it was used
        if 'deactivate' in globals():
            deactivate()

@app.route('/execute_agent', methods=['POST'])
def execute_agent():
    try:
        data = request.json
        print("Request received: ", data)  # Log the incoming request
        s3_file = data.get('s3_path')
        s3_path = S3_PATH_PREFIX + s3_file
        print(f"Full S3 path: {s3_path}")  # Log the full S3 path
        agent_input = data.get('input', {})

        if not s3_path:
            return jsonify({"error": "No S3 path provided"}), 400

        agent_dir = None
        try:
            agent_dir = download_and_extract_agent(s3_path)

            # Create a clean environment for the subprocess
            env = os.environ.copy()
            env['PYTHONPATH'] = agent_dir + os.pathsep + env.get('PYTHONPATH', '')

            # Run the agent in a subprocess
            result = subprocess.run(
                [sys.executable, "-c",
                 "from agent import Agent; import json; "
                 "agent = Agent(); "
                 f"result = agent.execute({json.dumps(agent_input)}); "
                 "print(json.dumps(result))"],
                env=env,
                cwd=agent_dir,
                capture_output=True,
                text=True,
                check=True
            )

            return jsonify(json.loads(result.stdout))

        except subprocess.CalledProcessError as e:
            print("Error executing: ", e)
            return jsonify({"error": f"Agent execution failed: {e.stderr}"}), 500
        except Exception as e:
            print("Error executing: ", e)
            return jsonify({"error": str(e)}), 500
        finally:
            # Clean up
            if agent_dir and os.path.exists(agent_dir):
                shutil.rmtree(agent_dir)
    except Exception as e:
        print("Error in execute_agent: ", e)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)