#!/bin/bash
set -e

echo "=== MongoDB Restore Configuration ==="
echo "Host: ${MONGO_DB_HOST}"
echo "Port: ${MONGO_DB_PORT}"
echo "Database: ${MONGO_DB_NAME}"
echo "Username: ${MONGO_DB_USERNAME}"
echo "Auth Source: ${MONGO_AUTH_SOURCE}"

# Construct MongoDB URI from environment variables
MONGO_URI=${MONGO_URI}

echo "Waiting for MongoDB to be ready..."
until mongosh --eval 'db.runCommand("ping").ok' "${MONGO_URI}" > /dev/null 2>&1; do
    echo "Waiting for MongoDB..."
    sleep 2
done

echo "MongoDB is ready. Starting restore..."
mongorestore --uri="${MONGO_URI}" --archive=/data/transaction.bin --drop

echo "✅ MongoDB restore completed successfully!"

echo "Restored collections:"
mongosh "${MONGO_URI}" --eval "db.getCollectionNames()"