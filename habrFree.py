import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

URL = 'https://freelance.habr.com/tasks'

headers = {
    'Host': 'freelance.habr.com',
    'User-Agent': 'Safari',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive'
}

def find_max_pages():
    habr_req = requests.get(URL, headers=headers)
    habr_soup = BeautifulSoup(habr_req.text, 'html.parser')
    pagination = habr_soup.find("div", {'id': 'pagination'})

    if pagination:
        page_links = pagination.find_all('a')
        page_numbers = [link.text for link in page_links if link.get('href') and 'page' in link.get('href')]
        max_page_number = max([int(number) for number in page_numbers if number.isdigit()])
        return max_page_number
    else:
        return "Pagination not found!"

def extract_data_from_html(html_content):
    result = []
    soup = BeautifulSoup(html_content, 'html.parser')

    titles = soup.find_all('div', {'class': 'task__title'})
    for title in titles:
        title_text = title.find('a').text
        link = title.find('a')['href']

        count_block = title.find_next('div', {'class': 'task__price'})
        count_spans = count_block.find_all('span', {'class': ['count', 'negotiated_price']})
        count_list = [span.text for span in count_spans]

        for count_text in count_list:
            result.append({'title': title_text, 'price': count_text, 'link': f'https://freelance.habr.com/{link}'})

    return result

def extract_data_from_page(page, keyword):
    result = []
    response = requests.get(URL, headers=headers, params={'page': page, 'q': keyword})
    html_content = response.text
    data = extract_data_from_html(html_content)
    result += data
    return result

def print_data_as_dict(last_page, keyword):
    result = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(extract_data_from_page, page, keyword) for page in range(last_page)]
        for future in futures:
            result += future.result()
    return result