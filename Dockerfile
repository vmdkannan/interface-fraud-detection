# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Use a Docker RUN instruction to securely handle secrets during the build process.
# The --mount flag mounts a secret file (POSTGRES_URL)
# Write the contents of the POSTGRES_URL secret to a temporary file for further processing.
# Append the AIRFLOW__DATABASE__SQL_ALCHEMY_CONN environment variable to the system-wide environment file.
RUN --mount=type=secret,id=POSTGRES_URL,mode=0444 \
    cat /run/secrets/POSTGRES_URL > /tmp/POSTGRES_URL && \
    echo "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=$(cat /tmp/POSTGRES_URL)" >> /etc/environment


# Run app.py when the container launches
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app"]
