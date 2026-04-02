FROM python:3.12-slim-bookworm

# working directory
WORKDIR /code

# Copy the requirements file and install Python dependencies
COPY ./requirements-linux.txt /code/requirements-linux.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements-linux.txt

# Copy the rest of the application code
COPY . /code

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

