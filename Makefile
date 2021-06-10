.PHONY: build run run-detached test

build:
	docker build -t docker-test .

test:
	docker run --rm docker-test python -m pytest tests/

run-detached:
	docker run -dp 81:8080 -v polls-db:/etc/polls -e PYTHONUNBUFFERED=1 docker-test

run:
	docker run --rm -p 81:8080 -v polls-db:/etc/polls -e PYTHONUNBUFFERED=1 docker-test
