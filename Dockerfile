# Use official Python base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install uv and system deps
RUN pip install --upgrade pip && pip install uv

# Copy project files
COPY . .

# Install dependencies using uv
RUN uv pip install -r requirements.txt

# Expose FastAPI port
EXPOSE 8000

# Expose localhost
ENV HOST 0.0.0.0

# Run the app using uvicorn via uv
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
