FROM nginx:stable

COPY ./nginx.conf /etc/nginx/conf.d/default.conf
COPY ./source/ /var/www

CMD ["nginx", "-g", "daemon off;"]
