import httpx
import asyncio

from lxml import html

async def pull_async():
    #url = 'https://screener.blogbourse.net/societes.html'
    #r = httpx.get(url)
    tree = html.fromstring(r.text)

    # format : [id, name, indice, id, name, indice...]
    tab1 = tree.xpath('(//table)[1]//td//text()')
    # format : [[name, indice], [name, indice], ...]
    companies = [tab1[x + 1:x + 3] for x in range(0, len(tab1), 3)]

    # format : [ref, ref, ...]
    tab2 = tree.xpath('(//table)[1]//td//@href')

    # format : [[name, indice, ref], ...]
    companies = [companies[x] + [str(tab2[x])] for x in range(0, len(tab2))]

    url = "https://screener.blogbourse.net/"
     "companies = [['total', 'cac40', 'cours-total.html'], ['safran', 'cac40', 'cours-safran.html']]

    for name, indice, ref in companies:
        client = httpx.AsyncClient()
        response = await asyncio.gather(*[client.get(url + ref)])

        try:
            tree = html.fromstring(response[0].text)
            sector = tree.xpath('/html/body/div/div/main/div[4]/ul/li[4]/a/text()')
            if len(sector) == 0:
                sector = tree.xpath('/html/body/div/div/main/div[4]/ul/li[4]/em/text()')
            sector = sector[0]
            force = float(tree.xpath('/html/body/div/div/main/div[4]/ul/li[5]/text()')[0].split(' : ')[1])
            phase, pub_date = tree.xpath('/html/body/div/div/main/div[4]/ul/li[6]/text()')[0].split(': ')[1].split(' (')
            pub_date = pub_date[:-1]
        except ValueError as err:
            print("ValueError for :", name, err)
            continue

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

        responses = await asyncio.gather(*[client.post('http://127.0.0.1:8000/api/companies/', json=js)])

        for r in responses:
            print(name, ' : ', r.status_code)


if __name__ == "__main__":
    asyncio.run(pull_async())