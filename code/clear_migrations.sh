#!/bin/bash

# List of internal apps
internal_apps=(
    'martyr' 'gallery' 'contact_us' 
)

echo "Starting migration files deletion..."
echo "=========================================="

# Loop through each app and delete migration files
for app in "${internal_apps[@]}"
do
    echo "Deleting migration files for: $app"
    
    # Delete .py files (except __init__.py)
    find . -path "*/$app/migrations/*.py" -not -name "__init__.py" -delete
    
    # Delete .pyc files
    find . -path "*/$app/migrations/*.pyc" -delete
    
    echo "✓ Migration files deleted for: $app"
    echo "------------------------------------------"
done

echo "=========================================="
echo "Migration files deletion completed!"
echo "Total apps processed: ${#internal_apps[@]}"