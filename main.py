import sys
import os

# إضافة المجلد الرئيسي للمشروع إلى مسارات البحث في Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from sqlalchemy import text
from src.utils.logger import setup_logger
from src.utils.db import get_db_engine
from src.validation.quality import validate_orders
from src.transformation.transform import load_staging_to_dw
logger = setup_logger()

def log_audit(engine, status, extracted, accepted, rejected, error_msg=None):
    query = """
    INSERT INTO audit.pipeline_execution_logs
    (pipeline_name, status, records_extracted, records_accepted, records_rejected, error_message)
    VALUES ('orders_daily_pipeline', :status, :extracted, :accepted, :rejected, :error_msg);
    """
    with engine.connect() as conn:
        trans = conn.begin()
        conn.execute(text(query), {
            "status": status,
            "extracted": extracted,
            "accepted": accepted,
            "rejected": rejected,
            "error_msg": error_msg
        })
        trans.commit()

def run_pipeline():
    logger.info("=== Start Moroccan Retail Data Pipeline ===")
    engine = get_db_engine()
    file_path = "data/raw/orders_20261022.csv"
    
    if not os.path.exists(file_path):
        logger.error(f"Target file not found: {file_path}")
        log_audit(engine, "FAILED", 0, 0, 0, f"File missing: {file_path}")
        return

    try:
        # 1. Extraction
        logger.info("Extracting CSV file...")
        df_raw = pd.read_csv(file_path)
        extracted_cnt = len(df_raw)

        # 2. Validation
        logger.info("Running Data Quality Checks...")
        df_clean, df_rejected = validate_orders(df_raw, engine)
        accepted_cnt = len(df_clean)
        rejected_cnt = len(df_rejected)

        # 3. Load Staging
        if not df_clean.empty:
            df_clean.to_sql("orders_staging", engine, schema="staging", if_exists="replace", index=False)

        # 4. Quarantine
        if not df_rejected.empty:
            df_rejected.to_sql("quarantine_orders", engine, schema="audit", if_exists="append", index=False)

        # 5. Transform & UPSERT to DW
        logger.info("Transforming & Loading to Data Warehouse (dw.fact_sales)...")
        rows_upserted = load_staging_to_dw(engine)
        logger.info(f"Successfully processed {rows_upserted} records in dw.fact_sales.")

        # 6. Audit Success Log
        log_audit(engine, "SUCCESS", extracted_cnt, accepted_cnt, rejected_cnt)
        logger.info("=== Pipeline Run Finished Successfully ===")

    except Exception as e:
        logger.error(f"Pipeline Execution Error: {str(e)}")
        log_audit(engine, "FAILED", 0, 0, 0, str(e))

if __name__ == "__main__":
    run_pipeline()