from sqlalchemy import text, engine

def load_staging_to_dw(db_engine: engine.Engine):
    """
    Transforme les données de staging et effectue un UPSERT dans dw.fact_sales.
    Garantit l'idempotence du traitement.
    """
    upsert_query = """
    INSERT INTO dw.fact_sales (
        commande_id,
        date_commande,
        client_id,
        produit_id,
        quantite,
        prix_unitaire,
        montant_total,
        statut,
        magasin_ville,
        updated_at
    )
    SELECT 
        commande_id,
        date_commande::timestamp,
        client_id,
        produit_id,
        quantite,
        prix_unitaire,
        (quantite * prix_unitaire) AS montant_total,
        statut,
        magasin_ville,
        CURRENT_TIMESTAMP AS updated_at
    FROM staging.orders_staging
    ON CONFLICT (commande_id)
    DO UPDATE SET
        date_commande = EXCLUDED.date_commande,
        client_id = EXCLUDED.client_id,
        produit_id = EXCLUDED.produit_id,
        quantite = EXCLUDED.quantite,
        prix_unitaire = EXCLUDED.prix_unitaire,
        montant_total = EXCLUDED.montant_total,
        statut = EXCLUDED.statut,
        magasin_ville = EXCLUDED.magasin_ville,
        updated_at = CURRENT_TIMESTAMP;
    """
    
    with db_engine.connect() as connection:
        trans = connection.begin()
        try:
            result = connection.execute(text(upsert_query))
            trans.commit()
            return result.rowcount
        except Exception as e:
            trans.rollback()
            raise e