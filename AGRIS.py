import os

from DB import DB
import requests
from bs4 import BeautifulSoup
import re
from CrawlerStatus import CrawlerStatus
from Crawler import Crawler
import time
from dotenv import load_dotenv


class Agris:
    AGRIS_BASE_URL = "https://agris.fao.org"
    LIST_ENDPOINT = "https://agris.fao.org/search/en?fields={%22abstract%22%3A[%22SEARCH_TERM%22]}&filters={%22languages%22%3A[{%22operator%22%3A%22all%22%2C%22values%22%3A[%22eng%22]}]}&range={%22start%22%3A%222023%22%2C%22end%22%3A%222024%22}&size=SEARCH_LIMIT"
    crawler = None
    CRAWLER_DELAY = 1
    CRAWLER_STEPPER = 1

    def __init__(self):
        load_dotenv()
        self.CRAWLER_DELAY = float(os.getenv("CRAWLER_DELAY", 1.5))
        self.CRAWLER_STEPPER = int(os.getenv("CRAWLER_STEPPER", 1))

    def fetchAbstracts(self, limit:int|None = None):
        limit = limit if limit else self.CRAWLER_STEPPER

        crawler = Crawler()

        for record in crawler.fetch_by_status(CrawlerStatus.PENDING.value,limit):
            crawler.set_status(record['_id'], CrawlerStatus.IN_PROGRESS.value)
            abstract_record = self.crawl(record)
            if abstract_record:
                crawler.save_abstract(abstract_record)
                crawler.set_status(record['_id'], CrawlerStatus.COMPLETED.value)
            else:
                crawler.set_status(record['_id'], CrawlerStatus.FAILED.value)
            self.wait()
        else:
            print('I have no more records to fetch! :)')

        crawler.close()

    def crawl(self, record):
        print(f"Fetching data from: {record['link']}")
        # Fetch the record
        response = requests.get(record['link'])
        if response.status_code != 200:
            print(f"Failed to fetch data: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'lxml')

        authors = [author['content'] for author in soup.find_all('meta', attrs={'name': 'citation_author'})]

        keywords = []
        tags_div = soup.find('div', attrs={'class': 'tags-list'})
        if tags_div:
            for keyword in tags_div.find_all('a', attrs={'class': 'badge'}):
                # Append the text content of each keyword to the keywords list
                keywords.append(keyword.get_text().strip())
        else:
            print("No tags found.")

        title = soup.find('meta', attrs={'name': 'citation_title'})
        pub_date = soup.find('meta', attrs={'name': 'citation_publication_date'})
        abstract_div = soup.find('div', attrs={'class': 'abstract'})

        abstract = {
            'title': title['content'] if title else None,
            'pub_date': pub_date['content'] if pub_date else None,
            'authors': authors,
            'keywords': keywords,
            'abstract': {
                'text': abstract_div.get_text() if abstract_div else None,
                'html': str(abstract_div) if abstract_div else None,
                'clean': self.text_clean(abstract_div.get_text(strip=True)) if abstract_div else None
            },
            'link': record['link'],
            'full_htnl': str(soup),
            'crawler_id': record['_id'],
            'created_at': time.time(),
        }

        print(abstract)
        return abstract

    def fetchTermAbstracts(self, term: str):
        links = self.fetchRecordLinks(term)

        data = []
        chunk_size = 100  # Define chunk size, adjust this number based on your needs
        crawler = Crawler()

        for index, link in enumerate(links):
            data.append({
                "link": link,
                "term": term,
                "status": CrawlerStatus.PENDING.value,
                "created_at": time.time(),
                "updated_at": time.time(),
            })

            # When the chunk is filled or it's the last element, insert the chunk
            if (index + 1) % chunk_size == 0 or index + 1 == len(links):
                crawler.queue(data)
                data = []  # Reset the data list for the next chunk

        crawler.close()
        return links

    def fetchRecordLinks(self, term: str, limit: str = "50"):
        links = []  # Store all the links across pages
        url = self.LIST_ENDPOINT.replace("SEARCH_TERM", term)
        url = url.replace("SEARCH_LIMIT", limit)
        print(f"[fetchRecordLinks] Fetching data from: {url}")
        while url:  # Continue as long as there is a URL to process
            try:
                print('[{term}] Fetching data from:'.format(term=term), url)
                # Fetch the data from the endpoint
                response = requests.get(url)
                if response.status_code != 200:
                    print(f"Failed to fetch data: {response.status_code}")
                    break  # Exit the loop if there's a bad response

                print('Data fetched successfully. Trying to parse.....')
                bsoup = BeautifulSoup(response.text, 'html.parser')

                # Extract links from the current page
                regex = re.compile(r'/search/en/records/\w+')
                results = bsoup.find_all('div', attrs={'class': 'dynamic-list'})
                for result in results:
                    for link in result.find_all('a', href=True):
                        if regex.match(link['href']):
                            links.append(self.AGRIS_BASE_URL + link['href'])

                # Find the next page link
                next_page = bsoup.find('a', attrs={'class': 'page-link', 'aria-label': 'Next'})
                url = next_page.get('href') if next_page and next_page.get('href') else None

                print(f"Next page: {url}")

                if url and not url.startswith("http"):
                    url = self.AGRIS_BASE_URL + url  # Ensure the URL is complete

                # Delay the next request
                self.wait()

            except requests.RequestException as e:
                print(f"Request failed: {e}")
                break  # Exit the loop on request failure

            except Exception as e:
                print(f"An error occurred: {e}")
                break  # Handle other possible exceptions

        print(f"Found {len(links)} links")
        return links

    def text_clean(self, text: str):
        return text.replace('\n', '').strip()

    def wait(self):
        print(f"Waiting for {self.CRAWLER_DELAY} seconds")
        time.sleep(self.CRAWLER_DELAY)