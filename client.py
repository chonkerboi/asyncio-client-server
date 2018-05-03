"""Throttling TCP client script (see 'ThrottlingClient' class for mote information)

Send up to 1 requests per second:
python3.6 client.py 1

Send up to 10 requests per second:
python3.6 client.py 20

Send up to 100 requests per second:
python3.6 client.py 100

Send up to N requests per second:
python3.6 client.py N
"""
import asyncio
import logging
import argparse
import itertools

import common

LOGGER = logging.getLogger(__name__)


class ThrottlingClient:
    """A TCP client that throttle requests"""

    def __init__(self, host, port, frequency):
        """A TCP client that throttle requests.

        Note: see 'make_requests' function for more information about the send rate (frequency).
              This class will ensure that the maximum number of requests per second is 'frequency' but in practice will
              be somewhat lower than this theoretical maximum.

        Args:
            host: the host address to connect to.
            port: the port to connect to.
            frequency: how many requests should be sent per second? (see 'make_requests' function for more information).
        """
        self.host = host
        self.port = port
        self.interval = 1 / frequency
        self.counter = itertools.count()

    async def start(self):
        """Make (schedule) requests.

        Note: This is not as accurate as expected. One reason is because of the overhead when creating the coroutine.
              when frequency is 10 the change is not significant enough to see.
              when the frequency is 100 the average send frequency is 90
              when the frequency is 200 the average send frequency is 166
        """
        while True:
            asyncio.ensure_future(self.send_request())  # ensure_future is faster than await in this case.
            await asyncio.sleep(self.interval)

    async def send_request(self):
        """Send one request."""
        try:
            _, writer = await asyncio.open_connection(self.host, self.port)
        except ConnectionError as ex:
            LOGGER.error(ex)
            return

        counter = str(next(self.counter))
        LOGGER.info('%s: sending request to server', counter)
        writer.write(counter.encode())
        writer.close()


def parse_args():  # pragma: no cover
    """Parse command lin arguments.

    Returns:
        the command line options.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('frequency', type=float)
    return parser.parse_args()


def main():
    """Main entry point."""
    common.init_logging()
    options = parse_args()
    client = ThrottlingClient('127.0.0.1', 8888, options.frequency)
    asyncio.get_event_loop().run_until_complete(client.start())
    asyncio.get_event_loop().close()


if __name__ == '__main__':
    main()
