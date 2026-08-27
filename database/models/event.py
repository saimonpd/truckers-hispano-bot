TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS evento (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message_id VARCHAR(64),
    creador_id VARCHAR(64),
    titulo VARCHAR(255),
    descripcion TEXT,
    juego_name VARCHAR(100),
    juego_value VARCHAR(100),
    servidor_name VARCHAR(100),
    servidor_value VARCHAR(100),
    organizador VARCHAR(255),
    fecha VARCHAR(50),
    hora_reunion VARCHAR(50),
    hora_salida VARCHAR(50),
    ruta_origen VARCHAR(255),
    ruta_destino VARCHAR(255),
    link_trucksbook VARCHAR(500),
    link_truckersmp VARCHAR(500),
    parada_intermedio VARCHAR(255),
    dlcs_requeridos VARCHAR(255),
    carga VARCHAR(255),
    trailer VARCHAR(255),
    ruta_imagen VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""
