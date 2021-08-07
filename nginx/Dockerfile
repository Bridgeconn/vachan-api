FROM nginx

LABEL maintainer="Uday Kumar <uday.kumar@bridgeconn.com>"

COPY ./www/ /var/www
COPY ./default.conf /etc/nginx/conf.d/default.conf

RUN ln -sf /dev/stdout /var/log/nginx/access.log \
	&& ln -sf /dev/stderr /var/log/nginx/error.log

EXPOSE 80
EXPOSE 443 