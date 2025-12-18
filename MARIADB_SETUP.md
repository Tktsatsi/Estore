# MariaDB Database Setup Guide 🗄️

## Overview

Your eStore is now configured to use **MariaDB** as the database instead of SQLite. This provides better performance, scalability, and is production-ready.

---

## 📋 Prerequisites

### 1. Install MariaDB Server

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install mariadb-server mariadb-client
sudo systemctl start mariadb
sudo systemctl enable mariadb
```

**macOS (using Homebrew):**
```bash
brew install mariadb
brew services start mariadb
```

**Windows:**
- Download from: https://mariadb.org/download/
- Run the installer
- Choose "MariaDB Server" during installation
- Set root password during setup

---

## 🔐 Step 1: Secure MariaDB Installation

Run the security script:
```bash
sudo mysql_secure_installation
```

Answer the prompts:
- Set root password: **YES** (choose a strong password)
- Remove anonymous users: **YES**
- Disallow root login remotely: **YES**
- Remove test database: **YES**
- Reload privilege tables: **YES**

---

## 🗄️ Step 2: Create Database and User

### Login to MariaDB:
```bash
sudo mysql -u root -p
# Enter your root password
```

### Create Database:
```sql
CREATE DATABASE estore_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Create User:
```sql
CREATE USER 'estore_user'@'localhost' IDENTIFIED BY 'your_secure_password';
```

**Important:** Replace `your_secure_password` with a strong password!

### Grant Permissions:
```sql
GRANT ALL PRIVILEGES ON estore_db.* TO 'estore_user'@'localhost';
FLUSH PRIVILEGES;
```

### Verify:
```sql
SHOW DATABASES;
SELECT User, Host FROM mysql.user WHERE User = 'estore_user';
```

### Exit:
```sql
EXIT;
```

---

## 🐍 Step 3: Install Python Dependencies

### Install mysqlclient:
```bash
# On Ubuntu/Debian, install dependencies first:
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential

# On macOS:
brew install mysql-client
export PATH="/usr/local/opt/mysql-client/bin:$PATH"

# Install Python package:
pip install mysqlclient

# Or install all requirements:
pip install -r requirements.txt
```

**Common Issues:**

**Issue:** `mysql_config not found`
- **Ubuntu/Debian:** `sudo apt-get install libmysqlclient-dev`
- **macOS:** `brew install mysql-client` and set PATH

**Issue:** `ld: library not found for -lssl`
- **macOS:** `export LDFLAGS="-L/usr/local/opt/openssl/lib"`

---

## ⚙️ Step 4: Configure Django Settings

The settings are already configured in `eStore/settings.py`:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "estore_db",
        "USER": "estore_user",
        "PASSWORD": "your_password",  # ⚠️ CHANGE THIS
        "HOST": "localhost",
        "PORT": "3306",
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            "charset": "utf8mb4",
        },
    }
}
```

**Update these values:**
1. `NAME`: Your database name (default: `estore_db`)
2. `USER`: Your database user (default: `estore_user`)
3. `PASSWORD`: Your secure password ⚠️
4. `HOST`: Database server (default: `localhost`)
5. `PORT`: Database port (default: `3306`)

---

## 🚀 Step 5: Run Migrations

### Make migrations:
```bash
python manage.py makemigrations
```

### Apply migrations:
```bash
python manage.py migrate
```

You should see output like:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, store, users, cart, orders
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  ...
```

---

## 👤 Step 6: Create Superuser

```bash
python manage.py createsuperuser
```

Enter:
- Username: `admin`
- Email: `admin@estore.com`
- Password: (choose a strong password)

---

## ✅ Step 7: Test Database Connection

### Test in Django shell:
```bash
python manage.py shell
```

```python
from django.db import connection
from django.contrib.auth.models import User

# Test connection
connection.ensure_connection()
print("✅ Database connected!")

# Test query
print(f"Users count: {User.objects.count()}")

# Exit
exit()
```

---

## 🔄 Alternative: Use SQLite for Development

If you want to use SQLite for development/testing, edit `eStore/settings.py`:

**Comment out MariaDB config:**
```python
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.mysql",
#         ...
#     }
# }
```

**Uncomment SQLite config:**
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
```

---

## 📊 Database Management

### Backup Database:
```bash
mysqldump -u estore_user -p estore_db > backup_$(date +%Y%m%d).sql
```

### Restore Database:
```bash
mysql -u estore_user -p estore_db < backup_20241023.sql
```

### View Database:
```bash
mysql -u estore_user -p estore_db
```

```sql
SHOW TABLES;
SELECT * FROM store_store;
SELECT * FROM store_product LIMIT 10;
EXIT;
```

---

## 🔧 Common MariaDB Commands

### Check MariaDB Status:
```bash
sudo systemctl status mariadb
```

### Start/Stop/Restart:
```bash
sudo systemctl start mariadb
sudo systemctl stop mariadb
sudo systemctl restart mariadb
```

### Login as root:
```bash
sudo mysql -u root -p
```

### Change user password:
```sql
ALTER USER 'estore_user'@'localhost' IDENTIFIED BY 'new_password';
FLUSH PRIVILEGES;
```

---

## 🚨 Troubleshooting

### Issue: "Can't connect to MySQL server"
**Solutions:**
1. Check if MariaDB is running: `sudo systemctl status mariadb`
2. Start MariaDB: `sudo systemctl start mariadb`
3. Check HOST in settings.py (should be 'localhost')

### Issue: "Access denied for user"
**Solutions:**
1. Check username/password in settings.py
2. Verify user exists: `sudo mysql -u root -p` → `SELECT User FROM mysql.user;`
3. Grant permissions again (see Step 2)

### Issue: "Unknown database 'estore_db'"
**Solution:**
1. Create database: `sudo mysql -u root -p` → `CREATE DATABASE estore_db;`

### Issue: mysqlclient installation fails
**Ubuntu/Debian:**
```bash
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
pip install mysqlclient
```

**macOS:**
```bash
brew install mysql-client pkg-config
export PKG_CONFIG_PATH="/usr/local/opt/mysql-client/lib/pkgconfig"
pip install mysqlclient
```

### Issue: "Error loading MySQLdb module"
**Solution:**
```bash
pip uninstall mysqlclient
pip install mysqlclient --no-cache-dir
```

---

## 🌐 Production Deployment

### For Production:
1. **Change DEBUG to False** in settings.py
2. **Set ALLOWED_HOSTS** in settings.py
3. **Use environment variables** for sensitive data:

```python
import os

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("DB_NAME", "estore_db"),
        "USER": os.environ.get("DB_USER", "estore_user"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "3306"),
    }
}
```

4. **Set environment variables:**
```bash
export DB_NAME=estore_db
export DB_USER=estore_user
export DB_PASSWORD=your_secure_password
export DB_HOST=localhost
export DB_PORT=3306
```

---

## ✅ Verification Checklist

- [ ] MariaDB installed and running
- [ ] Database `estore_db` created
- [ ] User `estore_user` created with password
- [ ] Permissions granted to user
- [ ] `mysqlclient` package installed
- [ ] Settings.py configured with correct credentials
- [ ] Migrations run successfully
- [ ] Superuser created
- [ ] Can login to admin panel
- [ ] Can create stores/products

---

## 📈 Performance Tips

### 1. Enable Query Caching:
Edit `/etc/mysql/mariadb.conf.d/50-server.cnf`:
```ini
[mysqld]
query_cache_size = 64M
query_cache_type = 1
```

### 2. Optimize for Django:
```ini
max_connections = 200
innodb_buffer_pool_size = 256M
```

### 3. Regular Maintenance:
```bash
# Optimize tables
mysqlcheck -u estore_user -p --optimize estore_db

# Analyze tables
mysqlcheck -u estore_user -p --analyze estore_db
```

---

## 📚 Additional Resources

- **MariaDB Docs:** https://mariadb.com/kb/en/documentation/
- **Django MySQL Docs:** https://docs.djangoproject.com/en/5.0/ref/databases/#mysql-notes
- **mysqlclient:** https://github.com/PyMySQL/mysqlclient

---

## 🎯 Quick Setup Script

Save this as `setup_mariadb.sh`:

```bash
#!/bin/bash

# Install MariaDB (Ubuntu/Debian)
sudo apt update
sudo apt install -y mariadb-server mariadb-client

# Start MariaDB
sudo systemctl start mariadb
sudo systemctl enable mariadb

# Install Python dependencies
sudo apt-get install -y python3-dev default-libmysqlclient-dev build-essential
pip install mysqlclient

echo "✅ MariaDB installed!"
echo "Next steps:"
echo "1. Run: sudo mysql_secure_installation"
echo "2. Create database and user (see guide)"
echo "3. Update settings.py with your credentials"
echo "4. Run migrations: python manage.py migrate"
```

Make it executable:
```bash
chmod +x setup_mariadb.sh
./setup_mariadb.sh
```

---

**Your database setup is complete! 🎉**
