FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
RUN pip install --no-cache-dir "fastapi>=0.110,<1" "uvicorn>=0.29,<1" "pydantic>=2,<3"
COPY . .
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health',timeout=3)"
CMD ["uvicorn", "agents.api:app", "--host", "0.0.0.0", "--port", "8000"]
