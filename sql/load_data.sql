
\COPY public.tb_city FROM '../Mock_DB/Cities.csv' WITH CSV HEADER DELIMITER ',';

\COPY public.tb_client FROM '../Mock_DB/Clients.csv' WITH CSV HEADER DELIMITER ',';

\COPY public.tb_product FROM '../Mock_DB/Products.csv' WITH CSV HEADER DELIMITER ',';

\COPY public.tb_order FROM '../Mock_DB/Orders.csv' WITH CSV HEADER DELIMITER ',';

\COPY public.tb_line_item FROM '../Mock_DB/LineItems.csv' WITH CSV HEADER DELIMITER ',';