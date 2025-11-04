db = db.getSiblingDB('admin');

// Create admin user if it doesn't exist
db.createUser({
  user: "zibal",
  pwd: "zibal",
  roles: [
    { role: "userAdminAnyDatabase", db: "admin" },
    { role: "readWriteAnyDatabase", db: "admin" },
    { role: "dbAdminAnyDatabase", db: "admin" }
  ]
});

// Switch to the application database
db = db.getSiblingDB('zibal');

// Create collections and additional setup if needed
db.createCollection('transactions');
db.createCollection('users');

// Create application-specific user with readWrite access to the zibal database
db.createUser({
  user: "zibal",
  pwd: "zibal",
  roles: [
    { role: "readWrite", db: "zibal" },
    { role: "dbAdmin", db: "zibal" }
  ]
});

print("MongoDB initialization completed successfully!");
