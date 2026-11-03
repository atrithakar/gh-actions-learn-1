import json
import logging
import os
from multiprocessing import Queue

import logging_loki


class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {"level": record.levelname.lower(), "msg": record.getMessage()}
        payload.update(getattr(record, "fields", {}))
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def setup_logging():
    logger = logging.getLogger("project97")
    if logger.handlers:  # avoid duplicate handlers on re-import
        return logger
    logger.setLevel(logging.INFO)

    fmt = JsonFormatter()

    loki = logging_loki.LokiQueueHandler(
        Queue(-1),
        url=os.environ["LOKI_URL"],
        tags={"app": "project97", "env": "prod"},
        version="1",
    )
    loki.setFormatter(fmt)
    logger.addHandler(loki)

    stdout = logging.StreamHandler()  # keeps `docker logs` working
    stdout.setFormatter(fmt)
    logger.addHandler(stdout)

    return logger