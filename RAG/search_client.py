from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType
import config

_client = SearchClient(
    endpoint=config.AZURE_SEARCH_ENDPOINT,
    index_name=config.AZURE_SEARCH_INDEX,
    credential=AzureKeyCredential(config.AZURE_SEARCH_KEY),
)


def search_documents(query: str) -> list[dict]:
    results = _client.search(
        search_text=query,
        query_type=QueryType.SEMANTIC,
        semantic_configuration_name=config.AZURE_SEARCH_SEMANTIC_CONFIG,
        top=config.SEARCH_TOP_K,
        select=["chunk", "title", "chunk_id", "parent_id"],
    )
    return [
        {
            "title":               r.get("title", ""),
            "chunk":               r.get("chunk", ""),
            "chunk_id":            r.get("chunk_id", ""),
            "parent_id":           r.get("parent_id", ""),
            "search_score":        r.get("@search.score", 0),
            "search_reranker_score": r.get("@search.rerankerScore", 0),
        }
        for r in results
    ]
