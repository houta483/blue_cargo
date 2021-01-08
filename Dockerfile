FROM python:3.8.2
# FROM selenium/standalone-chrome

RUN /usr/local/bin/python -m pip install --upgrade pip

WORKDIR /usr/src/app

COPY . . 
RUN apt-get update -y
RUN apt-get install apt-utils -y
RUN apt-get install build-essential libpoppler-cpp-dev pkg-config python-dev -y
RUN pip install --no-cache-dir -r requirements.txt
ENV GLUCOSE_PASSWORD French44!
CMD [ "python", "my_selenium.py" ]