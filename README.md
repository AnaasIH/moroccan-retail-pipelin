# Moroccan Retail Data Pipeline (Production-Style ETL)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)
![pytest](https://img.shields.io/badge/Tested%20with-pytest-green)

## 📌 Présentation du Projet
Ce projet simule l'architecture et l'implémentation d'un **Pipeline de Données de Production** pour un groupe de distribution/retail au Maroc (**Atlas Distribution**).

Il permet d'ingérer quotidiennement des flux de transactions (CSV), de contrôler rigoureusement la qualité des données, d'isoler les anomalies dans une zone de quarantaine, et d'alimenter un Data Warehouse PostgreSQL via un mécanisme d'**UPSERT idempotent**.

---

## 🏗️ Architecture Globale

```text
[Sources: CSV Files + Postgres Source]
                  │
                  ▼
         [Extraction Python]
                  │
                  ▼
       [Data Quality Engine]
        /                 \
       / (Valid)           \ (Invalid)
      ▼                     ▼
[Staging Schema]     [Audit Quarantine]
      │
      ▼ (UPSERT / Idempotent)
[Data Warehouse Schema (dw.fact_sales)]
      │
      ▼
[Audit & Execution Logs]