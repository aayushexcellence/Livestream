FROM python:3.8

WORKDIR /workspace

COPY app /workspace/app

COPY requirements.txt /workspace

RUN pip install -r requirements.txt



ENV FLASK_APP=app
ENV FLASK_ENV=production


RUN apt-get update && \
	apt-get install supervisor -y && \
    apt-get -y autoclean && \
	rm -rf /var/cache/apk/*


COPY ./docker/supervisor/conf.d/stream.conf /etc/supervisor/conf.d/stream.conf

RUN apt-get install -y debconf-utils
ENV TZ=Asia/Kolkata
RUN echo $TZ > /etc/timezone
# RUN rm /etc/localtime
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime
RUN export DEBIAN_FRONTEND=noninteractive
RUN apt-get install -y tzdata
RUN dpkg-reconfigure --frontend noninteractive tzdata
RUN apt-get clean

CMD ["/usr/bin/supervisord"]

