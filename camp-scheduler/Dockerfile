# Use an official Nginx image to serve static files
FROM nginx:alpine
COPY ./dist /usr/share/nginx/html
RUN sed -i 's/listen       80;/listen       8080;/' /etc/nginx/conf.d/default.conf
EXPOSE 8080 