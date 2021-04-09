CREATE SEQUENCE IF NOT EXISTS public.sq_city;
CREATE TABLE    IF NOT EXISTS public.tb_city (
	city_id 	  INTEGER PRIMARY KEY DEFAULT nextval( 'sq_city' ),
    name          VARCHAR NOT NULL,
    state		  VARCHAR(2) NOT NULL,
    country       VARCHAR NOT NULL DEFAULT 'US',
    UNIQUE(name)
);

CREATE SEQUENCE IF NOT EXISTS public.sq_client;
CREATE TABLE    IF NOT EXISTS public.tb_client(
	client_id      INTEGER PRIMARY KEY DEFAULT nextval( 'sq_client' ),
	name		   VARCHAR NOT NULL,
	age			   INTEGER,
	address		   VARCHAR NOT NULL,
	city 		   INTEGER NOT NULL REFERENCES tb_city,
	zipcode 	   VARCHAR(5) NOT NULL
);

CREATE SEQUENCE IF NOT EXISTS public.sq_product;
CREATE TABLE    IF NOT EXISTS public.tb_product (
	product_id     INTEGER PRIMARY KEY DEFAULT nextval( 'sq_product' ),
	name		   VARCHAR NOT NULL,
	manufacturer   VARCHAR,
	UNIQUE(name)
);

CREATE SEQUENCE IF NOT EXISTS public.sq_order;
CREATE TABLE    IF NOT EXISTS public.tb_order(
	order_id   		INTEGER PRIMARY KEY DEFAULT nextval( 'sq_order' ),
	client_id	    INTEGER NOT NULL REFERENCES tb_client,
	created			DATE NOT NULL DEFAULT now()::DATE,
	UNIQUE(client_id, created)
);

CREATE SEQUENCE IF NOT EXISTS public.sq_line_item;
CREATE TABLE    IF NOT EXISTS public.tb_line_item (
	line_item_id  	INTEGER PRIMARY KEY DEFAULT nextval( 'sq_line_item' ),
	order_id 		INTEGER NOT NULL REFERENCES tb_order,
	product_id		INTEGER NOT NULL REFERENCES tb_product,
	quantity		NUMERIC NOT NULL DEFAULT 0,
	price			NUMERIC	NOT NULL DEFAULT 0,
	UNIQUE(order_id, product_id)
);
