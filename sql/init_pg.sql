CREATE TABLE users (
  user_id INTEGER,
  signup_time TIMESTAMP,
  segment VARCHAR(20),
  marketing_channel VARCHAR(20),
  device_type VARCHAR(20)
);

CREATE TABLE sessions (
  session_id VARCHAR(50),
  user_id INTEGER,
  session_start TIMESTAMP,
  session_end TIMESTAMP,
  is_promotion_day BOOLEAN,
  session_length_sec DOUBLE PRECISION
);

CREATE TABLE events (
  event_id INTEGER,
  session_id VARCHAR(50),
  user_id INTEGER,
  event_name VARCHAR(50),
  event_time TIMESTAMP,
  amount DOUBLE PRECISION,
  segment VARCHAR(20),
  event_date DATE
);

CREATE TABLE purchases (
  purchase_id INTEGER,
  user_id INTEGER,
  session_id VARCHAR(50),
  purchase_time TIMESTAMP,
  amount DOUBLE PRECISION,
  product_id INTEGER,
  coupon_used BOOLEAN
);

CREATE TABLE daily_metrics (
  date DATE,
  dau INTEGER,
  new_users INTEGER,
  sessions INTEGER,
  purchases INTEGER,
  revenue DOUBLE PRECISION
);
