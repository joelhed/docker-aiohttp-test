.PHONY: build run

build:
	docker build -t docker-test .

run:
	docker run -dp 81:8080 -v polls-db:/etc/polls -e PYTHONUNBUFFERED=1 docker-test