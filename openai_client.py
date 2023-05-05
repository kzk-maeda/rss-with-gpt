import os
import csv
from dotenv import load_dotenv
from llama_index import GPTSimpleVectorIndex, SimpleWebPageReader
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
    
    
    def create_local_index(self, index_str: str) -> None:
        index = GPTSimpleVectorIndex.load_from_string(index_str)
        index.save_to_disk("index.json")


    def query(self, query_string: str, index_str: str) -> RESPONSE_TYPE:
        index = GPTSimpleVectorIndex.load_from_string(index_str)
        answer = index.query(query_string)
        return answer
