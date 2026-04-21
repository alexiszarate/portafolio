USE documentos_app;

CREATE TABLE documentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    tipo_documento VARCHAR(100) NOT NULL,
    documento VARCHAR(255) NOT NULL,
    fecha_emision DATE NOT NULL,
    fecha_caducidad DATE NOT NULL,
    fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);