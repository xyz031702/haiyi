FROM python:3.6-alpine

ENV PYTHONUNBUFFERED 1

RUN apk update \
	# psycopg2 dependencies
	&& apk add --virtual build-deps gcc python3-dev musl-dev \
	&& apk add postgresql-dev \
	# Pillow dependencies
	&& apk add jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev \
	# CFFI dependencies
	&& apk add libffi-dev py-cffi \
	# Weasyprint dependencies
	&& apk add cairo-dev pango-dev \
	&& apk add curl vim
#
#RUN mkdir -p /usr/share/fonts/truetype/serif
#COPY ./scantist/static/fonts/SourceHanSerifSC-Regular.otf /usr/share/fonts/truetype/serif
#RUN chmod 644 /usr/share/fonts/truetype/serif/*
#
## Rebuild the font cache.
#RUN fc-cache -fv

#RUN addgroup -S django \
#    && adduser -S -G django django

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./requirements /requirements
RUN pip install --no-cache-dir -r /requirements/local.txt \
    && rm -rf /requirements


COPY ./compose/local/django/gunicorn.sh /gunicorn.sh
RUN sed -i 's/\r//' /gunicorn.sh
RUN chmod +x /gunicorn.sh
#RUN chown django /gunicorn.sh

#COPY ./compose/local/django/entrypoint.sh /entrypoint.sh
#RUN sed -i 's/\r//' /entrypoint.sh
#RUN chmod +x /entrypoint.sh
##RUN chown django /entrypoint.sh

WORKDIR /app
#COPY . /app
#RUN chown -R django /app
#USER django


#ENTRYPOINT ["/entrypoint.sh"]
