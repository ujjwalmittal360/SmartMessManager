import os
import logging
from app import app

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Create data directory and CSV files if they don't exist
    from utils import init_data_files
    init_data_files()
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
