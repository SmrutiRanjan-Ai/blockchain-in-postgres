\echo Use "CREATE EXTENSION blockchain" to load this file. \quit
CREATE FUNCTION init_blockchain(_tbl regclass)
RETURNS VOID
LANGUAGE plpgsql 
  AS $$
    BEGIN
    EXECUTE 'CREATE TABLE IF NOT EXISTS block (ID INT NOT NULL, Hasher (65) NOT NULL, PRIMARY KEY (ID));'
    END;
  $$;
  
