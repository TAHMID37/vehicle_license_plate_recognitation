# vehicle_license_plate_recognitation

python -m venv env


CREATE TABLE vehicle_logs (
    id SERIAL PRIMARY KEY,
    license_plate VARCHAR(50) NOT NULL,
    entry_time TIMESTAMP DEFAULT NOW(),
    exit_time TIMESTAMP,
    charged_amount FLOAT DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE
);