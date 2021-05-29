from bs4 import BeautifulSoup
from dataclasses import dataclass
import dataclasses
import requests
import pprint
from typing import List, Optional, Tuple, Set, FrozenSet
import logging

FORMAT = '%(levelname)s: %(asctime)-15s - %(message)s'
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.INFO)

@dataclass(frozen=True, eq=True)
class ItemTarget:
    item_description: str
    item_id: int
    refinement: Optional[int] = None
    item_cards: Optional[FrozenSet[int]] = None
    target_price: Optional[float] = None

@dataclass(frozen=True, eq=True)
class ItemInStore:
    item_id: int
    refinement: Optional[int]
    item_cards: FrozenSet[int]
    price: float
    store_coordinates: Optional[str] = None
    store_url: Optional[str] = None

items = [
    ItemTarget(
        item_description='botas temporais +qq coisa des',
        item_id=22008,
        refinement=None,
        item_cards=frozenset([4877]),
    ),
    ItemTarget(
        item_description='lampiao da etc com mira 1',
        item_id=19035,
        refinement=None,
        item_cards=frozenset([4832]),
    )
]

base_url = 'https://mercado.ragnahistory.com'


@dataclass(frozen=True, eq=True)
class ItemOnSale:
    title: str
    coordinates: str
    item_id: int
    price: float
    store_link: str
    currency: str

cost_by_currency = {
    'Bolsa de Rubis': 100_000_000,
    'Bolsa de Diamantes': 1_000_000_000,
    'Zeny': 1,
}

def parse_preco(preco: str) -> float:
    return float(preco[:-2].replace(' ', ''))

def parse_on_sale_html(item_id: int, html: str) -> Tuple[List[ItemOnSale], int]:
    soup = BeautifulSoup(html, features="html.parser")
    table = soup.find('table')
    if table is None:
        return [], 1
    item_rows = table.find_all('tr')[1:]
    res = []
    for tr in item_rows:
        tds = tr.find_all('td')
        titulo = tds[2].div.text.strip()
        currency = titulo.split(']')[0][1:]
        cost_multiplier = cost_by_currency[currency]

        mapa_e_coordenadas = tds[3].text.strip()
        preco = parse_preco(tds[5].text.strip())
        ver_loja = tds[7].a['href']


        res.append(ItemOnSale(title=titulo,
            coordinates=mapa_e_coordenadas,
            item_id=item_id,
            price=preco*cost_multiplier,
            store_link=ver_loja,
            currency=currency,
        ))
    pages_t = soup.find('div', {'class': 'pages'})
    if pages_t is None:
        pages = 1
    else:
        pages = len(pages_t.find_all('a'))
    return res, pages



# TODO paginate
def on_sale(item_id: int) -> Set[ItemOnSale]:
    page = 1
    r_items = set([])
    while True:
        url = f'{base_url}/?idItem={item_id}' + (f'?&p={page}' if page > 1 else '')
        log.info(f'will get page {page} on item {item_id}')
        res = requests.get(url)
        res.raise_for_status()
        items, n_pages = parse_on_sale_html(item_id, res.text)
        r_items.update(items)
        if page >= n_pages:
            return r_items
        page += 1

# TODO parse currency
def parse_in_store_html(currency: str, html: str) -> List[ItemInStore]:
    soup = BeautifulSoup(html, features="html.parser")
    item_rows = soup.find('table').find_all('tr')[1:]
    res = []
    for item_row in item_rows:
        tds = item_row.find_all('td')
        _id = int(tds[0].text.strip())
        refinamento_content = tds[3].text.strip().replace('+','')

        refinamento = 0
        try:
            refinamento = int(refinamento_content)
        except ValueError:
            pass
        cartas = []
        for n in range(1, 5):
            carta_field = tds[3 + n].a
            if carta_field is not None:
                cartas.append(int(carta_field.text.strip()))
        preco = parse_preco(tds[8].text.strip())

        res.append(
            ItemInStore(
                item_id=_id,
                refinement=refinamento,
                item_cards=frozenset(cartas),
                price=cost_by_currency[currency]*preco
            )
        )
    return res


def in_store(item: ItemOnSale) -> List[ItemInStore]:
    url = f'{base_url}{item.store_link}'
    res = requests.get(url)
    res.raise_for_status()
    rez = []
    try:
        for i in parse_in_store_html(item.currency, res.text):
            newi = dataclasses.replace(
                i,
                store_coordinates=item.coordinates,
                store_url = url
            )
            if newi.item_id == item.item_id:
                rez.append(newi)
        return rez
    except:
        print('error getting url ', url)
        raise

def matches_requirements(target: ItemTarget, item_in_store: ItemInStore) -> bool:
    has_required_cards = (
        target.item_cards is None
        or set(target.item_cards)
            .difference(
                set(item_in_store.item_cards)) == set()
    )

    matches_refinement = (
        target.refinement is None
        or target.refinement == item_in_store.refinement
    )
    return has_required_cards and matches_refinement

def scrape() -> None:
    toprint = set([])
    for target in items:
        items_on_sale = on_sale(target.item_id)
        # pprint.pprint(items_on_sale)
        for item_on_sale in items_on_sale:
            items_in_store = in_store(item_on_sale)
            for item_in_store in items_in_store:
                if matches_requirements(target, item_in_store):
                    toprint.add(item_in_store)
    pprint.pprint(sorted(list(toprint), key=lambda p: p.price))


if __name__ == '__main__':
    scrape()