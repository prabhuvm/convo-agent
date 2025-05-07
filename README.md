Steps to create and host the agents repo:
=====================================
To create an agent with a packed venv:
Create a new directory for your agent
Set up a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

Install your dependencies:
pip install your-dependencies

Create your agent.py file
Zip the entire directory, including the venv folder:
zip -r agent.zip agent.py venv



- Create zip by selecting all files, not the folder.



Sample Request for chatGPT-agent:
==============================
curl http://127.0.0.1:5000/execute_agent \
-H "Content-Type: application/json" \
-X POST \
-d '{
"s3_path": "nnrbvvgL/nnrbvvgL_rPT59QMe.zip",
"input": {
"text": "Hey there! What'\''s up? I'\''ve got some awesome news to share with you guys.",
"style": "formal business email"
}
}'