import os
from datetime import timedelta

# Get the base directory
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration"""
    # Secret key for JWT and sessions
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration - FIXED with absolute path
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'productivity_pet.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    JWT_COOKIE_CSRF_PROTECT = False
    
    # Pet Health Decay Schedule (in hours)
    HEALTH_DECAY_INTERVAL = 6
    
    # Gamification Settings
    POINTS_LOW_PRIORITY = 5
    POINTS_MEDIUM_PRIORITY = 10
    POINTS_HIGH_PRIORITY = 20
    
    # Level Thresholds
    LEVEL_THRESHOLDS = {
        1: 0,
        2: 100,
        3: 250,
        4: 500,
        5: 1000,
        6: 2000,
        7: 3500,
        8: 5500,
        9: 8000,
        10: 11000
    }
    
    # Pet Evolution Stages
    EVOLUTION_REQUIREMENTS = {
        1: 0,      # Egg
        2: 100,    # Baby
        3: 500,    # Teen
        4: 1500,   # Adult
        5: 3500    # Elder/Legendary
    }
    
    # Pet Stats Configuration
    MAX_HEALTH = 100
    MAX_HAPPINESS = 100
    MAX_HUNGER = 100
    
    HEALTH_INCREASE_ON_TASK = 15
    HAPPINESS_INCREASE_ON_TASK = 10
    HEALTH_DECREASE_ON_OVERDUE = 10
    HAPPINESS_DECREASE_ON_OVERDUE = 5
    
    FEED_COST = 5  # Points needed to feed pet
    HUNGER_DECREASE_ON_FEED = 30

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test_productivity_pet.db')
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}