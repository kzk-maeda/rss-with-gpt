from dotenv import load_dotenv
from typing import Optional

from datetime import timedelta

from momento import CacheClient, Configurations, CredentialProvider
from momento.responses import CacheGet, CacheSet, CreateCache, ListCaches, CacheDictionarySetFields, CacheListPushBack, CacheListFetch
from momento.responses.control.cache.list import CacheInfo

load_dotenv()

MOMENTO_TTL_SECONDS=60*60*24

class MomentoClient:
    def __init__(self, cache_name: str, token: str):
        self.cache_name = cache_name
        self.token = token
        self.auth = CredentialProvider.from_string(self.token)

    def _client(self) -> CacheClient:
        cache_client = CacheClient(
            configuration=Configurations.Laptop.v1(),
            credential_provider=CredentialProvider.from_string(self.token),
            default_ttl=timedelta(seconds=MOMENTO_TTL_SECONDS),
        )
        return cache_client
    
    def create_cache(self, cache_name: str) -> None:
        with self._client() as cache_client:
            create_cache_response = cache_client.create_cache(cache_name)
            match create_cache_response:
                case CreateCache.CacheAlreadyExists():
                    print(f"Cache with name: {cache_name} already exists.")
                case CreateCache.Error() as error:
                    raise error.inner_exception

    def list_caches(self) -> Optional[list[CacheInfo]]:
        with self._client() as cache_client:
            list_caches_response = cache_client.list_caches()
            match list_caches_response:
                case ListCaches.Success() as success:
                    for cache_info in success.caches:
                        print(f"- {cache_info.name!r}")
                case ListCaches.Error() as error:
                    raise error.inner_exception

    # string type cache item
    def get_item(self, key: str) -> Optional[str]:
        with self._client() as cache_client:
            get_response = cache_client.get(self.cache_name, key)
            match get_response:
                case CacheGet.Hit() as hit:
                    print(f"Look up resulted in a hit: {hit}")
                    return hit.value_string
                case CacheGet.Miss():
                    print("Look up resulted in a: miss. This is unexpected.")
                case CacheGet.Error() as error:
                    raise error.inner_exception

    def set_item(self, key: str, value: str | bytes) -> None:
        with self._client() as cache_client:
            set_response = cache_client.set(self.cache_name, key, value)
            match set_response:
                case CacheSet.Error() as error:
                    raise error.inner_exception
    
    # dict type cache item
    def set_dict_item(self, key: str, dict_value: dict[str, str]) -> None:
        with self._client() as cache_client:
            set_response = cache_client.dictionary_set_fields(self.cache_name, key, dict_value)
            match set_response:
                case CacheDictionarySetFields.Error() as error:
                    raise error.inner_exception
    
    # list type cache item
    def push_list_item(self, key: str, item: str) -> None:
        with self._client() as cache_client:
            set_response = cache_client.list_push_back(self.cache_name, key, item)
            match set_response:
                case CacheListPushBack.Error() as error:
                    raise error.inner_exception
    
    def fetch_list_item(self, key: str) -> list[str]:
        with self._client() as cache_client:
            get_response = cache_client.list_fetch(self.cache_name, key)
            match get_response:
                case CacheListFetch.Hit() as hit:
                    return hit.value_list_string
                case CacheListFetch.Miss():
                    print("Look up resulted in a: miss. This is unexpected.")
                    raise
                case CacheListFetch.Error() as error:
                    raise error.inner_exception
        return []
    
    def is_item_present(self, key: str) -> bool:
        with self._client() as cache_client:
            get_response = cache_client.list_fetch(self.cache_name, key)
            match get_response:
                case CacheListFetch.Hit() as hit:
                    return True
                case CacheListFetch.Miss():
                    return False
                case CacheListFetch.Error() as error:
                    raise error.inner_exception
        return False
    
    def delete_item(self, key: str) -> None:
        pass

