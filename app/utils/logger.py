import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

class CustomLogger:
    def __init__(self, name):
        self.name = name
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Create formatters
        self.detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Setup handlers
        self._setup_file_handlers()
        self._setup_latest_handlers()
        self._setup_console_handler()
    
    def _setup_file_handlers(self):
        # Regular log file with date
        log_file = self.logs_dir / f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(self.detailed_formatter)
        self.logger.addHandler(file_handler)
    
    def _setup_latest_handlers(self):
        # Latest log file
        latest_log = self.logs_dir / f"{self.name}_latest.log"
        if latest_log.exists():
            latest_log.unlink()  # Delete existing latest log
        
        latest_handler = logging.FileHandler(latest_log)
        latest_handler.setLevel(logging.DEBUG)
        latest_handler.setFormatter(self.detailed_formatter)
        self.logger.addHandler(latest_handler)
    
    def _setup_console_handler(self):
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(self.simple_formatter)
        self.logger.addHandler(console_handler)
    
    def get_logger(self):
        return self.logger

# Create loggers for different components
def setup_service_loggers():
    tts_logger = CustomLogger("tts_service").get_logger()
    llm_logger = CustomLogger("llm_service").get_logger()
    route_logger = CustomLogger("routes").get_logger()
    