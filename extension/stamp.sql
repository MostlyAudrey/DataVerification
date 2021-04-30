CREATE OR REPLACE FUNCTION verification._create_leaf_node_for_join_table(
    in_relation             INTEGER,
    in_primary_table        VARCHAR,
    in_primary_key          VARCHAR,
    in_primary_key_value    INTEGER,
    in_join_table_id        INTEGER,
    in_join_table           VARCHAR,
    in_join_key             VARCHAR,
    in_join_table_pk        VARCHAR
)
RETURNS integer[] AS
    $_$
DECLARE
    my_string_agg       varchar;
    my_hash_val         char(64);
    my_pk_value         integer;
    my_new_leaf_nodes   integer[];
    my_new_child_nodes  integer[];
    my_leaf_node_id     integer;
BEGIN
    -- Get the columns of the join table 
    SELECT 'SELECT substring(sha256(('||
           string_agg('b.'||attname, '::VARCHAR||')||
           ')::BYTEA)::VARCHAR,3,64),b.'||
           in_join_table_pk||
           ' FROM '||
           in_primary_table||
           ' a JOIN ' ||
           in_join_table||
           ' b ON a.'||
           in_join_key ||
           ' = b.'||
           in_join_key||
           ' WHERE a.'||
           in_primary_key||
           ' = '||
           in_primary_key_value
      INTO my_string_agg 
      FROM pg_attribute,pg_class
     WHERE attrelid = pg_class.oid
       AND attnum > 0
       AND pg_class.relname=in_join_table;    

    -- Hash all of the values in the root table at the relation_pk

    FOR my_hash_val, my_pk_value in EXECUTE my_string_agg
    LOOP
        -- Create the leaf node for the relation_pk
        INSERT INTO verification.tb_leaf_node (
            table_name,
            primary_key_value,
            data_hash
        ) VALUES (
            in_join_table,
            my_pk_value,
            my_hash_val
        )
        RETURNING leaf_node_id INTO my_leaf_node_id;
        SELECT array_append(my_new_leaf_nodes, my_leaf_node_id) INTO my_new_leaf_nodes;


        -- 2. Create leaf nodes for all tables that join to this join table:
        SELECT array_agg("1")
          INTO my_new_child_nodes
          FROM (
                SELECT unnest(verification._create_leaf_node_for_join_table( in_relation, in_join_table, in_join_table_pk, my_pk_value, rst.relation_sub_table_id, rst.sub_table::varchar, rst.join_key::varchar, rst.primary_key::varchar)) as "1"
                  FROM verification.tb_relation_sub_table rst
                 WHERE rst.relation = in_relation
                   AND rst.join_table = in_join_table_id
            ) as foo;

        SELECT my_new_leaf_nodes||my_new_child_nodes INTO my_new_leaf_nodes;

    END LOOP;

    RETURN my_new_leaf_nodes;
END
    $_$
        language plpgsql;



CREATE OR REPLACE FUNCTION verification.stamp(  
    in_relation integer,
    in_relation_pk integer
)
RETURNS char(64) AS
    $_$
DECLARE
    my_primary_table        varchar;
    my_primary_key          varchar;
    my_primary_table_id     integer;
    my_string_agg           varchar;
    my_hash_val             char(64);
    my_leaf_node_id         integer;
    my_new_nodes            integer[];
    my_inner_node_id        integer;
    my_new_inner_nodes      integer[];
    my_nodes_cnt            integer;
    my_while_counter        integer := 1;
BEGIN

    -------------------------------
    --     Create Leaf Nodes     --
    -------------------------------

    -- 1. Create leaf node for root table:

    -- Get Root Table from relation
    SELECT rst.relation_sub_table_id, rst.sub_table,    rst.primary_key
      INTO my_primary_table_id,       my_primary_table, my_primary_key
      FROM verification.tb_relation_sub_table rst
     WHERE rst.relation = in_relation AND rst.join_table IS NULL;


    -- Get the columns of the root table 
    SELECT 'SELECT substring(sha256(('||
           string_agg(attname, '::VARCHAR||')||
           ')::BYTEA)::VARCHAR,3,64) FROM '||
           my_primary_table||
           ' WHERE '||
           my_primary_key||
           ' = '||
           in_relation_pk
      INTO my_string_agg 
      FROM pg_attribute,pg_class
     WHERE attrelid = pg_class.oid
       AND attnum > 0
       AND pg_class.relname=my_primary_table;

    -- Hash all of the values in the root table at the relation_pk
    EXECUTE my_string_agg INTO my_hash_val;

    -- Create the leaf node for the relation_pk
    INSERT INTO verification.tb_leaf_node (
        table_name,
        primary_key_value,
        data_hash
    ) VALUES (
        my_primary_table,
        in_relation_pk,
        my_hash_val
    ) RETURNING leaf_node_id INTO my_leaf_node_id;
    

    -- 2. Create leaf nodes for all tables that join to the root table:
    SELECT array_agg("1")
      INTO my_new_nodes
      FROM (
            SELECT unnest(verification._create_leaf_node_for_join_table( in_relation, my_primary_table, my_primary_key, in_relation_pk, rst.relation_sub_table_id, rst.sub_table::varchar, rst.join_key::varchar, rst.primary_key::varchar)) as "1"
              FROM verification.tb_relation_sub_table rst
             WHERE rst.relation = in_relation
               AND rst.join_table = my_primary_table_id
        ) as foo;
    SELECT array_append(my_new_nodes, my_leaf_node_id) INTO my_new_nodes;
    SELECT array_length( my_new_nodes, 1 ) INTO my_nodes_cnt; 

    -- 3. Create the inner node for every 2 leaf nodes
    WHILE my_while_counter <= my_nodes_cnt
    LOOP
        IF my_while_counter + 1 <= my_nodes_cnt THEN
            INSERT INTO verification.tb_inner_node( left_child, left_child_hash, right_child, right_child_hash, are_children_leaves )
            VALUES( 
                my_new_nodes[my_while_counter],
                (
                    SELECT substring(sha256((leaf_node_id::VARCHAR||table_name||primary_key_value||data_hash)::BYTEA)::VARCHAR,3,64)
                      FROM verification.tb_leaf_node
                     WHERE leaf_node_id = my_new_nodes[my_while_counter]
                ),
                my_new_nodes[my_while_counter+1],
                (
                    SELECT substring(sha256((leaf_node_id::VARCHAR||table_name||primary_key_value||data_hash)::BYTEA)::VARCHAR,3,64)
                      FROM verification.tb_leaf_node
                     WHERE leaf_node_id = my_new_nodes[my_while_counter+1]
                ),
                True
            )
            RETURNING inner_node_id INTO my_inner_node_id; 
            SELECT array_append(my_new_inner_nodes, my_inner_node_id) INTO my_new_inner_nodes;
        ELSE
            INSERT INTO verification.tb_inner_node( left_child, left_child_hash, are_children_leaves )
            VALUES( 
                my_new_nodes[my_while_counter],
                (
                    SELECT substring(sha256((leaf_node_id::VARCHAR||table_name||primary_key_value||data_hash)::BYTEA)::VARCHAR,3,64)
                      FROM verification.tb_leaf_node
                     WHERE leaf_node_id = my_new_nodes[my_while_counter]
                ),
                True
            )
            RETURNING inner_node_id INTO my_inner_node_id; 
            SELECT array_append(my_new_inner_nodes, my_inner_node_id) INTO my_new_inner_nodes;
        END IF;

        my_while_counter := my_while_counter + 2;
    END LOOP;

    SELECT array_length( my_new_inner_nodes, 1 ), my_new_inner_nodes, NULL INTO my_nodes_cnt, my_new_nodes, my_new_inner_nodes;
    WHILE my_nodes_cnt > 1
    LOOP
        my_while_counter := 1;
        WHILE my_while_counter <= my_nodes_cnt
        LOOP
            IF my_while_counter + 1 <= my_nodes_cnt THEN
                INSERT INTO verification.tb_inner_node( left_child, left_child_hash, right_child, right_child_hash, are_children_leaves )
                VALUES( 
                    my_new_nodes[my_while_counter],
                    (
                        SELECT substring(sha256((inner_node_id::VARCHAR||left_child::VARCHAR||left_child_hash||right_child::VARCHAR||right_child_hash||are_children_leaves::VARCHAR)::BYTEA)::VARCHAR,3,64)
                          FROM verification.tb_inner_node
                         WHERE inner_node_id = my_new_nodes[my_while_counter]
                    ),
                    my_new_nodes[my_while_counter+1],
                    (
                        SELECT substring(sha256((inner_node_id::VARCHAR||left_child::VARCHAR||left_child_hash||right_child::VARCHAR||right_child_hash||are_children_leaves::VARCHAR)::BYTEA)::VARCHAR,3,64)
                          FROM verification.tb_inner_node
                         WHERE inner_node_id = my_new_nodes[my_while_counter+1]
                    ),
                    False
                )
                RETURNING inner_node_id INTO my_inner_node_id; 
                SELECT array_append(my_new_inner_nodes, my_inner_node_id) INTO my_new_inner_nodes;
            ELSE
                INSERT INTO verification.tb_inner_node( left_child, left_child_hash, are_children_leaves )
                VALUES( 
                    my_new_nodes[my_while_counter],
                    (
                        SELECT substring(sha256((inner_node_id::VARCHAR||left_child::VARCHAR||left_child_hash||right_child::VARCHAR||right_child_hash||are_children_leaves::VARCHAR)::BYTEA)::VARCHAR,3,64)
                          FROM verification.tb_inner_node
                         WHERE inner_node_id = my_new_nodes[my_while_counter]
                    ),
                    False
                )
                RETURNING inner_node_id INTO my_inner_node_id; 
                SELECT array_append(my_new_inner_nodes, my_inner_node_id) INTO my_new_inner_nodes;
            END IF;

            my_while_counter := my_while_counter + 2;
        END LOOP;

        SELECT array_length( my_new_inner_nodes, 1 ), my_new_inner_nodes, NULL INTO my_nodes_cnt, my_new_nodes, my_new_inner_nodes;
    END LOOP;

    INSERT INTO verification.tb_relation_inner_node(relation_id, primary_key_value, root_inner_node)
         VALUES (
                    in_relation,
                    in_relation_pk,
                    my_new_nodes[1]
            );

    RETURN ( SELECT substring(sha256((inner_node_id::VARCHAR||left_child::VARCHAR||left_child_hash||right_child::VARCHAR||right_child_hash||are_children_leaves::VARCHAR)::BYTEA)::VARCHAR,3,64)
               FROM verification.tb_inner_node
              WHERE inner_node_id = my_new_nodes[1]);



    
END
    $_$
        language plpgsql;
