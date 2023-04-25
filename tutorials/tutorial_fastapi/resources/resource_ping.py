from fastapi import APIRouter
from tekleo_common_message_protocol import PingOutput
from tekleo_common_utils import UtilsPing

router_ping = APIRouter()
utils_ping = UtilsPing()


@router_ping.get("/ping", response_model=PingOutput)
def ping() -> PingOutput:
    return utils_ping.build()
