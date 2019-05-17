#!/bin/sh
## startup script
cp /etc/nginx/conf.d/ssm.conf.new /etc/nginx/conf.d/ssm.conf ## if new conf passed at runtime, use it
cd /npm_build;
cp .env.docker.new .env.docker;  # if react env file passed in at runtime, use that
npm run build:docker;
cp -a build/. /var/www/html/react/;
cp -a /var/www/html/react/static/. /var/www/html/react/;
rm -rf /var/www/html/react/static;
cp -a /var/www/html/react/. /var/www/html/static/;
nginx -g 'daemon off;';
exec "$@"