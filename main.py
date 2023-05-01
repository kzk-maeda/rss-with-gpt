from math import e
import os
import io
import sys
from dotenv import load_dotenv
from datetime import datetime
from contextlib import contextmanager

from openai_client import OpenAIClient
from moment_client import MomentClient

@contextmanager
def suppress_stdout():
    original_stdout = sys.stdout
    with open(os.devnull, 'w') as devnull:
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = original_stdout


def main():
    load_dotenv()

    csv_file = "urls.csv"
    cache_name = "default-cache"
    token = os.getenv("MOMENTO_AUTH_TOKEN", "")

    openpi_client = OpenAIClient()
    momento_client = MomentClient(cache_name, token)

    date_str = datetime.now().strftime("%Y-%m-%d")
    index_key = f"index-{date_str}"
    print(index_key)

    if not momento_client.is_item_present(index_key):
        print("Creating index...")
        index_str = openpi_client.create_index_from_csv(csv_file)
        momento_client.create_cache(cache_name)
        momento_client.set_item(f"index-{date_str}", index_str)
    else:
        print(f"Index {index_key} already exists in momento.")

    with suppress_stdout():
        index_str = momento_client.get_item(index_key) or ""
    query_string = "tell me the newly supported RDS instance types."
    print(f"Q: {query_string}")
    answer = openpi_client.query(query_string, index_str)
    print(f"A: {answer}")


if __name__ == "__main__":
    main()
