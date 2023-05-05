import os
import csv
from dotenv import load_dotenv
from llama_index import GPTSimpleVectorIndex, GPTListIndex, SimpleWebPageReader
from llama_index.response.schema import RESPONSE_TYPE

class OpenAIClient():
    def __init__(self) -> None:
        load_dotenv()
        # os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY") # type: ignore

        self.openapi_org = os.environ.get("OPENAPI_ORG")
    
    def create_index_from_csv(self, file_name: str) -> str:
        article_urls = []
        with open(file_name) as f:
            reader = csv.reader(f)
            for row in reader:
                article_urls.append(row[0])

        documents = SimpleWebPageReader().load_data(article_urls)
        index = GPTSimpleVectorIndex.from_documents(documents)

        return index.save_to_string()
    
    def create_index_from_urls(self, urls: list) -> str:
        documents = SimpleWebPageReader().load_data(urls)
        index = GPTSimpleVectorIndex.from_documents(documents)

        return index.save_to_string()

    def create_index(self, index_str_list: list[str]) -> GPTListIndex:
        index_list = []
        for index_string in index_str_list:
            # current_index = GPTSimpleVectorIndex.load_from_string(index_string)
            index_list.append(GPTSimpleVectorIndex.load_from_string(index_string))
        
        result_index = GPTListIndex(index_struct=index_list)
        return result_index

    def query_from_disk(self, query_string: str, index_file: str) -> RESPONSE_TYPE:
        index = GPTSimpleVectorIndex.load_from_disk(index_file)
        answer = index.query(query_string)
        return answer

    def query(self, query_string: str, index: GPTListIndex) -> RESPONSE_TYPE:
        # index = GPTSimpleVectorIndex.load_from_disk(index_file)
        answer = index.query(query_string)
        return answer
