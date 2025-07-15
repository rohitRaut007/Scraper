UPDATE products
SET sizes_available = REGEXP_REPLACE(sizes_available, E'\\nRs\\.\\s?[0-9]+', '', 'g');
