TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS route_participant (
    id INT PRIMARY KEY AUTO_INCREMENT,
    message_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    UNIQUE KEY unique_user_route (message_id, user_id),
    FOREIGN KEY (message_id) REFERENCES route(message_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""