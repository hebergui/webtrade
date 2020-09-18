import logging
import time

from queue import Queue
from threading import Thread

from helpers import *

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DownloadWorker(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            # Get the work from the queue and expand the tuple
            name, indice, ref, url_ref = self.queue.get()
            try:
                name, debug = download_data(name, indice, ref, url_ref)
                logger.info('End {} (Code: {})'.format(name, debug))
            finally:
                self.queue.task_done()


def main():
    ts = time.time()
    url = 'https://screener.blogbourse.net/societes.html'
    url_ref = "https://screener.blogbourse.net/"

    #companies = get_companies(url)

    companies = [["Total", "CAC 40", "cours-total.html"],
            ["Vallourec", "N/C", "cours-vallourec.html"],
            ["Pharmanext", "Euronext Growth", "cours-pharnext.html"],
            ["Solutions 30 SE", "Euronext Growth", "cours-solutions-30-se.html"]
        ]

    # Create a queue to communicate with the worker threads
    queue = Queue()

    # Create 8 worker threads
    for x in range(8):
        worker = DownloadWorker(queue)
        # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()

    # Put the tasks into the queue as a tuple
    for name, indice, ref in companies:
        logger.info('Queueing {}'.format(name))
        queue.put((name, indice, ref, url_ref))

    # Causes the main thread to wait for the queue to finish processing all the tasks
    queue.join()
    logging.info('Took %s', time.time() - ts)


if __name__ == '__main__':
    main()
