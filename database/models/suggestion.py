from enum import StrEnum

class SuggestionStatus(StrEnum):
    PENDING = "Pendiente"
    IN_REVISION = "En Revisión"
    APPROVED = "Aceptada"
    DENIED = "Rechazada"

TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS suggestion (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_user VARCHAR(64) NOT NULL,
    id_channel VARCHAR(64) NOT NULL,
    id_message VARCHAR(64) NOT NULL,
    user_name VARCHAR(255),
    description TEXT NOT NULL,
    moderator_id VARCHAR(64),
    moderator_name VARCHAR(255),
    moderator_answer TEXT,
    status ENUM('Pendiente','En Revisión','Aceptada','Rechazada') DEFAULT 'Pendiente',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""