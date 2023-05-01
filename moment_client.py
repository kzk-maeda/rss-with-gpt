from dotenv import load_dotenv
from typing import Optional

from datetime import timedelta

from momento import CacheClient, Configurations, CredentialProvider
from momento.responses import CacheGet, CacheSet, CreateCache, ListCaches
from momento.responses.control.cache.list import CacheInfo

load_dotenv()

MOMENTO_TTL_SECONDS=3600

class MomentClient:
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
    
    def is_item_present(self, key: str) -> bool:
        with self._client() as cache_client:
            get_response = cache_client.get(self.cache_name, key)
            match get_response:
                case CacheGet.Hit() as hit:
                    return True
                case CacheGet.Miss():
                    return False
                case CacheGet.Error() as error:
                    raise error.inner_exception
        return False

    def get_item(self, key: str) -> Optional[str]:
        with self._client() as cache_client:
            get_response = cache_client.get(self.cache_name, key)
            match get_response:
                case CacheGet.Hit() as hit:
                    print(f"Look up resulted in a hit: {hit}")
                    print(f"Looked up Value: {hit.value_string!r}")
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
    
    def delete_item(self, key: str) -> None:
        pass

