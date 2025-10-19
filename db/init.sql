-- TypeFlow Database Initialization Script

-- Create database (if running this manually)
-- CREATE DATABASE typeflow;
-- \c typeflow;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create indexes for better performance
-- These will be created by Alembic migrations in production

-- Sample data can be loaded via scripts/seed_data.py