#####################################
######   Create Knowledge Base   #######
#####################################
import gradio as gr
import os
import shutil
from llama_index.core import VectorStoreIndex, Settings, SimpleDirectoryReader
from llama_index.embeddings.dashscope import (
    DashScopeEmbedding,
    DashScopeTextEmbeddingModels,
    DashScopeTextEmbeddingType,
)
from llama_index.core.schema import TextNode
from upload_file import *

WORK_DIR = os.getenv("WORK_DIR")
DB_PATH = f"{WORK_DIR}/VectorStore"
STRUCTURED_FILE_PATH = f"{WORK_DIR}/File/Structured"
UNSTRUCTURED_FILE_PATH = f"{WORK_DIR}/File/Unstructured"
TMP_NAME = f"{WORK_DIR}/tmp_abcd"

# Initialize directories
if not os.path.exists(DB_PATH):
    os.makedirs(DB_PATH)

if not os.path.exists(STRUCTURED_FILE_PATH):
    os.makedirs(STRUCTURED_FILE_PATH)

if not os.path.exists(UNSTRUCTURED_FILE_PATH):
    os.makedirs(UNSTRUCTURED_FILE_PATH)

if not os.path.exists(TMP_NAME):
    os.makedirs(TMP_NAME)

# Configure embedding model
EMBED_MODEL = DashScopeEmbedding(
    model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V2,
    text_type=DashScopeTextEmbeddingType.TEXT_TYPE_DOCUMENT,
)

# For local embedding model, uncomment:
# from langchain_community.embeddings import ModelScopeEmbeddings
# from llama_index.embeddings.langchain import LangchainEmbedding
# embeddings = ModelScopeEmbeddings(model_id="modelscope/iic/nlp_gte_sentence-embedding_chinese-large")
# EMBED_MODEL = LangchainEmbedding(embeddings)

Settings.embed_model = EMBED_MODEL


def refresh_knowledge_base():
    """Refresh knowledge base list"""
    return os.listdir(DB_PATH)


def create_unstructured_db(db_name: str, label_name: list):
    """Create unstructured vector database"""
    print(f"Knowledge base name: {db_name}, Categories: {label_name}")
    if not label_name:
        gr.Info("No categories selected")
    elif not db_name:
        gr.Info("Please name the knowledge base")
    elif db_name in os.listdir(DB_PATH):
        gr.Info("Knowledge base exists. Please rename or delete existing one")
    else:
        gr.Info("Creating knowledge base... Proceed to Q&A when completed")
        documents = []
        for label in label_name:
            label_path = os.path.join(UNSTRUCTURED_FILE_PATH, label)
            documents.extend(SimpleDirectoryReader(label_path).load_data())

        index = VectorStoreIndex.from_documents(documents)
        db_path = os.path.join(DB_PATH, db_name)

        if not os.path.exists(db_path):
            os.mkdir(db_path)
            index.storage_context.persist(db_path)

        gr.Info("Knowledge base created successfully")


def create_structured_db(db_name: str, data_table: list):
    """Create structured vector database"""
    print(f"Knowledge base name: {db_name}, Tables: {data_table}")
    if not data_table:
        gr.Info("No tables selected")
    elif not db_name:
        gr.Info("Please name the knowledge base")
    elif db_name in os.listdir(DB_PATH):
        gr.Info("Knowledge base exists. Please rename or delete existing one")
    else:
        gr.Info("Creating knowledge base... Proceed to Q&A when completed")
        documents = []
        for label in data_table:
            label_path = os.path.join(STRUCTURED_FILE_PATH, label)
            documents.extend(SimpleDirectoryReader(label_path).load_data())

        nodes = []
        for doc in documents:
            doc_content = doc.get_content().split("\n")
            for chunk in doc_content:
                node = TextNode(text=chunk)
                node.metadata = {"source": doc.get_doc_id(), "file_name": doc.metadata["file_name"]}
                nodes.append(node)

        index = VectorStoreIndex(nodes)
        db_path = os.path.join(DB_PATH, db_name)

        if not os.path.exists(db_path):
            os.mkdir(db_path)

        index.storage_context.persist(db_path)
        gr.Info("Knowledge base created successfully")


def delete_db(db_name: str):
    """Delete specified knowledge base"""
    if db_name:
        folder_path = os.path.join(DB_PATH, db_name)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            gr.Info(f"Successfully deleted {db_name}")
            print(f"Deleted {db_name}")
        else:
            gr.Info(f"{db_name} not found")
            print(f"{db_name} not found")


def update_knowledge_base():
    """Update knowledge base dropdown"""
    return gr.update(choices=os.listdir(DB_PATH))


def create_tmp_kb(files):
    """Create temporary knowledge base"""
    tmp_dir = os.path.join("File", TMP_NAME)
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)

    for file in files:
        file_name = os.path.basename(file)
        shutil.move(file, os.path.join(tmp_dir, file_name))

    documents = SimpleDirectoryReader(tmp_dir).load_data()
    index = VectorStoreIndex.from_documents(documents)
    db_path = os.path.join(DB_PATH, TMP_NAME)

    if not os.path.exists(db_path):
        os.mkdir(db_path)

    index.storage_context.persist(db_path)


def clear_tmp():
    """Clear temporary files"""
    tmp_data = os.path.join("File", TMP_NAME)
    tmp_db = os.path.join(DB_PATH, TMP_NAME)

    if os.path.exists(tmp_data):
        shutil.rmtree(tmp_data)
    if os.path.exists(tmp_db):
        shutil.rmtree(tmp_db)
