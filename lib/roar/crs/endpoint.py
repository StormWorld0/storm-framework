from .transport import CRSD
from lib.smf.core.manage import ExceptionGate as eg


class CRS:

    @classmethod
    def send(cls, data: dict) -> dict:
        resp, err = CRSD.send_data(data)

        def _process_data(*args):
            for data in args:
                if data:
                    yield data

        # Management Exception
        eg.gate_stream(_process_data(resp, err))
        return resp
