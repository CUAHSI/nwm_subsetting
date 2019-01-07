import os

# Server settings

address="0.0.0.0"
port="8080"

debug=True
static_path = os.path.join(os.path.dirname(__file__), "static")
template_path = os.path.join(os.path.dirname(__file__), "templates")


# logging settings

log_dir = os.path.join(os.getcwd(), 'logs')
log_file_size = 1024 * 20
log_count = 10

# levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
access_level = 'INFO'
application_level = 'INFO'
general_level = 'INFO'
