TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS vote (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_suggestion BIGINT NOT NULL,
    id_user BIGINT NOT NULL,
    vote_type VARCHAR(10) NOT NULL,
    FOREIGN KEY (id_suggestion) REFERENCES suggestion(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""