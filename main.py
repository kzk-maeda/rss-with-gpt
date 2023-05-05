import os
import sys
import uuid
from dotenv import load_dotenv
from datetime import datetime, date, timedelta
from contextlib import contextmanager

from openai_client import OpenAIClient
from momento_client import MomentoClient
from rss_parser import RSS

CHUNK_SIZE = 2

@contextmanager
def suppress_stdout():
    original_stdout = sys.stdout
    with open(os.devnull, 'w') as devnull:
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = original_stdout


def get_aws_update() -> list[str]:
    rss = RSS("https://aws.amazon.com/about-aws/whats-new/recent/feed/")
    target_date = date.today() - timedelta(days=1)
    matching_entries = rss.extract(target_date)

    urls = []
    for title, url, published_date in matching_entries:
        urls.append(url)
        print(f"Title: {title}")
        print(f"  Published Date: {published_date}")
        print("-------------------------------")
    
    return urls


def divide_urls_into_chunks(urls: list, chunk_size: int) -> list:
    chunks = []
    for i in range(0, len(urls), chunk_size):
        chunks.append(urls[i:i + chunk_size])
    return chunks


def main():
    load_dotenv()

    urls = get_aws_update()
    cache_name = "aws-update-index"
    token = os.getenv("MOMENTO_AUTH_TOKEN", "")

    openpi_client = OpenAIClient()
    momento_client = MomentoClient(cache_name, token)
    momento_client.create_cache(cache_name)

    date_str = datetime.now().strftime("%Y-%m-%d")
    index_key = f"index-{date_str}"
    index_master_key = f"index-{date_str}"
    print(index_key)

    if not momento_client.is_item_present(index_master_key):
        print("Creating index...")
        chunked_urls = divide_urls_into_chunks(urls, CHUNK_SIZE)
        for chunk in chunked_urls:
            index_str = openpi_client.create_index_from_urls(chunk)
            chunk_key = uuid.uuid4().hex
            # momento_client.set_dict_item(chunk_key, json.loads(index_str))
            momento_client.set_item(chunk_key, index_str)
            momento_client.push_list_item(index_master_key, chunk_key)
    else:
        print(f"Index {index_key} already exists in momento.")

    # get index list
    index_list = momento_client.fetch_list_item(index_master_key)
    for index in index_list:
        print(f"index_key: {index}")

    # with suppress_stdout():
    #     index_str = momento_client.get_item(index_key) or ""
    # query_string = "tell me the summary of yesterday AWS update."
    # print(f"Q: \n{query_string}")
    # with suppress_stdout():
    #     answer = openpi_client.query(query_string, index_str)
    # print(f"A: {answer}")


if __name__ == "__main__":
    main()
