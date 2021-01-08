FROM python:3.8.2

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
    curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`\
    /chromedriver_linux64.zip

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

# Install all dependencies
RUN apt-get update -y
RUN apt-get install unzip -y
RUN apt-get install vim -y
RUN apt-get install apt-utils -y
RUN apt-get install build-essential libpoppler-cpp-dev pkg-config python-dev -y
RUN pip install --no-cache-dir -r requirements.txt

# Install Chrome for Selenium
# RUN curl https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o /chrome.deb
# RUN dpkg -i /chrome.deb || apt-get install -yf
# RUN rm /chrome.deb

# Install chromedriver for Selenium
# RUN curl https://chromedriver.storage.googleapis.com/2.31/chromedriver_linux64.zip -o /usr/local/bin/chromedriver
# RUN chmod +x /usr/local/bin/chromedriver

# Set env variables
ENV GLUCOSE_PASSWORD French44!
CMD [ "python", "my_selenium.py" ]