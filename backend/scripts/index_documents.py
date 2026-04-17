import os 
import glob
import logging
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import AzureChatOpenAI , AzureOpenAIEmbeddings
from langchain_community.vectorstores import AzureSearch

load_dotenv(override=True) 

logger=logging.basicConfig(
    level = logging,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("indexer")

def index_docs():

    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.join(current_dir , "../../backend/data")

    logger.info("="*60)
    logger.info("Environment confoguration check: ")
    logger.info("="*60)

    required_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY",
        "AZURE_SEARCH_ENDPOINT",
        "AZURE_SEARCH_API_KEY",
        "AZURE_SEARCH_INDEX_NAME"
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(f"Missing env : {missing_vars}")
        return
    
    try:

        logger.info("Initializing azure openai embedding")

        embeddings = AzureOpenAIEmbeddings(
            azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT" , "text-embedding-3-small"),
            azure_endpoint =os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key= os.getenv("AZURE_OPENAI_API_KEY"),
        )

        logger.info("Embedding model initialized successfully")

    except Exception as e:
        logger.error("failed to initialize embeddings : {e}")
        return
    
    try:

        logger.info("Initializing azure search vector store")

        vector_store=AzureSearch(
        azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        azure_search_key= os.getenv("AZURE_SEARCH_API_KEY"),
        index_name= os.getenv("AZURE_SEARCH_INDEX_NAME"),
        embedding_function = embeddings.embed_query
    )

        logger.info("vector store initialized successfully")

    except Exception as e:
        logger.error("failed to initialize vector store : {e}")
        return
    
    pdf_files = glob.glob(os.path.join(data_folder , "*.pdf"))

    if not pdf_files:
        logger.warning(f"No pdf founf in {data_folder}")
    
    logger.info(f"found {len(pdf_files)} pdf to process : {[os.path.basename(f) for f in pdf_files]}")

    all_splits= []

    for pdf_path in pdf_files:
        try:

            logger.info(f"loading: {os.path.basename(pdf_path)}")
            loader = PyPDFLoader(pdf_path)
            raw_docs = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size = 1000,
                chunk_overlap = 200
            )

            splits= text_splitter.split_documents(raw_docs)
            for split in splits:
                split.metadata["source"] = os.path.basename(pdf_path)
            
            all_splits.extend(splits)

            logger.info(f"split into {len(splits)} chunks")
        
        except Exception as e:
            logger.error(f"Failed to process {pdf_path} : {e}")
        
        if all_splits:
            logger.info(f"Uploading {len(all_splits)} chunks to azure AI search index ")

            try:
                vector_store.add_documents(documnets=all_splits)
                logger.info("indexing complete")

            except Exception as e:
                logger.error("failed to upload the documents to azure serach",e)

        else:
            logger.warning("No documents were processed")

if __name__ == "__main__":
    index_docs()