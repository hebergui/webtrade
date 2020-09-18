import httpx

from lxml import html

API = "http://35.224.98.28:8000"


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


def download_data(name, indice, ref, url_ref):
    response = httpx.get(url_ref + ref)

    try:
        tree = html.fromstring(response.text)

        pub_date = 'N/C'
        tmp = tree.xpath('/html/body/div/div/main/div[4]/ul/li[2]/text()')[0]
        if tmp.find('Cours') != -1:
            pub_date = tmp.split('  au ')[1].split(' : ')[0]

        sector = tree.xpath('/html/body/div/div/main/div[4]/ul/li[4]/a/text()')
        if len(sector) == 0:
            sector = tree.xpath('/html/body/div/div/main/div[4]/ul/li[4]/em/text()')
        sector = sector[0]

        force = float(tree.xpath('/html/body/div/div/main/div[4]/ul/li[5]/text()')[0].split(' : ')[1])

        phase = 'N/C'
        tmp = tree.xpath('/html/body/div/div/main/div[4]/ul/li[6]/text()')[0]
        if tmp.find('Phase') != -1:
            phase = tmp.split(' : ')[1].split(' (')[0]
    except ValueError as err:
        return name, err

    js = {
        "name": name,
        "ref": ref,
        "indice": indice,
        "sector": sector,
        "indicators": [
            {
                "pub_date": pub_date,
                "force": force,
                "phase": phase
            }
        ]
    }

    #print(js)
    r = httpx.post(API + '/api/companies/', json=js)

    return name, r.status_code
