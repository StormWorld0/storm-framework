from .transport import CRSD
from lib.smf.core.manage import ExceptionManager as em


class CRS:

    @classmethod
    def send(cls, data: dict) -> dict:
        resp, err = CRSD.send_data(data)

        def _process_data(data1, data2):
            if data1:
                yield data1
            if data2:
                yield data2

        # Management Exception
        em.process_exc(_process_data(resp, err))
        return resp
