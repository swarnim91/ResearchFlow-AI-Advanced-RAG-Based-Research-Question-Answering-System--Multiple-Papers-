import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from metadata_extractor import extract_metadata, save_metadata
from config import *
import json
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever


def load_paper_with_metadata(file_path, category):
    """Load paper and extract metadata."""
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    
    # Extract metadata
    metadata = extract_metadata(file_path)
    metadata['category'] = category
    save_metadata(metadata['filename'], metadata)
    
    # Add metadata to documents
    for doc in documents:
        doc.metadata.update(metadata)
    
    return documents

def load_all_papers(base_dir):
    """Load all papers from all categories."""
    all_documents = []
    
    for category in os.listdir(base_dir):
        cat_path = os.path.join(base_dir, category)
        if not os.path.isdir(cat_path):
            continue
        
        print(f"Loading {category} papers...")
        for filename in os.listdir(cat_path):
            if filename.endswith('.pdf'):
                file_path = os.path.join(cat_path, filename)
                try:
                    docs = load_paper_with_metadata(file_path, category)
                    all_documents.extend(docs)
                    print(f"  ✓ Loaded {filename}")
                except Exception as e:
                    print(f"  ✗ Error loading {filename}: {e}")
    
    return all_documents

def create_vector_store(documents):

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = text_splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_DB_DIR
    )

    vectorstore.persist()

    return vectorstore

def load_vector_store():

    if os.path.exists(VECTOR_DB_DIR) and os.listdir(VECTOR_DB_DIR):

        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )

        return Chroma(
            persist_directory=VECTOR_DB_DIR,
            embedding_function=embeddings
        )

    return None

def load_metadata(filename):
    """Load metadata for a paper."""
    json_path = os.path.join(METADATA_DIR, f"{os.path.splitext(filename)[0]}.json")
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            return json.load(f)
    return None

def create_synthesis_chain(vectorstore):
    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name=MODEL_NAME,
        temperature=0
    )

    template = """You are a strict research assistant.

Use ONLY the provided context to answer.
If the answer is not present, say: "Not found in provided papers."

First, provide a brief "Summary:" paragraph that summarizes the explicit answer to the question based on the context.
Then, under a new section "Details:", provide the detailed explanation.

Context:
{context}

Question:
{question}

Answer:"""
    
    PROMPT = PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )

    metadata_field_info = [
        AttributeInfo(
            name="title",
            description="The title of the paper",
            type="string",
        ),
        AttributeInfo(
            name="authors",
            description="The authors of the paper",
            type="string",
        ),
        AttributeInfo(
            name="year",
            description="The publication year of the paper",
            type="integer",
        ),
        AttributeInfo(
            name="summary",
            description="A brief summary of the paper",
            type="string",
        ),
        AttributeInfo(
            name="keywords",
            description="Keywords related to the paper",
            type="string",
        ),
        AttributeInfo(
            name="category",
            description="The category of the paper",
            type="string",
        ),
        AttributeInfo(
            name="filename",
            description="The filename of the paper",
            type="string",
        ),
    ]

    document_content_description = "A section of an academic research paper"

    base_retriever = SelfQueryRetriever.from_llm(
        llm,
        vectorstore,
        document_content_description,
        metadata_field_info,
        verbose=True
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=base_retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )
    return qa_chain

def ask_question(qa_chain, question):
    """Ask question and get synthesized answer."""
    try:
        result = qa_chain.invoke({"query": question})
        answer = result["result"]
        sources = result.get("source_documents", [])
        
        # Get unique papers cited
        cited_papers = {}
        for source in sources:
            filename = source.metadata.get('filename', 'Unknown')
            if filename not in cited_papers:
                metadata = load_metadata(filename)
                if metadata:
                    cited_papers[filename] = metadata
        
        return {
            "answer": answer,
            "sources": sources,
            "cited_papers": cited_papers
        }
    except Exception as e:
        return {
            "answer": f"Error: {str(e)}",
            "sources": [],
            "cited_papers": {}
        }

def main():
    """Main function."""
    print("=" * 60)
    print("🔬 Academic Research Companion")
    print("=" * 60)
    
    vectorstore = load_vector_store()
    
    if vectorstore is None:
        print("\nCreating database from papers...")
        documents = load_all_papers(PAPERS_DIR)
        if not documents:
            print("No papers found! Add PDFs to 'papers' folder.")
            return
        vectorstore = create_vector_store(documents)
    
    qa_chain = create_synthesis_chain(vectorstore)
    
    print("\n" + "=" * 60)
    print("System ready! Ask research questions")
    print("Type 'quit' to exit")
    print("=" * 60)
    
    while True:
        question = input("\n🔬 Research question: ").strip()
        if question.lower() in ['quit', 'exit', 'q']:
            break
        
        print("\nAnalyzing papers...")
        result = ask_question(qa_chain, question)
        
        print("\n" + "=" * 60)
        print("📊 Synthesized Answer:")
        print("=" * 60)
        print(result["answer"])
        
        if result["cited_papers"]:
            print("\n" + "=" * 60)
            print("📚 Papers Referenced:")
            print("=" * 60)
            for filename, metadata in result["cited_papers"].items():
                print(f"\n• {metadata.get('title', filename)}")
                print(f"  Authors: {metadata.get('authors', 'Unknown')}")
                print(f"  Year: {metadata.get('year', 'Unknown')}")
                print(f"  Category: {metadata.get('category', 'Unknown')}")
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
