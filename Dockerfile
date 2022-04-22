FROM apache/airflow:2.2.5

ARG AIRFLOW_USER_HOME=/opt/airflow

ENV PYTHONPATH=$PYTHONPATH:${AIRFLOW_USER_HOME}

USER airflow

RUN pip install --upgrade pip && \
    pip install selenium && \
    pip install bs4 && \
    pip install apache-airflow-providers-airbyte

RUN mkdir ${AIRFLOW_USER_HOME}/outputs
