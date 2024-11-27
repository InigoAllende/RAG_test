run-db:
	docker compose up -d db

run-local: run-db
	fastapi dev src/rag_test/main.py

build:
	docker compose build

run:
	docker compose up