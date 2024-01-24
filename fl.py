import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

URL_FL = 'https://www.fl.ru/search/?type=projects&action=search&search_string=верстка'

headers = {
    'Host': 'www.fl.ru',
    'User-Agent': 'Safari',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive'
}

def find_max_pages_fl():
    req = requests.get(URL_FL, headers=headers)
    soup = BeautifulSoup(req.text, 'html.parser')
    pages = soup.find("div", {'class': 'b-pager'}).find_all('a')

    if pages:
        page_numbers = [link.text for link in pages if link.get('href') and 'page' in link.get('href')]
        max_page_number = max([int(number) for number in page_numbers if number.isdigit()])
        return max_page_number
    else:
        return "Pagination not found!"

def extract_data_from_html_fl(html_content):
    result = []
    soup = BeautifulSoup(html_content, 'html.parser')

    search_items = soup.find_all('div', {'class': 'search-lenta-item c'})

    for item in search_items:
        title_div = item.find('div', {'class': 'search-item-body has_sbr'})
        if title_div:
            title = title_div.find('h3').find('a')
            title_text = title.text.strip() if title else 'Title not available'
            link = title['href'] if title else 'Link not available'
        else:
            title_text = 'Title not available'
            link = 'Link not available'

        price_span = item.find('span', {'class': ['search-price', 'bujet-dogovor']})
        price_text = price_span.text.strip().replace('\xa0', ' ') if price_span else 'Price not available'

        result.append({
            'title': title_text,
            'link': f'https://www.fl.ru/{link}',
            'price': price_text
        })

    return result

def extract_data_from_page_fl(page, keyword):
    result = []
    response = requests.get(f'{URL_FL}&search_string={keyword}&page={page}', headers=headers)
    html_content = response.text
    data = extract_data_from_html_fl(html_content)
    result.extend(data)
    return result

def print_data_as_dict_fl(last_page, keyword):
    result = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(extract_data_from_page_fl, page, keyword) for page in range(last_page)]
        for future in futures:
            result.extend(future.result())
    return result