#!/bin/bash


sudo docker exec -t atre_shohada_db pg_dump \
  -U atre_shohada_user \
  -d atre_shohada_db \
  --no-owner \
  --no-privileges \
  --format=plain \
  > backup.sql