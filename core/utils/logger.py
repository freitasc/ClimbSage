import logging
import os
from datetime import datetime

def setup_logger(name: str, log_file: str, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    handler = logging.FileHandler(f'logs/{log_file}')
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Add console output
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

debug_logger = setup_logger('debug', 'debug.log')
time_logger = setup_logger('time', 'times.log', logging.INFO)