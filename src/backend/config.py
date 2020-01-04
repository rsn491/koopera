import os

ALLOW_CORS = os.getenv('ALLOW_CORS', True)
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '<your_secret_key>')
DATABASE_URI = os.getenv('DATABASE_URI', 'postgres+psycopg2://postgres:password@localhost:5432/koopera')
