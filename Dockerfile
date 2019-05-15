FROM python:3.7
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
RUN apt update && apt dist-upgrade -y
RUN apt install build-essential python-all-dev libboost-python-dev libpq-dev -y
RUN mkdir /repo
RUN mkdir /src
RUN mkdir /config
RUN mkdir /var/log/gunicorn
RUN git clone https://github.com/Aninstance/simple-stock-management /repo
ADD config /repo/config
RUN cp -a /repo/src/. /src
RUN cp -a /repo/config/. /config
RUN rm -rf /repo
RUN pip install -r /config/requirements.txt
RUN groupadd -r -g 9001 ssm && useradd --no-log-init -r -g 9001 -u 9001 ssm
RUN chown -R ssm /src /config /var/log
USER ssm
RUN cp /config/settings.docker.py /src/StockManagement/settings.py
WORKDIR /src
EXPOSE 8000
ENTRYPOINT [ "/config/entrypoint-dev-server.sh" ]