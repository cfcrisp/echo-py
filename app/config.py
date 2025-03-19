# app/config.py
import os
from datetime import timedelta

class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers', 'cookies']  # Allow tokens in headers and cookies
    JWT_ACCESS_COOKIE_NAME = 'access_token'      # Name of the cookie
    JWT_COOKIE_SECURE = True                     # Use True in production with HTTPS
    JWT_COOKIE_SAMESITE = 'Lax'                  # Prevents CSRF in most cases
    JWT_COOKIE_CSRF_PROTECT = False              # Disable CSRF for simplicity (enable if needed)
    
    # Application
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload

class DevelopmentConfig(Config):
    DEBUG = True
    JWT_COOKIE_SECURE = False  # Allow non-HTTPS in development

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
    # Make sure these are set in environment variables in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')