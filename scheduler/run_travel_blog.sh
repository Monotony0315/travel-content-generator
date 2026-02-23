#!/bin/bash
# Travel Blog Auto-Generator Cron Script
# Uses Pexels + Pixabay only (Unsplash disabled)

export PEXELS_API_KEY="ioGXDRNtGkKS4xnh96owdsVasgdCuQdLs8GRjCgd6Beb0UPyp9z6igtW"
export PIXABAY_API_KEY="54702280-34b6357830834f9bd1e0d1ed3"
# Unsplash is disabled - using Pexels + Pixabay only
export UNSPLASH_ACCESS_KEY=""

cd ~/Development/projects/travel-content-generator

# Log file
LOG_FILE="logs/cron_$(date +%Y%m%d_%H%M%S).log"
mkdir -p logs

# Run blog generation
echo "[$(date)] Starting travel blog generation..." >> "$LOG_FILE"
python3 generate_daily_blog.py >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "[$(date)] Blog generated successfully" >> "$LOG_FILE"
else
    echo "[$(date)] Blog generation failed" >> "$LOG_FILE"
fi
