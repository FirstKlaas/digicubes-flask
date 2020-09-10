FROM python:slim

LABEL maintainer="klaas.nebuhr@gmail.com"

WORKDIR /digicubes

RUN apt-get update \
&& apt-get install apt-utils -y \
&& apt-get install gcc -y \
&& apt-get install -y --no-install-recommends git \
&& apt-get clean

RUN mkdir -p data
RUN mkdir -p logs

RUN python -m pip install --no-cache-dir wheel
RUN python -m pip install --upgrade pip

COPY requirements.txt .

RUN mkdir -p digicubes_flask
COPY digicubes_flask/ digicubes_flask/
#RUN python -m pip install --no-cache-dir --upgrade --force-reinstall git+https://github.com/FirstKlaas/digicubes-flask
COPY wsgi.py .
COPY loop.py .

RUN pip install -r requirements.txt

#RUN pip install digicubes-server

EXPOSE 5000/tcp

VOLUME /digicubes/data

ENV DIGICUBES_SECRET b3j6casjk7d8szeuwz00hdhuw4ohwDu9o

CMD ["gunicorn", "-b 0.0.0.0:5000", "--worker-tmp-dir=/dev/shm", "--workers=2", "--threads=4", "--worker-class=gthread", "wsgi:app"]
# Generated at 2020-09-10 16:30:25.208974