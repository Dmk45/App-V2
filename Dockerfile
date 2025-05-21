# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.12-slim

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

COPY milk2-32695-92bfb749ee38.json .
ENV GOOGLE_APPLICATION_CREDENTIALS="milk2-32695-92bfb749ee38.json"
ENV OPENAI_API_KEY="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"
# Replace the `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` values
# with appropriate values for your project.
ENV GOOGLE_CLOUD_PROJECT=milk2-32695
ENV GOOGLE_CLOUD_LOCATION=us-central1
ENV GOOGLE_GENAI_USE_VERTEXAI=True


COPY requirements.txt .
RUN python -m pip install -r requirements.txt
RUN pip3 install --upgrade "google-cloud-aiplatform>=1.64"

WORKDIR /app



COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker", "new:app"]
