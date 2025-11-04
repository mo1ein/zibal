#!/bin/bash
set -e

# Wait for MongoDB to be ready
echo "Waiting for MongoDB at $MONGO_DB_HOST:$MONGO_DB_PORT..."
while ! nc -z $MONGO_DB_HOST $MONGO_DB_PORT; do
  sleep 1
done
echo "MongoDB is ready!"

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Precompute summaries
echo "Precomputing summaries..."
python manage.py precompute_summaries

echo "All setup tasks completed!"
exec "$@"