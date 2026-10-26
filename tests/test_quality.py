import pytest
import pandas as pd
from unittest.mock import MagicMock
from src.validation.quality import validate_orders

def test_validate_orders_detects_invalid_quantity_and_price():
    # 1. Préparation des données de test
    mock_engine = MagicMock()
    
    # Simulation des réponses SQL pour les clients et produits valides
    valid_customers = pd.DataFrame({'client_id': ['CUST-001']})
    valid_products = pd.DataFrame({'produit_id': ['PROD-001']})
    
    def mock_read_sql(query, engine):
        if "source.customers" in query:
            return valid_customers
        elif "source.products" in query:
            return valid_products
        return pd.DataFrame()

    pd.read_sql = MagicMock(side_effect=mock_read_sql)

    # DataFrame contenant un enregistrement valide et deux invalides
    test_data = pd.DataFrame([
        {
            'commande_id': 'ORD-TEST-1',
            'client_id': 'CUST-001',
            'produit_id': 'PROD-001',
            'quantite': 2,
            'prix_unitaire': 50.0
        },
        {
            'commande_id': 'ORD-TEST-2',
            'client_id': 'CUST-001',
            'produit_id': 'PROD-001',
            'quantite': -1,  # Quantité invalide
            'prix_unitaire': 50.0
        },
        {
            'commande_id': 'ORD-TEST-3',
            'client_id': 'CUST-001',
            'produit_id': 'PROD-001',
            'quantite': 1,
            'prix_unitaire': 0.0  # Prix invalide
        }
    ])

    # 2. Exécution de la validation
    df_clean, df_rejected = validate_orders(test_data, mock_engine)

    # 3. Vérifications (Assertions)
    assert len(df_clean) == 1
    assert len(df_rejected) == 2
    assert 'INVALID_QUANTITY' in df_rejected.iloc[0]['rejection_reason']
    assert 'INVALID_PRICE' in df_rejected.iloc[1]['rejection_reason']