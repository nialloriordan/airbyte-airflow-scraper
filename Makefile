.DEFAULT_GOAL := help
help:
	@egrep -h '\s#\s' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?# "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build-airflow-image: # build the airflow image
	docker build -f Dockerfile -t docker_airflow .
start-airflow-airbyte-stack: # start airflow and airbyte localy
	docker-compose -f docker-compose.airflow.yaml \
		-f docker-compose.airbyte.yaml up
restart-airflow-airbyte-stack: # restart airflow and airbyte locally
	docker-compose -f docker-compose.airflow.yaml \
		-f docker-compose.airbyte.yaml down && \
	docker-compose -f docker-compose.airflow.yaml \
		-f docker-compose.airbyte.yaml up
