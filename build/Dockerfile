FROM python:3.8-slim



COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /app
COPY dbt dbt

WORKDIR "/app/dbt"


ENTRYPOINT ["python3"]
CMD ["module.py"]
