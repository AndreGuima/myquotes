CREATE DATABASE IF NOT EXISTS myquotes_db;

USE myquotes_db;

CREATE TABLE quotes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    author VARCHAR(100) NOT NULL,
    text VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert a valid example row for fresh databases so developers have a record to inspect
INSERT INTO quotes (author, text) VALUES
    ('Admin', 'Este é um registro de exemplo criado automaticamente durante a inicialização do banco.');

