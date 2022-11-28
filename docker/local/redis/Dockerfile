ARG REDIS_VERSION=5

FROM redis:${REDIS_VERSION}-alpine as app_redis

WORKDIR /app/redis

COPY docker/local/redis/redis.conf /usr/local/etc/redis/redis.conf
RUN mkdir -p /app/redis/log \
#    && chown redis:redis /app/redis/log \
    && mkdir -p /app/redis/dump \
#    && chown redis:redis /app/redis/dump \
    && > /app/redis/log/redis.log

CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]