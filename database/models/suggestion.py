from enum import StrEnum


class SuggestionStatus(StrEnum):
    PENDING = "Pendiente"
    IN_REVISION = "En Revisión"
    APPROVED = "Aceptada"
    DENIED = "Rechazada"

TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS suggestion (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_user BIGINT NOT NULL,
    id_channel BIGINT NOT NULL,
    id_message BIGINT NOT NULL,
    message VARCHAR(255) NOT NULL,
    positive_votes INT DEFAULT 0,
    negative_votes INT DEFAULT 0,
    moderator_id BIGINT,
    moderator_name VARCHAR(255),
    moderator_answer VARCHAR(255),
    status ENUM('Pendiente','En Revisión','Aceptada','Rechazada') DEFAULT 'Pendiente',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""