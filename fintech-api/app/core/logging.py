import logging
import sys

def configure_logging():
    """Configure logging for the application"""
    # Force remove all existing handlers
    root = logging.getLogger()
    root.handlers = []
    
    # Set level to DEBUG to see everything
    root.setLevel(logging.DEBUG)
    
    # Create console handler that writes to stderr (uvicorn uses stderr)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.DEBUG)
    
    # Create formatter with more details
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to root logger
    root.addHandler(console_handler)
    
    # Also add a handler to stdout for print statements
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)
    root.addHandler(stdout_handler)
    
    # Configure uvicorn loggers explicitly
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(logging.INFO)
    uvicorn_logger.handlers = []
    uvicorn_logger.addHandler(console_handler)
    
    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_access.setLevel(logging.INFO)
    uvicorn_access.handlers = []
    uvicorn_access.addHandler(console_handler)
    
    # Configure our app loggers explicitly
    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.DEBUG)
    app_logger.propagate = True
    
    app_core_logger = logging.getLogger("app.core")
    app_core_logger.setLevel(logging.DEBUG)
    app_core_logger.propagate = True
    
    app_services_logger = logging.getLogger("app.services")
    app_services_logger.setLevel(logging.DEBUG)
    app_services_logger.propagate = True
    
    # Silence noisy loggers (pymongo, etc.)
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    logging.getLogger("pymongo.topology").setLevel(logging.WARNING)
    logging.getLogger("pymongo.serverSelection").setLevel(logging.WARNING)
    logging.getLogger("pymongo.connection").setLevel(logging.WARNING)
    logging.getLogger("motor").setLevel(logging.WARNING)
    
    # Test log
    test_logger = logging.getLogger(__name__)
    test_logger.info("=" * 80)
    test_logger.info("Logging configured successfully - all logs should be visible now")
    test_logger.info("=" * 80)
