FROM python:2
MAINTAINER SatNOGS project <dev@satnogs.org>

WORKDIR /workdir/

COPY requirements.txt /usr/local/src/satnogs-db/
RUN pip install \
	--no-cache-dir \
	--no-deps \
	--ignore-installed \
	-r /usr/local/src/satnogs-db/requirements.txt

COPY . /usr/local/src/satnogs-db/
RUN pip install \
	--no-cache-dir \
	--no-deps \
	--ignore-installed \
	/usr/local/src/satnogs-db

RUN rm -rf /usr/local/src/satnogs-db

COPY bin/djangoctl.sh /usr/local/bin/

ENV DJANGO_SETTINGS_MODULE db.settings

EXPOSE 8000
