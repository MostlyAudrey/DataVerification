psql -U postgres -c 'DROP DATABASE "DataVerification"';
psql -U postgres -c 'CREATE DATABASE "DataVerification"';

psql -U postgres -d DataVerification -f 'create_data_schema.sql' -1;

psql -U postgres -d DataVerification -f 'create_verification_schema.sql' -1;

psql -U postgres -d DataVerification -f 'load_data.sql' -1;