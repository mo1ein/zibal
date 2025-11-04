############### Builder stage

FROM python:3.14-alpine AS builder

RUN pip install uv

WORKDIR /app

COPY requirements.txt ./

RUN uv pip install --system --no-cache -r requirements.txt

COPY . .


############### Runtime stage
FROM python:3.14-alpine AS runtime

RUN apk add --no-cache \
    bash \
    curl \
    libstdc++ \
    && rm -rf /var/cache/apk/*

RUN addgroup -S app && adduser -S app -G app

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.14/site-packages/ /usr/local/lib/python3.14/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

COPY --from=builder /app/ /app/

RUN chown -R app:app /app

USER app

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Copy entrypoint script and make executable
COPY --chown=app:app entrypoint.sh /app/

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]