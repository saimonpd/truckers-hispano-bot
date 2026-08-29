TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS evento (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message_id VARCHAR(64) NOT NULL,
    creador_id VARCHAR(64) NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    descripcion TEXT,
    juego_name VARCHAR(100) NOT NULL,
    juego_value VARCHAR(100) NOT NULL,
    servidor_name VARCHAR(100) NOT NULL,
    servidor_value VARCHAR(100) NOT NULL,
    organizador VARCHAR(255) NOT NULL,
    fecha VARCHAR(50) NOT NULL,
    hora_reunion VARCHAR(50) NOT NULL,
    hora_salida VARCHAR(50) NOT NULL,
    ruta_origen VARCHAR(255) NOT NULL,
    ruta_destino VARCHAR(255) NOT NULL,
    link_trucksbook VARCHAR(500) NOT NULL,
    link_truckersmp VARCHAR(500) NOT NULL,
    parada_intermedio VARCHAR(255),
    dlcs_requeridos VARCHAR(255),
    carga VARCHAR(255) NOT NULL,
    trailer VARCHAR(255) NOT NULL,
    ruta_imagen VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""
