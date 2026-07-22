"""Training worker entry point.

Consumes TrainingRequested events from Kafka and runs the training pipeline.
"""

import logging

from trainer.consumer import run

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s [%(name)s] %(message)s",
)
logger = logging.getLogger("trainer")


def main() -> None:
    logger.info("training service starting")
    run()


if __name__ == "__main__":
    main()
