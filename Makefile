WORKDIR = $(shell pwd)
NAME = deploy
HOST_PORT = 5050
REMOTE_PORT = 5050
DEPLOY_REMOTE_PORT = 80
IGNORE = $(shell python3 ignore.py)
PY_FILES = $(shell python3 -c "import ignore; print(ignore.get_python_files())")

build:
	docker build -t $(NAME):latest .

build_deploy:
	docker build -f Dockerfile.publish -t $(NAME):latest .

publish:
	docker build -t 056684691971.dkr.ecr.us-east-1.amazonaws.com/deploy-api:$(VERSION) -f Dockerfile.publish .
	docker push 056684691971.dkr.ecr.us-east-1.amazonaws.com/deploy-api:$(VERSION)

run:
	curl -L 'http://169.254.169.254/config/arn:aws:iam::056684691971:role/app/mesos/test/test-deploy-api-role-IAMRole-BTQUIKNIHTXY' -o ~/.aws/deploy-config
	docker run -d \
		-v `ls -d ~/.aws/deploy-config`:/root/.aws/config \
		--rm \
		-p $(HOST_PORT):$(REMOTE_PORT) \
		--name $(NAME) \
		--env "AWS_DEFAULT_REGION=us-east-1" \
		--env "USER=$(USER):YOURPASSWORDGOESHERE" \
		--env "ENVIRONMENT=test" \
		--env "MODE=test" \
		$(NAME):latest python3 run.py

run_deploy:
	docker run -d \
		-p $(HOST_PORT):$(DEPLOY_REMOTE_PORT) \
		--name $(NAME) \
		--env "AWS_DEFAULT_REGION=us-east-1" \
		--env "USER=$(USER):YOURPASSWORDGOESHERE" \
		--env "ENVIRONMENT=test" \
		--env "MODE=prod" \
		$(NAME):latest

run_watch:
	docker exec -it $(NAME) make watch

ssh:
	docker exec -it $(NAME) /bin/bash

repl:
	docker exec -it $(NAME) ipython

tail:
	docker logs -f $(NAME)

watch:
	ptw --runner "pytest $(IGNORE)"

clean:
	docker stop $(NAME)
	docker rm $(NAME)
