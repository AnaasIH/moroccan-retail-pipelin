import pandas as pd
from sqlalchemy import engine

def validate_orders(df: pd.DataFrame, db_engine: engine.Engine):
    valid_customers = pd.read_sql("SELECT client_id FROM source.customers", db_engine)['client_id'].tolist()
    valid_products = pd.read_sql("SELECT produit_id FROM source.products", db_engine)['produit_id'].tolist()
    
    rejections = []
    clean_rows = []

    for idx, row in df.iterrows():
        errors = []
        
        if row['quantite'] <= 0:
            errors.append(f"INVALID_QUANTITY: {row['quantite']}")
            
        if row['prix_unitaire'] <= 0:
            errors.append(f"INVALID_PRICE: {row['prix_unitaire']}")
            
        if row['client_id'] not in valid_customers:
            errors.append(f"UNKNOWN_CUSTOMER: {row['client_id']}")
            
        if row['produit_id'] not in valid_products:
            errors.append(f"UNKNOWN_PRODUCT: {row['produit_id']}")

        if errors:
            rejections.append({
                'commande_id': row['commande_id'],
                'raw_data': row.to_json(),
                'rejection_reason': " | ".join(errors)
            })
        else:
            clean_rows.append(row)

    df_clean = pd.DataFrame(clean_rows)
    df_rejected = pd.DataFrame(rejections)
    
    if not df_clean.empty:
        df_clean = df_clean.drop_duplicates(subset=['commande_id'])

    return df_clean, df_rejected