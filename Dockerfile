FROM centos:7
RUN yum makecache
RUN yum -y install epel-release
RUN yum -y install python python-pip python-devel git gcc libjpeg-turbo-devel \
                   libxml2-devel libxslt-devel mysql-devel mysql npm
RUN yum -y clean all
RUN npm install -g bower gulp-cli
RUN pip install --upgrade pip

COPY ./requirements/ /tmp/requirements/
RUN pip install --no-cache-dir --require-hashes --no-deps -r /tmp/requirements/dev.txt

WORKDIR /app
COPY . /app

EXPOSE 80

CMD ["./docker/run-docker.sh"]
