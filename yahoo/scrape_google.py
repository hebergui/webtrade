import re
import time
import logging
import requests
from queue import Queue
from threading import Thread
from bs4 import BeautifulSoup

skip_companies = ['whiteni', 'pacte-novation', 'toques-blanches', 'fsdv', 'cta-holding', 'green-energy',
                        'maison-antoine-baud', 'digitech', 'infoclip', 'toutabo', 'mybest-group', 'onlineformapro',
                        'rousselet-centrifugation', 'hexcel', 'datbim', 'toit-pour-toi', 'corep-lighting', 'consort-nt',
                        'condor-technologies', 'ag3i', 'firstcaution', 'one-experience', 'grecemar', 'd2l-group',
                        'securinfor', 'ardoin-saint-amand', 'groupe-carnivor', 'novatech-industries', 'parfex', 'olmix',
                        'visio-nerf', 'galeo-concept', 'fonciere-vindi', 'energie-europe-service',
                        'compagnie-miniere-grecemar', 'easson-telecom', 'mulann', 'guandao-puer-inves', 'media-lab',
                        'italy-innovazioni', 'emova-group2', 'saipppp', 'bourbon', 'lilly-company', 'vale', 'afone',
                        'alpha-mos', 'biom-up', 'rougier', 'eurasia-groupe', 'futuren', 'stallergenes-greer', 'cesar',
                        'groupimo', 'oxatis', 'primecity-investment', 'enensys-technologies', 'assima',
                        'solutions-30-se', 'traqueur', 'ivalis', 'bourrelier-group', 'ales-groupe', 'harvest',
                        'velcan-energy', 'millet-innovation', 'medicrea', 'weborama', 'acces-industrie', 'a2micile',
                        'vexim', 'global-ecopower', 'technofirst', 'oceasoft', 'horizontal-software', 'sorbet-amour',
                        'hotelim', 'proventure-gold', 'simat', 'metalliance', 'hotel-majestic-cannes', 'atv',
                        'silkan-rt', 'global-health-group', 'altran', 'ingenico', 'baccarat', 'intexa', 'stentys',
                        'april', 'sequana', 'blue-solutions', 'ymagis', 'quotium-technologies', 'cellnovo',
                        'orchestra-premaman', 'mediawan', 'antalis-international', 'financiere-ouest-africain',
                        'fonciere-verte', 'agta-record', 'brasserie-cameroun', 'lafuma', 'electricite-madagascar',
                        'siph', 'toupargel', 'gemalto', 'sodifrance', 'medasys', 'spir', 'officiis-properties',
                        'terreis', 'le-belier', 'its-group', 'recylex', 'mainstay-medical-international']
SERVER = 'http://192.168.59.128:8000'
GOOGLE = 'http://google.com/search?q='
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
HEADERS = {"user-agent": USER_AGENT}
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
N_COMPANIES = 0
N_SKIP = 0
N_TICKERS = 0
N_NULL = 0
N_UPDATES = 0
N_CREATIONS = 0
N_NO_UP = 0
N_NO_200 = 0


def extract_data(content, isYahoo=False):
    if content is None:
        return '#', 'N/A'

    soup = BeautifulSoup(content, "html.parser")
    limit = 5
    for g in soup.find_all('div', class_='g'):
        # anchor div
        rc = g.find('div', class_='rc')
        # description div: s = g.find('div', class_='s')
        if rc:
            divs = rc.find_all('div', recursive=False)
            if len(divs) >= 2:
                anchor = divs[0].find('a')
                link = anchor['href']
                if isYahoo:
                    title = anchor.find('h3').text
                    title_search = re.search(' \((.*)\) ', title)
                    if title_search:
                        quote = title_search.group(1)
                        return link, quote
                    else:
                        limit -= 1
                        if limit == 0:
                            break
                else:
                    return link, 'N/A'
    return '#', 'N/A'


def query_web(web, company_name):
    query = f"{web}-{company_name}"
    query = query.replace('-', '+')

    resp = requests.get(f"{GOOGLE}{query}", headers=HEADERS)
    if resp.status_code == 200:
        return resp.content
    else:
        logger.error(f"Query_web {company_name}: (Error on {web} [{resp.status_code}])")
    return None


def get_ticker(company_name):
    resp = requests.get(f"{SERVER}/get_pk/ticker/{company_name}/")

    # Ticker exist
    if resp.status_code == 200:
        ticker_pk = resp.json().get('pk')
        resp = requests.get(f"{SERVER}/api/tickers/{ticker_pk}/?format=json")

        if resp.status_code == 200:
            return resp.json()
        else:
            logger.error(f"Get_ticker {company_name}: (Error on api/tickers [{resp.status_code}])")
    else:
        logger.error(f"Get_ticker {company_name}: (Error on get_pk/ticker [{resp.status_code}])")

    # Ticker doesn't exist, search company to create it
    resp = requests.get(f"{SERVER}/get_pk/company/{company_name}")

    if resp.status_code == 200:
        company_pk = resp.json().get('pk')

        js = {
            "name": company_name,
            "zb": "N/A",
            "yf": "N/A",
            "inv": "N/A",
            "zb_link": "#",
            "yf_link": "#",
            "inv_link": "#",
            "company_fk": int(company_pk)
        }
        return js
    else:
        logger.error(f"Get_ticker {company_name}: (Error on get_pk/company [{resp.status_code}])")

    # Ticker Error
    return None


def send_to_api(js):
    global N_UPDATES, N_CREATIONS
    if js.get('url'):
        # update
        url = js.get('url').replace('?format=json', '')
        r = requests.put(url, json=js)
        N_UPDATES += 1
        return r.status_code
    else:
        # creation
        url = f"{SERVER}/api/tickers/"
        r = requests.post(url, json=js)
        N_CREATIONS += 1
        return r.status_code


class Worker(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        global N_TICKERS, N_NULL, N_NO_UP, N_NO_200

        while True:
            # Get the work from the queue and expand the tuple
            company_name = self.queue.get()
            try:
                zb = query_web('zonebourse', company_name)
                yf = query_web('yahoo-finance', company_name)
                inv = query_web('investir', company_name)

                zb_link, _ = extract_data(zb)
                yf_link, yf_quote = extract_data(yf, isYahoo=True)
                inv_link, _ = extract_data(inv)

                ticker = get_ticker(company_name)
                if ticker is not None:
                    N_TICKERS += 1
                    needUpdate = False

                    if ticker['zb_link'] == '#' and zb_link != '#':
                        needUpdate = True
                        ticker['zb_link'] = zb_link
                    if ticker['yf_link'] == '#' and yf_link != '#':
                        needUpdate = True
                        ticker['yf_link'] = yf_link
                    if ticker['inv_link'] == '#' and inv_link != '#':
                        needUpdate = True
                        ticker['inv_link'] = inv_link
                    if ticker['yf'] == 'N/A' and yf_quote != 'N/A':
                        needUpdate = True
                        ticker['yf'] = yf_quote

                    if needUpdate:
                        status_code = send_to_api(ticker)
                    else:
                        N_NO_UP = N_NO_UP + 1
                        status_code = 222

                    if status_code < 200 or status_code > 299:
                        N_NO_200 += 1

                    logger.info(f"End {company_name}: (Debug = {status_code})")
                else:
                    N_NULL += 1
                    logger.error(f"End {company_name}: (Error on Ticker)")
            finally:
                self.queue.task_done()


def scrape():
    global N_COMPANIES, N_SKIP, N_TICKERS, N_NULL, N_UPDATES, N_CREATIONS, N_NO_UP, N_NO_200

    ts = time.time()

    r = requests.get(f"{SERVER}/api/companies/?format=json")
    if r.status_code != 200:
        logger.error('Webtrade request error...')
        exit(-1)

    # Create a queue to communicate with the worker threads
    queue = Queue()

    # Create 8 worker threads
    for x in range(8):
        worker = Worker(queue)
        # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()

    # Put the tasks into the queue as a tuple
    for company in r.json():
        company_name = company['name']
        if company_name in skip_companies:
            logger.info(f"Skipping {company_name}")
            N_SKIP += 1
        else:
            logger.info(f"Queueing {company_name}")
            N_COMPANIES += 1
            queue.put(company_name)

    # Causes the main thread to wait for the queue to finish processing all the tasks
    queue.join()
    logger.info('Took %s', time.time() - ts)
    logger.info('KPI :')
    logger.info(f"\tCOMPANIES:\t{N_COMPANIES}")
    logger.info(f"\t SKIP:\t\t{N_SKIP}")
    logger.info(f"\tTICKERS:\t{N_TICKERS}")
    logger.info(f"\t NULL:\t\t{N_NULL}")
    logger.info(f"\t UPDATES:\t{N_UPDATES}")
    logger.info(f"\t CREATIONS:\t{N_CREATIONS}")
    logger.info(f"\t NO_UP:\t\t{N_NO_UP}")
    logger.info(f"\t NO_200:\t{N_NO_200}")


if __name__ == '__main__':
    scrape()
