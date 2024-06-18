from pandasai.ee.vectorstores.chroma import ChromaDB
#from chromadb.utils import embedding_functions


def get_pandasai_vector_store(llm):
    return ChromaDB(max_samples=2,
                        #embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name='all-mpnet-base-v2')
                    )