# Use selenium's standalone Chrome image
FROM selenium/standalone-chrome:latest

# Set up the working directory
WORKDIR /app

# Install Python and Selenium library
USER root
RUN apt-get update && apt-get install -y python3 python3-pip

# Install the required Python packages
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Switch back to the selenium user to run the application
USER seluser

# Copy the Python script into the container
ADD . .

CMD ["python3", "app.py"]
