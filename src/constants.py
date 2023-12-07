from pathlib import Path
# URL constants
MAIN_DOC_URL = 'https://docs.python.org/3/'
PEP_TABLE_URL = 'https://peps.python.org/'

# Argument constants
PRETTY = 'pretty'
FILE = 'file'

# DIR constants
BASE_DIR = Path(__file__).parent
LOGS_DIR_NAME = 'logs'
RESULTS_DIR_NAME = 'results'

# Files
LOG_FILE_NAME = 'parser.log'

# Format
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'

# Encoding
LOG_ENCODING = 'utf-8'
RESPONSE_ENCODING = 'utf-8'

EXPECTED_STATUS = {
    'A': ('Accepted', 'Active'),
    'D': ('Deferred'),
    '': ('Draft'),
    'F': ('Final'),
    'P': ('Provisional'),
    'R': ('Rejected'),
    'S': ('Superseded'),
    'W': ('Withdrawn'),
}
