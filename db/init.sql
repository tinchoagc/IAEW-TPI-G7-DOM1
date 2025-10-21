CREATE TABLE patients (
  id SERIAL PRIMARY KEY,
  full_name TEXT NOT NULL,
  email TEXT UNIQUE
);

CREATE TABLE professionals (
  id SERIAL PRIMARY KEY,
  full_name TEXT NOT NULL,
  specialty TEXT
);

CREATE TABLE appointments (
  id SERIAL PRIMARY KEY,
  patient_id INT REFERENCES patients(id),
  professional_id INT REFERENCES professionals(id),
  scheduled_at TIMESTAMP NOT NULL,
  status TEXT DEFAULT 'CONFIRMED'
);
    