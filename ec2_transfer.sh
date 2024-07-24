#bash ec2_transfer.sh

scp -r -i  ~/.ssh/maze-public-ec2.pem /Users/vishnumurthyprabhu/0-1/maze/maze-code/backend/maze-agent-flask/maze_agent_runtime/  ubuntu@13.229.69.52:/home/ubuntu/maze-agent-flask/