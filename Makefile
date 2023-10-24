.PHONY: format_and_isort docker

format:
	black . && isort . --profile black

docker:
	docker-compose up -d --build
