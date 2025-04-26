import logging

from rich.logging import RichHandler

logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    datefmt="[%X]",
    filename="test.log"
)
logger = logging.getLogger("rich")
