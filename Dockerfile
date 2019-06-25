FROM nginx:latest
RUN rm /etc/nginx/conf.d/default.conf
RUN mkdir -p /var/www/html/media
RUN mkdir /var/www/html/static
RUN mkdir /var/www/html/react
RUN mkdir /npm_build
RUN apt update && apt dist-upgrade -y
RUN apt install curl git -y
RUN curl -sL https://deb.nodesource.com/setup_9.x | bash -
RUN git clone --single-branch --branch frontend https://github.com/Aninstance/simple-stock-management /npm_build
COPY public /npm_build
WORKDIR  /npm_build
RUN apt install npm -y
RUN npm i npm@latest -g
RUN npm install --save
COPY ssm.conf /etc/nginx/conf.d/
COPY nginx.conf /etc/nginx/
COPY nginx-entrypoint.sh /
WORKDIR /
RUN groupadd -r -g 9001 ssm && useradd --no-log-init -r -g 9001 -u 9001 ssm
#EXPOSE 80
ENTRYPOINT [ "/nginx-entrypoint.sh" ]