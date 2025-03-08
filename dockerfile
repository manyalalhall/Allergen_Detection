# Use an official Python runtime as base image
FROM python:3.10

WORKDIR /app

# Copy files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port FastAPI runs on
EXPOSE 8000

# Run the API
CMD ["uvicorn", "electrothon:app", "--host", "0.0.0.0", "--port", "8000"]


