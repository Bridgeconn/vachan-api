FROM nginx:1.17-alpine

RUN rm /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/
RUN rm /etc/nginx/conf.d/default.conf
COPY vachan.conf /etc/nginx/conf.d/