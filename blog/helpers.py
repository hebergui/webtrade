import httpx
from lxml import html
from datetime import date

# API = "http://35.224.98.28:8000"
# API = "http://0.0.0.0:8000"
API = "http://futrax.fr:8000"


def get_companies(url):
    r = httpx.get(url)
    tree = html.fromstring(r.text)

    # format : [id, name, indice, id, name, indice...]
    tab1 = tree.xpath('(//table)[1]//td//text()')
    # format : [[name, indice], [name, indice], ...]
    companies = [tab1[x + 1:x + 3] for x in range(0, len(tab1), 3)]

    # format : [ref, ref, ...]
    tab2 = tree.xpath('(//table)[1]//td//@href')

    # format : [[name, indice, ref], ...]
    companies = [companies[x] + [str(tab2[x])] for x in range(0, len(tab2))]

    return companies


def get_pk(name):
    r = httpx.get(API + '/get_pk/company/' + name)
    if r.status_code == 200:
        return r.json().get('pk')
    else:
        return None


def download_data(name, indice, ref, url_ref):
    cur_date = date.today().strftime("%Y-%m-%d")
    data = {
        'ut': 'w',
        'debut': '2019-09-18',
        'fin': cur_date,
        'chandelier': 'on',
        'mm': 'on',
        'vol': 'on',
        'forceRel': 'on',
        'maj': ''
    }
    response = httpx.post(url_ref + ref, data=data, timeout=None)

    # Parsing part
    try:
        txt = response.text

        # dict format : db["pub_date"] = [pub_date, force, cmin, cmax, copen, cclose, mm30, phase]
        histo = {}

        # Parse post response
        chart1 = txt.split("'Force Relative'],\n")[1].split(');')[0]
        data_chart1 = eval('[' + chart1)
        for pub_date, force in data_chart1:
            histo[pub_date] = [pub_date, force]

        chart2 = txt.split('var dataC = google.visualization.arrayToDataTable(')[1].split('\n')[0].split(', true')[0]
        data_chart2 = eval(chart2)

        for pub_date, cmin, copen, cclose, cmax, mm30 in data_chart2:
            if pub_date not in histo:
                histo[pub_date] = []
            histo[pub_date] += [cmin, cmax, copen, cclose, mm30, 'N/C']

        tree = html.fromstring(txt)

        pub_date = 'N/C'
        # tmp = tree.xpath('/html/body/div/div/main/div[4]/ul/li[2]/text()')[0]
        tmp = tree.xpath('/html/body/div/div/main/div[5]/ul/li[2]/text()')[0]
        if tmp.find('Cours') != -1:
            pub_date = tmp.split('  au ')[1].split(' : ')[0]
            # 11/09/2020 to 11/09/20
            pub_date = pub_date[0:6] + pub_date[-2:]

        # sector = tree.xpath('/html/body/div/div/main/div[4]/ul/li[4]/a/text()')
        sector = tree.xpath('/html/body/div/div/main/div[5]/ul/li[4]/a/text()')
        if len(sector) == 0:
            # sector = tree.xpath('/html/body/div/div/main/div[4]/ul/li[4]/em/text()')
            sector = tree.xpath('/html/body/div/div/main/div[5]/ul/li[4]/em/text()')
        sector = sector[0]

        # should be the same in histo
        # force = float(tree.xpath('/html/body/div/div/main/div[4]/ul/li[5]/text()')[0].split(' : ')[1])

        phase = 'N/C'
        # tmp = tree.xpath('/html/body/div/div/main/div[4]/ul/li[6]/text()')[0]
        tmp = tree.xpath('/html/body/div/div/main/div[5]/ul/li[6]/text()')[0]
        if tmp.find('Phase') != -1:
            phase = tmp.split(' : ')[1].split(' (')[0]

        if pub_date in histo:
            histo[pub_date][len(histo[pub_date]) - 1] = phase

    except ValueError as err:
        return name, err

    # Check if company exists in db
    pk = get_pk(name)
    if pk is None:
        # Create company
        js = {
            "name": name,
            "ref": ref,
            "indice": indice,
            "sector": sector,
        }
        r = httpx.post(API + '/api/companies/', json=js)
        if r.status_code == 201:
            pk = get_pk(name)
        else:
            return name, r.content

    count = 0
    ok = 0
    # Create all indicators related to company
    for k, v in histo.items():
        count += 1
        pub_date, force, cmin, cmax, copen, cclose, mm30, phase = v
        js = {
            'pub_date': pub_date,
            'force': force,
            'cmin': cmin,
            'cmax': cmax,
            'copen': copen,
            'cclose': cclose,
            'mm30': mm30,
            'phase': phase,
            'company': pk
        }
        # Send to api
        r = httpx.post(API + '/api/indicators/', json=js)
        if r.status_code == 201:
            ok += 1

    return name, '{}/{}'.format(ok, count)
