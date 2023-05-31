docker-build:
	docker build . --tag parasol-locks:0.1.0

docker-run:
	docker run --rm -it --env-file .env parasol-locks:0.1.0
