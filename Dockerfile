FROM python:slim

LABEL maintainer="klaas.nebuhr@gmail.com"

WORKDIR /digicubes

RUN apt-get update \
&& apt-get install apt-utils -y \
&& apt-get install gcc -y \
&& apt-get clean

RUN mkdir -p data

RUN pip install --no-cache-dir wheel
RUN pip install --upgrade pip
RUN pip install --no-cache-dir digicubes-flask
COPY wsgi.py .

#RUN pip install digicubes-server


EXPOSE 5000/tcp

VOLUME /digicubes/data

ENV DIGICUBES_SECRET b3j6casjk7d8szeuwz00hdhuw4ohwDu9o
ENV FLASK_ENV production
ENV FLASK_APP digicubes_flask.web
ENV DC_SMTP_HOST=None


#CMD ["python", "docker.py"]

CMD ["gunicorn", "-b 0.0.0.0:5000", "wsgi:app"]