FROM openshift/base-centos7

# Need to install the cern repo
USER root
RUN yum -y update

EXPOSE 8080

ENV PYTHON_VERSION=2.7 \
    PATH=$HOME/.local/bin/:$PATH

LABEL io.k8s.description="Platform for building and running Python 2.7 applications" \
      io.k8s.display-name="Python 2.7" \
      io.openshift.expose-services="8080:http" \
      io.openshift.tags="builder,python,python27,rh-python27"

RUN yum install -y centos-release-scl epel-release && \
    INSTALL_PKGS="\
     libffi \
     libffi-devel \
     python-devel python-setuptools python-pip \
     pytz \
     make \
     gcc \
     gcc-c++ \
     tar \
     curl \
     python-lxml \
     libxslt-devel \
     unixODBC-devel \
     mariadb-devel \
     httpd httpd-devel" && \
    yum install -y $INSTALL_PKGS && \
    yum clean all -y

RUN curl --silent --location https://rpm.nodesource.com/setup_4.x | bash -
RUN yum -y install nodejs

## Install all the pip requirements
RUN mkdir -p /opt/libs
RUN pip install setuptools --upgrade --target=/opt/libs
ENV PYTHONPATH $PYTHONPATH:/opt/libs


USER default

COPY ./base-requirements.txt /opt/app-root/base-requirements.txt
RUN pip install --user -r /opt/app-root/base-requirements.txt

COPY ./base-package.json /opt/app-root/src/package.json
RUN npm install

RUN rm /opt/app-root/src/package.json
RUN rm /opt/app-root/base-requirements.txt

USER root

# Copy the S2I scripts from the specific language image to $STI_SCRIPTS_PATH.
COPY ./bin/ $STI_SCRIPTS_PATH
RUN chmod +x $STI_SCRIPTS_PATH/assemble $STI_SCRIPTS_PATH/run $STI_SCRIPTS_PATH/usage

# Each language image can have 'contrib' a directory with extra files needed to
# run and build the applications.
COPY ./contrib/ /opt/app-root

# In order to drop the root user, we have to make some directories world
# writable as OpenShift default security model is to run the container under
# random UID.
RUN chown -R 1001:0 /opt/app-root && chmod -R ug+rwx /opt/app-root

USER 1001

# Set the default CMD to print the usage of the language image.
CMD $STI_SCRIPTS_PATH/usage

