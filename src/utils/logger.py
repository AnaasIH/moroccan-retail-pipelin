import logging
import os

def setup_logger(name="data_pipeline"):
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] - %(message)s')
        
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        fh = logging.FileHandler("logs/pipeline.log")
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
    return logger