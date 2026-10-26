-- 1. Création des Schemas
CREATE SCHEMA IF NOT EXISTS source;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS dw;
CREATE SCHEMA IF NOT EXISTS audit;

-- 2. Table Source Customers
CREATE TABLE source.customers (
    client_id VARCHAR(50) PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    ville VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    date_creation DATE NOT NULL
);

-- 3. Table Source Products
CREATE TABLE source.products (
    produit_id VARCHAR(50) PRIMARY KEY,
    nom_produit VARCHAR(100) NOT NULL,
    categorie VARCHAR(50) NOT NULL,
    prix_unitaire_mad NUMERIC(10, 2) NOT NULL
);

-- 4. Insertion des données de test
INSERT INTO source.customers (client_id, nom, ville, email, date_creation) VALUES
('CUST-001', 'Amine Bennani', 'Casablanca', 'amine.bennani@email.ma', '2023-01-15'),
('CUST-002', 'Sarah El Amrani', 'Rabat', 'sarah.elamrani@email.ma', '2023-02-20'),
('CUST-003', 'Youssef El Fassi', 'Tanger', 'youssef.elfassi@email.ma', '2023-03-10'),
('CUST-004', 'Meryem Chraibi', 'Marrakech', 'meryem.chraibi@email.ma', '2023-04-05');

INSERT INTO source.products (produit_id, nom_produit, categorie, prix_unitaire_mad) VALUES
('PROD-001', 'Huile d Olive 1L', 'Alimentaire', 85.00),
('PROD-002', 'Thé Vert Pack 500g', 'Alimentaire', 45.00),
('PROD-003', 'Caftan Moderne XL', 'Textile', 1200.00),
('PROD-004', 'Tajine en Terre Cuite', 'Artisanat', 150.00);


-- =====================================================
-- 5. Data Warehouse (DW Schema)
-- =====================================================

-- Table de Faits: Sales
CREATE TABLE IF NOT EXISTS dw.fact_sales (
    sales_key SERIAL PRIMARY KEY,
    commande_id VARCHAR(50) NOT NULL UNIQUE,
    date_commande TIMESTAMP NOT NULL,
    client_id VARCHAR(50) REFERENCES source.customers(client_id),
    produit_id VARCHAR(50) REFERENCES source.products(produit_id),
    quantite INT NOT NULL,
    prix_unitaire NUMERIC(10, 2) NOT NULL,
    montant_total NUMERIC(10, 2) NOT NULL,
    statut VARCHAR(20) NOT NULL,
    magasin_ville VARCHAR(50) NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 6. Audit & Monitoring Schema
-- =====================================================
CREATE TABLE IF NOT EXISTS audit.pipeline_execution_logs (
    execution_id SERIAL PRIMARY KEY,
    pipeline_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    records_extracted INT,
    records_accepted INT,
    records_rejected INT,
    execution_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT
);