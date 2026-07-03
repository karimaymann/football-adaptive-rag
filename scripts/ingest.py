import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

def main():
    print("--- 📄 STARTING GOOGLE-ALIGNED DOCUMENT INGESTION ---")
    
    # 1. Load the target rulebook PDF
    pdf_path = "./data/laws_of_the_game.pdf" # Double check your file path matches
    if not os.path.exists(pdf_path):
        print(f"❌ Error: Could not locate the rule book file at {pdf_path}")
        return
        
    loader = PyPDFLoader(pdf_path)
    raw_documents = loader.load()
    print(f"  -> Successfully imported {len(raw_documents)} raw pages from PDF.")

    # 2. Slice text cleanly via character length (Model-Agnostic, Google-Safe)
    # 600 characters equals ~150 words. An overlap of 100 preserves sentence context.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True
    )
    
    print("  -> Splitting raw document blocks into character chunks...")
    docs = text_splitter.split_documents(raw_documents)
    print(f"  -> Processed document text into {len(docs)} individual clean chunks.")

    # 3. Connect to the Google Generative AI Embeddings Engine
    print("  -> Initializing 'gemini-embedding-001' vectorizer...")
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

    # 4. Wipe out any old corrupt index collection and save freshly chunked strings
    persist_directory = "./.football_chroma"
    print(f"  -> Re-building vector database collection under '{persist_directory}'...")
    
    # Instantiate and force overwrite the index collection cleanly
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    
    print("--- ✅ SUCCESS: KNOWLEDGE BASE VECTOR INDEX IS SYNCED AND READY ---")

if __name__ == "__main__":
    main()