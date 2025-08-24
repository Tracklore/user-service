FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY user-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared libraries
COPY shared_libs /app/shared_libs

# Install shared libraries
RUN pip install --no-cache-dir /app/shared_libs

# Copy the application
COPY user-service/ .

# Expose the port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]