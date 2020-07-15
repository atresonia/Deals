import csv
import sys
import requests
import logging
import pprint
import concurrent.futures
import traceback
import json

from typing import Dict, List
from urllib.parse import urljoin, urlparse
from timeit import default_timer as timer
from html_similarity import similarity

# TSV file format: url\tdescritpion (first line: header)
# the input TSV (tab-separated values) file with format: url\tdescription
DEALS_INPUT_FILE = "pammcduc_deals.tsv"

# Output file(JSON format)
DEALS_OUTPUT_FILE = "depersonalized_deals.json"

# maximum number of deals read from input file
MAX_DEALS = 200
# maximum number of worker threads created to process deals
MAX_WORKERS = 40

# HTML document similarity score is a value between 0.0 and 1.0, inclusive
SIMILARITY_THRESHOLD = 0.7

# HTTP request timeout in seconds (makes sure code doesn't hang)
HTTP_TIMEOUT_SEC = 10

# headers used to mimic a Chrome browser
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/83.0.4103.97 Safari/537.36"}

Deal = Dict[str, str]


def load_deals(deals_file: str) -> List[Deal]:
    with open(deals_file) as file:
        result = [{k: str(v) for k, v in row.items()}
                  for row in csv.DictReader(file.readlines()[0:MAX_DEALS + 1], skipinitialspace=True, delimiter="\t")]
        # +1 for extra header line
    return result


def redirected_link(url: str) -> str:
    newURL = url

    while True:
        response = requests.get(newURL, timeout=HTTP_TIMEOUT_SEC, headers=HEADERS, allow_redirects=False)
        # Raise an HTTPError for certain status codes
        response.raise_for_status()

        if response.status_code == 301 or response.status_code == 302:
            newURL = response.headers.get("Location")
        else:
            break

    return newURL


def remove_query_string(url: str) -> str:
    return urljoin(url, urlparse(url).path)


def get_body(url: str) -> str:
    response = requests.get(url, timeout=HTTP_TIMEOUT_SEC, headers=HEADERS)

    if response.status_code != 200:
        raise Exception(f"ERROR: Got {response.status_code} for {url}")
    return response.text


def get_similarity(url1: str, url2: str) -> int:
    r1 = get_body(url1)
    r2 = get_body(url2)
    return similarity(r1, r2)


def process_deal(deal: Deal) -> None:
    logging.info(f"Processing deal {deal['description']}")
    try:
        final_link = redirected_link(deal["url"])
        stripped_link = remove_query_string(final_link)
        similarity_score = get_similarity(final_link, stripped_link)
        out_deal = {"description": deal["description"], "url": deal["url"], "similarity_score": similarity_score}
        if similarity_score > SIMILARITY_THRESHOLD:
            out_deal["url_new"] = stripped_link
        else:
            out_deal["url_new"] = None
        out_deals.append(out_deal)

    except Exception as e:
        logging.error(e)
        traceback.print_exc(file=sys.stdout)
        out_deals.append({"url_new": None, "description": deal["description"], "url": deal["url"], "similarity_score": 0.0})


def process_deals() -> None:
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(process_deal, deals)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, format="[%(threadName)s] %(levelname)s - %(message)s", level=logging.INFO)
    pp = pprint.PrettyPrinter(indent=2)
    deals: List[Deal] = load_deals(DEALS_INPUT_FILE)
    start_time = timer()
    out_deals: List[Deal] = []
    process_deals()
    elapsed_time_ms = round(1000 * (timer() - start_time))
    count_success = 0
    for the_deal in out_deals:
        if the_deal["url_new"] is not None:
            count_success += 1
    print(f"{count_success} out of {len(out_deals)} deals succeeded")
    # pp.pprint(out_deals)
    with open(DEALS_OUTPUT_FILE, "w", encoding='utf-8') as outfile:
        json.dump(out_deals, outfile, ensure_ascii=False, indent=4)
    logging.info(f"Elapsed time: {elapsed_time_ms} msec")
