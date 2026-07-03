from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# 1. Initialize the exact same embedding model used during ingestion
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

# 2. Load our existing database collection from our local directory
vector_store = Chroma(
    collection_name="football_rules_collection",
    embedding_function=embeddings,
    persist_directory="./.football_chroma"
)

# 3. Expose it as a retriever interface
# By default, this will grab the top 4 most relevant chunks (k=4)
retriever = vector_store.as_retriever()