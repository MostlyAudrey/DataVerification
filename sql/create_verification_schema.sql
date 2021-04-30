CREATE SCHEMA IF NOT EXISTS verification;

CREATE SEQUENCE IF NOT EXISTS verification.sq_inner_node;
CREATE TABLE    IF NOT EXISTS verification.tb_inner_node (
    inner_node_id       INTEGER PRIMARY KEY DEFAULT nextval( 'verification.sq_inner_node' ),
    left_child          INTEGER NOT NULL,
    left_child_hash     CHAR(64) NOT NULL,
    right_child         INTEGER,
    right_child_hash    CHAR(64),
    are_children_leaves BOOlEAN NOT NULL DEFAULT FALSE
);

CREATE SEQUENCE IF NOT EXISTS verification.sq_leaf_node;
CREATE TABLE    IF NOT EXISTS verification.tb_leaf_node (
    leaf_node_id        INTEGER PRIMARY KEY DEFAULT nextval( 'verification.sq_leaf_node' ),
    table_name          VARCHAR NOT NULL,
    primary_key_value   INTEGER NOT NULL,
    data_hash           CHAR(64) NOT NULL
);

CREATE SEQUENCE IF NOT EXISTS verification.sq_relation;
CREATE TABLE    IF NOT EXISTS verification.tb_relation (
    relation_id       INTEGER PRIMARY KEY DEFAULT nextval( 'verification.sq_relation' ),
    label             VARCHAR NOT NULL,
    UNIQUE(label)
);


CREATE SEQUENCE IF NOT EXISTS verification.sq_relation_sub_table;
CREATE TABLE    IF NOT EXISTS verification.tb_relation_sub_table (
    relation_sub_table_id     INTEGER PRIMARY KEY DEFAULT nextval( 'verification.sq_relation_sub_table' ),
    relation                  INTEGER REFERENCES verification.tb_relation(relation_id),
    sub_table                 name NOT NULL,
    primary_key               name NOT NULL,
    join_table                INTEGER REFERENCES verification.tb_relation_sub_table,
    join_key                  name,
    CONSTRAINT ct_join_check CHECK ( ( join_table IS NULL AND join_key IS NULL ) OR (join_table IS NOT NULL AND join_key IS NOT NULL ) )
);

CREATE SEQUENCE IF NOT EXISTS verification.sq_relation_inner_node;
CREATE TABLE    IF NOT EXISTS verification.tb_relation_inner_node (
    relation_map_id       INTEGER PRIMARY KEY DEFAULT nextval( 'verification.sq_relation_inner_node' ),
    relation_id           INTEGER NOT NULL REFERENCES verification.tb_relation,
    primary_key_value     INTEGER NOT NULL,
    root_inner_node       INTEGER NOT NULL REFERENCES verification.tb_inner_node
);


INSERT INTO verification.tb_relation(label) VALUES('Ordering');
INSERT INTO verification.tb_relation_sub_table (relation, sub_table, primary_key)
VALUES ( 1, 'tb_order', 'order_id' );

INSERT INTO verification.tb_relation_sub_table (relation, sub_table, primary_key, join_table, join_key)
VALUES
( 1, 'tb_line_item', 'line_item_id', 1, 'order_id'   ),
( 1, 'tb_product'  , 'product_id'  , 2, 'product_id' ),
( 1, 'tb_client'   , 'client_id'   , 1, 'client_id'  )


