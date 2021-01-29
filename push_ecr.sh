aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 286380851113.dkr.ecr.us-west-2.amazonaws.com
docker build -t houta483/glucose .
docker tag houta483/glucose:latest 286380851113.dkr.ecr.us-west-2.amazonaws.com/houta483/glucose:latest
docker push 286380851113.dkr.ecr.us-west-2.amazonaws.com/houta483/glucose:latest