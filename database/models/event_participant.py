TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS event_participant(
    id INT AUTO_INCREMENT PRIMARY KEY,
    message_id VARCHAR(64) NOT NULL,
    discord_id VARCHAR(64) NOT NULL,
    discord_name VARCHAR(64) NOT NULL,
    joined_at TIMESTAMP NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""