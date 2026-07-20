"""Training worker entry point.

Sprint 4: polls the database for queued jobs. Sprint 5 will replace this
polling loop with a Kafka consumer (TrainingRequested events) — the claim /
process / persist core stays identical.
"""

import logging
import time

from trainer.config import settings
from trainer.db import SessionLocal, claim_next_job
from trainer.runner import process_job

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s [%(name)s] %(message)s",
)
logger = logging.getLogger("trainer")


def main() -> None:
    logger.info("training service started (poll every %.1fs)", settings.poll_interval_seconds)
    while True:
        with SessionLocal() as session:
            job = claim_next_job(session)
            if job is None:
                time.sleep(settings.poll_interval_seconds)
                continue
            logger.info("claimed job %s (model=%s)", job.id, job.model_type)
            process_job(session, job)


if __name__ == "__main__":
    main()
