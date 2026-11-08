FROM python:3.14-slim

WORKDIR /app
COPY requirements.txt requirements_dev.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt -r requirements_dev.txt

CMD ["bash"]
