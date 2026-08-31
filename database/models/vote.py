TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS suggestion_vote (
    id INT PRIMARY KEY AUTO_INCREMENT,
    suggestion_id INT NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    vote_type VARCHAR(10) NOT NULL,
    UNIQUE KEY unique_user_suggestion (suggestion_id, user_id),
    FOREIGN KEY (suggestion_id) REFERENCES suggestions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""