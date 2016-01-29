FROM centos:centos7

# Need to install the cern repo
USER root
RUN yum -y update

EXPOSE 8080

RUN curl --silent --location https://rpm.nodesource.com/setup_4.x | bash -


RUN yum -y install epel-release && yum clean all

RUN yum -y install python-devel python-pip pytest \
 libffi libffi-devel mariadb-devel \
 pytz python-gunicorn git sudo make gcc gcc-c++ \
 tar curl bzip2 wget python-lxml libxslt-devel unixODBC-devel nodejs && yum clean all

RUN pip install --upgrade pip
RUN pip --version

## Install all the pip requirements
RUN mkdir -p /opt/libs
ENV PYTHONPATH $PYTHONPATH:/opt/libs
RUN pip install setuptools --upgrade --target=/opt/libs

## Install whatever is necessary
COPY ./requirements.txt /opt/app-root/src/requirements.txt
RUN pip install -r /opt/app-root/src/requirements.txt --target=/opt/libs

WORKDIR /opt/app-root/src
COPY ./package.json /opt/app-root/src
RUN npm install


COPY ./app /opt/app-root/src/app
COPY ./tests /opt/app-root/src/tests
COPY ./babel.cfg /opt/app-root/src
COPY ./wsgi.py /opt/app-root/src
