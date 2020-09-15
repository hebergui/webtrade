from lxml import html
import requests
import unicodedata

url = 'https://screener.blogbourse.net/societes.html'
page = requests.get(url)
tree = html.fromstring(page.content)

tab1 = tree.xpath('(//table)[1]//td//text()')
#[name, indice]
companies = [tab1[x+1:x+3] for x in range(0, len(tab1), 3)]

url = 'https://screener.blogbourse.net/'
tab2 = tree.xpath('(//table)[1]//td//@href')
#[name, indice, ref]
companies = [companies[x]+[str(tab2[x])] for x in range(0, len(tab2))]

for i in range(0, len(companies):
    url = 'https://screener.blogbourse.net/' + companies[i][2]
    page = requests.get(url)
    tree = html.fromstring(page.content)
    sector = tree.xpath('/html/body/div/div/main/div[4]/ul/li[4]/a/text()')[0]
    force = float(tree.xpath('/html/body/div/div/main/div[4]/ul/li[5]/text()')[0].split(' : ')[1])
    phase, pub_date = tree.xpath('/html/body/div/div/main/div[4]/ul/li[6]/text()')[0].split(': ')[1].split(' (')
    pub_date = pub_date[:-1]

    companies[i] = companies[i] + [pub_date, sector, force, phase]

#[name, indice, ref, pub_date, sector, force, phase]
