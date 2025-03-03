# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HOST 0.0.0.0

# Set the working directory
WORKDIR /app

# Install build tools
RUN apt-get update && apt-get install -y build-essential

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy the Poetry files
COPY pyproject.toml poetry.lock /app/

# Install dependencies
RUN poetry install --no-root --no-interaction --no-ansi

# Copy the application code
COPY . /app/

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["poetry", "run", "python", "llm_translator/manage.py", "runserver", "0.0.0.0:8000"]