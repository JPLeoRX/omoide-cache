# Run dependency injections
import os
import tekleo_common_utils
from injectable import load_injection_container
load_injection_container()
load_injection_container(str(os.path.dirname(tekleo_common_utils.__file__)))

# Other imports only after injection was performed
from fastapi import FastAPI
from resources.resource_ping import router_ping

# Create app
app = FastAPI()

# Register routers
app.include_router(router_ping)
