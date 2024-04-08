from elasticsearch import Elasticsearch
import sys

class SearchEngine:
    def __init__(self, host='http://localhost:9200'):
        self._es = Elasticsearch([host])

    def close(self):
        self._es.transport.close()

    def __del__(self):
        self.close()

    def index_text(self, text):
        # Индексация текста
        try:
            response = self._es.index(index="blog", body={"content": text})
            print(f"Документ добавлен с ID: {response['_id']}")
        except Exception as e:
            print(f"Ошибка при индексации текста: {e}")

    def search_phrase(self, phrase):
        try:
            response = self._es.search(index="blog", body={
                "query": {
                    "match": {
                        "content": phrase
                    }
                }
            })
            search_results = []
            for hit in response['hits']['hits']:
                document_id = hit['_id']
                content = hit['_source']['content']
                search_results.append(f"{content}")
        
            return search_results
        
        except Exception as e:
            print(f"Ошибка при поиске: {e}")
            return []  # Возвращаем пустой список в случае ошибки

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Использование: search_engine.py [read|write] [файл|фраза]")
        sys.exit(1)

    mode = sys.argv[1]
    arg = sys.argv[2]
    search_engine = SearchEngine()

    if mode == "write":
        search_engine.index_file(arg)
    elif mode == "read":
        search_engine.search_phrase(arg)
    else:
        print("Неизвестный режим. Используйте 'read' или 'write'.")