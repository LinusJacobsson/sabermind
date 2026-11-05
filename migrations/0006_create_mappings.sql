CREATE TABLE mappings (
    object_id text PRIMARY KEY
        CHECK (object_id ~ '^[0-9a-v]{19}[0g]$'),
    object_type text NOT NULL,
    external_id text NOT NULL,
    source text NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT now(),
    created_at timestamptz NOT NULL DEFAULT now()
);