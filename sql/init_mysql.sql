CREATE TABLE users (
  user_id INT,
  signup_time DATETIME,
  segment VARCHAR(20),
  marketing_channel VARCHAR(20),
  device_type VARCHAR(20)
);

CREATE TABLE sessions (
  session_id VARCHAR(50),
  user_id INT,
  session_start DATETIME,
  session_end DATETIME,
  is_promotion_day BOOLEAN,
  session_length_sec DOUBLE
);

CREATE TABLE events (
  event_id INT,
  session_id VARCHAR(50),
  user_id INT,
  event_name VARCHAR(50),
  event_time DATETIME,
  amount DOUBLE,
  segment VARCHAR(20),
  event_date DATE
);

CREATE TABLE purchases (
  purchase_id INT,
  user_id INT,
  session_id VARCHAR(50),
  purchase_time DATETIME,
  amount DOUBLE,
  product_id INT,
  coupon_used BOOLEAN
);

CREATE TABLE daily_metrics (
  date DATE,
  dau INT,
  new_users INT,
  sessions INT,
  purchases INT,
  revenue DOUBLE
);
