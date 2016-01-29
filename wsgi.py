import os
import sys

sys.path.append(os.path.join(sys.path[0], 'libs/'))
sys.path.append(os.path.join(sys.path[0], './'))

from app.main import app as application