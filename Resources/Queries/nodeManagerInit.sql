-- Create if not exists nodes table
CREATE TABLE IF NOT EXISTS infra.nodes
(
    node_id text COLLATE pg_catalog."default" NOT NULL,
    node_name text COLLATE pg_catalog."default" NOT NULL,
    node_ip text COLLATE pg_catalog."default",
    node_os text COLLATE pg_catalog."default",
    CONSTRAINT nodes_pkey PRIMARY KEY (node_id, node_name)
);

-- Create if not exists node_status table
CREATE TABLE IF NOT EXISTS infra.node_status
(
    node_id text COLLATE pg_catalog."default" NOT NULL,
    node_status text COLLATE pg_catalog."default",
    updated_on timestamp without time zone,
    CONSTRAINT node_status_pkey PRIMARY KEY (node_id)
);

-- Create if not exists node_health table
CREATE TABLE IF NOT EXISTS infra.node_health
(
    node_id text COLLATE pg_catalog."default" NOT NULL,
    health numeric,
    CONSTRAINT node_health_pkey PRIMARY KEY (node_id)
)




