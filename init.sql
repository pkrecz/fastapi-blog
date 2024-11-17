SELECT 'CREATE DATABASE fastapi_blog_db' 
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'fastapi_blog_db')\gexec
