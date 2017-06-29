FROM 056684691971.dkr.ecr.us-east-1.amazonaws.com/sps-instantclient:latest

RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y build-essential
RUN apt-get install -y libssl-dev
RUN apt-get install -y libffi-dev
RUN apt-get install -y libpq-dev
RUN apt-get install -y python3-dev
RUN apt-get install -y ssh
RUN apt-get install -y nginx
RUN apt-get install -y supervisor

RUN mkdir -p /opt/sps/api
WORKDIR /opt/sps/api

COPY api ./
COPY api/conf api/
COPY api/data_access api/
COPY api/utils api/

RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.pip

EXPOSE 5050
WORKDIR /opt/sps/api
