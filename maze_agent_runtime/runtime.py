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

S3_PATH_PREFIX = "s3://maze-social-agent-app/app-zip/"
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
    else:
        # Install dependencies from requirements.txt
        requirements_file = os.path.join(agent_dir, 'requirements.txt')
        if os.path.exists(requirements_file):
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir",  "-r", requirements_file])

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

@app.route('/execute_agent', methods=['POST'])
def execute_agent():
    try:
        data = request.json
        print("Request recieved: ", data)
        s3_file = data.get('s3_path')
        s3_path = S3_PATH_PREFIX + s3_file
        agent_input = data.get('input', {})

        if not s3_path:
            return jsonify({"error": "No S3 path provided"}), 400

        agent_dir = None
        try:
            agent_dir = download_and_extract_agent(s3_path)
            list_directory_contents(agent_dir)
            agent = load_agent(agent_dir)

            if agent is None:
                return jsonify({"error": "Failed to load agent"}), 500

            result = agent.execute(agent_input)
            return jsonify(result)

        except Exception as e:
            return jsonify({"error": str(e)}), 500

        finally:
            # Clean up
            if agent_dir and os.path.exists(agent_dir):
                shutil.rmtree(agent_dir)
    except Exception as e:
        print("Error in processing: ", e)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)