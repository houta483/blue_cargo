aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 286380851113.dkr.ecr.us-west-2.amazonaws.com

docker build -t houghton_glucose .

docker tag houghton_glucose:latest 286380851113.dkr.ecr.us-west-2.amazonaws.com/houghton_glucose:latest

docker push 286380851113.dkr.ecr.us-west-2.amazonaws.com/houghton_glucose:latest