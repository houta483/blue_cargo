FROM python:3.8.2

# Set root user
USER root

# Adding trusting keys to apt for repositories
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

# Adding Google Chrome to the repositories
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# Updating apt to see and install Google Chrome
RUN apt-get -y update

# Magic happens
RUN apt-get install -y google-chrome-stable

# Installing Unzip
RUN apt-get install -yqq unzip

# Download the Chrome Driver
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`\
    curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE\
    `/chromedriver_linux64.zip

# Unzip the Chrome Driver into /usr/local/bin directory
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/
# Set display port as an environment variable
ENV DISPLAY=:99

RUN /usr/local/bin/python -m pip install --upgrade pip

RUN mkdir -p /usr/local/bin/

# Set the working directory
WORKDIR /usr/src/app

# Copy all files over
COPY . . 

ENV AM_I_IN_A_DOCKER_CONTAINER=True

# Install all dependencies
RUN apt-get update -y
RUN apt-get install unzip -y
RUN apt-get install vim -y
RUN apt-get install apt-utils -y
RUN apt-get install build-essential libpoppler-cpp-dev pkg-config python-dev -y
RUN pip install --no-cache-dir -r requirements.txt

# Set env variables
CMD [ "python", "my_selenium.py" ]