
\COPY public.tb_city FROM '../Mock_DB/Cities.csv' WITH CSV HEADER DELIMITER ',';

\COPY public.tb_client FROM '../Mock_DB/Clients.csv' WITH CSV HEADER DELIMITER ',';

\COPY public.tb_product FROM '../Mock_DB/Products.csv' WITH CSV HEADER DELIMITER ',';

\COPY public.tb_order FROM '../Mock_DB/Orders.csv' WITH CSV HEADER DELIMITER ',';

\COPY public.tb_line_item FROM '../Mock_DB/LineItems.csv' WITH CSV HEADER DELIMITER ',';

CREATE TABLE temp_table (
    left_child          INTEGER NOT NULL,
    left_child_hash     VARCHAR NOT NULL,
    right_child         INTEGER,
    right_child_hash    VARCHAR,
    num_leaf_nodes	    INTEGER,
    are_children_leaves BOOlEAN NOT NULL DEFAULT FALSE
);

\COPY temp_table FROM '../Mock_DB/InnerNodes.csv' WITH CSV HEADER DELIMITER ',' NULL 'None';

INSERT INTO verification.tb_inner_node(left_child, left_child_hash, right_child, right_child_hash, are_children_leaves)
SELECT left_child, left_child_hash, right_child, right_child_hash, are_children_leaves  FROM temp_table;

DROP TABLE temp_table;

CREATE TABLE temp_table (
    table_name          VARCHAR NOT NULL,
    primary_key_value   INTEGER NOT NULL,
    data_hash           VARCHAR NOT NULL
);


\COPY temp_table FROM '../Mock_DB/LeafNodes.csv' WITH CSV HEADER DELIMITER ',';

INSERT INTO verification.tb_leaf_node(table_name, primary_key_value, data_hash)
SELECT table_name, primary_key_value, data_hash FROM temp_table;

DROP TABLE temp_table;

CREATE TABLE temp_table (
    primary_key_value     INTEGER NOT NULL,
    root_inner_node       INTEGER NOT NULL REFERENCES verification.tb_inner_node
);

\COPY temp_table FROM '../Mock_DB/order_root_node.csv' WITH CSV HEADER DELIMITER ',';

INSERT INTO verification.tb_relation_inner_node(relation_id, primary_key_value, root_inner_node)
SELECT 1, primary_key_value, root_inner_node FROM temp_table;
