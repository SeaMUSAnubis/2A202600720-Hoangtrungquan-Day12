FROM nginx:alpine
COPY nginx.conf /nginx.conf.template
EXPOSE 80
CMD sh -c "envsubst '\\$BACKEND_HOST \\$FRONTEND_HOST' < /nginx.conf.template > /etc/nginx/nginx.conf && nginx -g 'daemon off;'"
