import logging
import time
import httpx
import os

from lxml import html
from datetime import date
from queue import Queue
from threading import Thread

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

SERVER_IP = "futrax.fr"
SERVER_PORT = 8000
if os.environ.get('DJANGO_DEVELOPMENT'):
    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 8000
API_URL = "http://{}:{}".format(SERVER_IP, SERVER_PORT)
WS_URL = "ws://{}:{}/ws/live/debug/".format(SERVER_IP, SERVER_PORT)

BLOG_URL = 'https://screener.blogbourse.net/societes.html'
BLOG_URL_REF = "https://screener.blogbourse.net/"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Company:
    def __init__(self, fullname, indice, ref, sector='N/C'):
        self.name = ref.replace('cours-','').replace('.html', '')
        self.fullname = fullname
        self.indice = indice
        self.ref = ref
        self.sector = sector

    def __str__(self):
        return self.name

    def add_sector(self, sector):
        self.sector = sector

    def to_json(self):
        return {
            "name": self.name,
            "fullname": self.fullname,
            "ref": self.ref,
            "indice": self.indice,
            "sector": self.sector,
        }


class Indicator:
    def __init__(self, company_fk, pub_date, force, cmin='0', cmax='0', copen='0', cclose='0', mm30='0', phase='N/C'):
        self.company_fk = company_fk
        self.pub_date = pub_date
        self.force = force
        self.cmin = cmin
        self.cmax = cmax
        self.copen = copen
        self.cclose = cclose
        self.mm30 = mm30
        self.phase = phase

    def __str__(self):
        return '{}-{}'.format(self.company_fk, self.pub_date)

    def add_fields(self, cmin, cmax, copen, cclose, mm30):
        self.cmin = cmin
        self.cmax = cmax
        self.copen = copen
        self.cclose = cclose
        self.mm30 = mm30

    def add_phase(self, phase):
        self.phase = phase

    def to_json(self):
        return {
            'pub_date': self.pub_date,
            'force': self.force,
            'cmin': self.cmin,
            'cmax': self.cmax,
            'copen': self.copen,
            'cclose': self.cclose,
            'mm30': self.mm30,
            'phase': self.phase,
            'company_fk': self.company_fk
        }


def get_companies(url):
    # Request website
    response = httpx.get(url)
    tree = html.fromstring(response.text)

    # format : [id, name, indice, id, name, indice...]
    tab1 = tree.xpath('(//table)[1]//td//text()')
    # format : [ref, ref, ...]
    tab2 = tree.xpath('(//table)[1]//td//@href')

    companies = []
    for ref in tab2:
        # remove id
        tab1.pop(0)
        company = Company(fullname=tab1.pop(0), indice=tab1.pop(0), ref=ref)
        companies.append(company)

    return companies


def get_pk_and_dates(name):
    # Request API
    r = httpx.get(API_URL + '/get_pk/company/' + name)
    if r.status_code == 200:
        return r.json().get('pk'), r.json().get('dates')
    else:
        return None


def get_company_data(company):
    # Check if company exists in db
    pk_in_db, pubdates_in_db = get_pk_and_dates(company.name)
    if pk_in_db is None:
        # Create company
        r = httpx.post(API_URL + '/api/companies/', json=company.to_json())
        if r.status_code == 201:
            pk_in_db, pubdates_in_db = get_pk_and_dates(company.name)
        else:
            return company, r.content

    # Request website
    js = {
        'ut': 'w',
        'debut': '2019-09-18',
        'fin': date.today().strftime("%Y-%m-%d"),
        'chandelier': 'on',
        'mm': 'on',
        'vol': 'on',
        'forceRel': 'on',
        'maj': ''
    }
    response = httpx.post(BLOG_URL_REF + company.ref, data=js, timeout=None)

    # Parsing part
    try:
        txt = response.text

        # dict format : db["pub_date"] = [pub_date, force, cmin, cmax, copen, cclose, mm30, phase]
        indicators = {}

        # Parse post response
        chart1 = txt.split("'Force Relative'],\n")[1].split(');')[0]
        data_chart1 = eval('[' + chart1)
        for pub_date, force in data_chart1:
            indicators[pub_date] = Indicator(company_fk=pk_in_db, pub_date=pub_date, force=force)

        chart2 = txt.split('var dataC = google.visualization.arrayToDataTable(')[1].split('\n')[0].split(', true')[0]
        data_chart2 = eval(chart2)

        for pub_date, cmin, copen, cclose, cmax, mm30 in data_chart2:
            indicator = indicators[pub_date]
            indicator.add_fields(cmin=cmin, cmax=cmax, copen=copen, cclose=cclose, mm30=mm30)

        tree = html.fromstring(txt)

        # Code ISIN
        isin = 'N/A'
        tmp = tree.xpath('/html/body/div/div/main/div[5]/ul/li[1]/text()')[0]
        if tmp.find('ISIN') != -1:
            isin = tmp.split(' : ')[1]

        # Cours
        # cours = tree.xpath('/html/body/div/div/main/div[5]/ul/li[2]/text()')[0]

        # Indice
        # indice = tree.xpath('/html/body/div/div/main/div[5]/ul/li[3]/text()')
        # if len(indice) == 0:
        #     indice = tree.xpath('/html/body/div/div/main/div[5]/ul/li[3]/em/text()')
        # indice = indice[0]
#
        # Sector
        sector = tree.xpath('/html/body/div/div/main/div[5]/ul/li[4]/a/text()')
        if len(sector) == 0:
            sector = tree.xpath('/html/body/div/div/main/div[5]/ul/li[4]/em/text()')
        sector = sector[0]
        company.add_sector(sector=sector)

        # Force
        # should be the same in histo
        # force = float(tree.xpath('/html/body/div/div/main/div[4]/ul/li[5]/text()')[0].split(' : ')[1])

        phase = 'N/C'
        tmp = tree.xpath('/html/body/div/div/main/div[5]/ul/li[6]/text()')[0]
        if tmp.find('Phase') != -1:
            phase = tmp.split(' : ')[1].split(' (')[0]

        # Phase written should be for last_pubdate=current_pubdat
        if len(indicators) > 0:
            last_pubdate = list(indicators.keys())[-1]
            indicator = indicators[last_pubdate]
            indicator.add_phase(phase)

    except ValueError as err:
        return company, err

    count = 0
    ok = 0
    # Create all indicators related to company
    for pub_date, indicator in indicators.items():
        # Create only if not already created
        if pub_date not in pubdates_in_db:
            count += 1
            # Send to api
            r = httpx.post(API_URL + '/api/indicators/', json=indicator.to_json())
            if r.status_code == 201:
                ok += 1

    return company, 'OK[{}] - COUNT[{}]'.format(ok, count)


class DownloadWorker(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            # Get the work from the queue and expand the tuple
            company = self.queue.get()
            try:
                name, debug = get_company_data(company)
                logger.info('End {} (Debug: {})'.format(name, debug))
            finally:
                self.queue.task_done()


def scrape():
    ts = time.time()

    companies = []
    skip = 0
    for company in get_companies(BLOG_URL):
        if company.name in skip_companies:
            logger.info('Skip {}'.format(company.name))
            skip += 1
        else:
            companies.append(company)
    
    logger.info('Companies ({}) / Blacklist ({}) / Skipped ({})'.format(len(companies), skip, len(skip_companies)))
    """
    companies = [Company("Total", "CAC 40", "cours-total.html"),
            Company("Vallourec", "N/C", "cours-vallourec.html"),
            Company("Pharmanext", "Euronext Growth", "cours-pharnext.html"),
            Company("Solutions 30 SE", "Euronext Growth", "cours-solutions-30-se.html")
        ]
    """

    # Create a queue to communicate with the worker threads
    queue = Queue()

    # Create 8 worker threads
    for x in range(8):
        worker = DownloadWorker(queue)
        # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()

    # Put the tasks into the queue as a tuple
    for company in companies:
        logger.info('Queueing {}'.format(company))
        queue.put(company)

    # Causes the main thread to wait for the queue to finish processing all the tasks
    queue.join()
    logger.info('Took %s', time.time() - ts)


if __name__ == '__main__':
    scrape()
