FROM ubuntu:14.04
RUN apt-get -y update
RUN sudo apt-get -y install python-dev python-pip build-essential python-distribute git nginx libpq-dev
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
COPY ./config/nginx /etc/nginx/sites-enabled/capuchin.conf
RUN sudo service nginx reload
