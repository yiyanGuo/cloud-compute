FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates openjdk-17-jre-headless \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /opt/jdbc \
    && curl -fSL "https://repo.maven.apache.org/maven2/org/opengauss/opengauss-jdbc/7.0.0-RC3/opengauss-jdbc-7.0.0-RC3.jar" -o /opt/jdbc/opengauss-jdbc.jar

COPY app ./app
COPY spark ./spark

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
