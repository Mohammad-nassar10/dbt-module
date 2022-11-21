FROM python:3.8-slim

# ENV USER_UID=1001 \
#     USER_NAME=dbt-module

# COPY  build/bin /usr/local/bin
# RUN  /usr/local/bin/user_setup

COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /app
COPY dbt/module.py module.py
COPY dbt/utils.py utils.py
COPY dbt dbt
COPY sample-conf.yaml sample-conf.yaml

# ENTRYPOINT ["python3"]
# CMD ["module.py"]

ENTRYPOINT ["tail", "-f", "/dev/null"]

# USER ${USER_UID}