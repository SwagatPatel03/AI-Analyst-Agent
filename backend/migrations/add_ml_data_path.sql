-- Migration: Add ml_data_path to reports table
-- Date: 2025-10-22
-- Purpose: Store path to ML-ready JSON file for predictions

-- Add the new column
ALTER TABLE reports ADD COLUMN ml_data_path VARCHAR;

-- Add comment
COMMENT ON COLUMN reports.ml_data_path IS 'Path to ML-ready JSON file optimized for predictions';
