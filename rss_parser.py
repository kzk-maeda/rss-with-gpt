from typing import List, Tuple
import feedparser
from datetime import datetime, date

EntryData = Tuple[str, str, str]

class RSS:
    """
    A class for parsing and extracting data from an RSS feed.
    """
    def __init__(self, rss_url: str):
        """
        Initialize the RSS class with a URL of the RSS feed.
        :param rss_url: The URL of the RSS feed to parse.
        """
        self.rss_url = rss_url
        self.feed = feedparser.parse(self.rss_url)

    def extract(self, target_date: date) -> List[EntryData]:
        """
        Extract entries with a specified published date from the RSS feed.
        :param target_date: The target date for filtering entries.
        :return: A list of tuples containing the title, URL, and published date of matching entries.
        """
        matching_entries = []

        for entry in self.feed.entries:
            published_date = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z').date()
            if published_date == target_date:
                matching_entries.append((entry.title, entry.link, entry.published))

        return matching_entries

    def parse_all(self) -> List[EntryData]:
        """
        Parse all entries from the RSS feed.
        :return: A list of tuples containing the title, URL, and published date of all entries.
        """
        all_entries = []

        for entry in self.feed.entries:
            all_entries.append((entry.title, entry.link, entry.published))

        return all_entries


