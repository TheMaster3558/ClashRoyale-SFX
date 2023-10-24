.PHONY: format_and_isort docker

format:
	black . && isort . --profile black

docker:
	docker build . --tag ghcr.io/themaster3558/clashroyaleaudio:latest
