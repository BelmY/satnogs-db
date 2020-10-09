FROM python:3.8.6
MAINTAINER SatNOGS project <dev@satnogs.org>

WORKDIR /workdir/

RUN groupadd -r satnogs \
	&& useradd -r -g satnogs satnogs \
	&& install -d -m 755 -o satnogs -g satnogs /var/run/celery

COPY requirements.txt /usr/local/src/satnogs-db/
RUN pip install \
	--no-cache-dir \
	--no-deps \
	--force-reinstall \
	-r /usr/local/src/satnogs-db/requirements.txt

COPY . /usr/local/src/satnogs-db/
RUN pip install \
	--no-cache-dir \
	--no-deps \
	--force-reinstall \
	/usr/local/src/satnogs-db
RUN install -m 755 /usr/local/src/satnogs-db/bin/djangoctl.sh /usr/local/bin/

RUN rm -rf /usr/local/src/satnogs-db

ENV DJANGO_SETTINGS_MODULE db.settings

EXPOSE 8000
