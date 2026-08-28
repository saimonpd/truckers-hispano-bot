from dataclasses import dataclass
from typing import Optional

TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS empresa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_empresa VARCHAR(255) NOT NULL,
    dueño_empresa VARCHAR(255) NOT NULL,
    rol_id VARCHAR(64) NOT NULL,
    canal_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""
