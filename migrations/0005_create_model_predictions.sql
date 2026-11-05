CREATE TABLE model_predictions (
    prediction_id text PRIMARY KEY
        CHECK (prediction_id ~ '^[0-9a-v]{19}[0g]$'),
    event_id text NOT NULL REFERENCES events(event_id) ON DELETE CASCADE,
    model_name text NOT NULL,
    market text NOT NULL,
    outcome text NOT NULL,
    predicted_probability numeric NOT NULL CHECK (predicted_probability >= 0 AND predicted_probability <= 1),
    updated_at timestamptz NOT NULL DEFAULT now(),
    created_at timestamptz NOT NULL DEFAULT now()
);