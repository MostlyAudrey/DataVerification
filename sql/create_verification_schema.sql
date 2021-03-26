CREATE SCHEMA IF NOT EXISTS verification;

CREATE SEQUENCE IF NOT EXISTS verification.sq_inner_node;
CREATE TABLE IF NOT EXISTS verification.tb_inner_node (
	inner_node_id 		INTEGER PRIMARY KEY DEFAULT nextval( 'verification.sq_inner_node' ),
    left_child    		INTEGER NOT NULL,
    left_child_hash 	VARCHAR NOT NULL,
    right_child	    	INTEGER,
    right_child_hash	VARCHAR
);

CREATE SEQUENCE IF NOT EXISTS verification.sq_leaf_node;
CREATE TABLE IF NOT EXISTS verification.tb_leaf_node (
    leaf_node_id 		INTEGER PRIMARY KEY DEFAULT nextval( 'verification.sq_leaf_node' ),
    table_name	     	VARCHAR NOT NULL,
    primary_key_value 	INTEGER NOT NULL,
    data_hash	    	VARCHAR NOT NULL
);
