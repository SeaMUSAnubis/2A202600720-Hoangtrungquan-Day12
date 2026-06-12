FROM nginx:alpine
COPY nginx.conf /nginx.conf.template
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
EXPOSE 80
CMD ["/entrypoint.sh"]
