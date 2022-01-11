# Use an official Python runtime as a parent image
FROM arm32v7/python:3.10.1-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN apt-get update \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --trusted-host pypi.python.org -r requirements.txt \
    && apt-get purge -y --auto-remove

# Build sertificate

# Make port 81 available to the world outside this container
#EXPOSE 81

# Define environment variable
#ENV ENV_NAME env_value

# Run app.py when the container launches
CMD ["python", "src/app.py"]