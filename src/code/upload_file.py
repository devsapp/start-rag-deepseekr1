#####################################
#######    File Upload Module    #######
#####################################
import gradio as gr
import os
import shutil
import pandas as pd

WORK_DIR = os.getenv("WORK_DIR")
STRUCTURED_FILE_PATH = f"{WORK_DIR}/File/Structured"
UNSTRUCTURED_FILE_PATH = f"{WORK_DIR}/File/Unstructured"

# Initialize directories
if not os.path.exists(STRUCTURED_FILE_PATH):
    os.makedirs(STRUCTURED_FILE_PATH)

if not os.path.exists(UNSTRUCTURED_FILE_PATH):
    os.makedirs(UNSTRUCTURED_FILE_PATH)


def refresh_label():
    """Refresh unstructured categories"""
    return os.listdir(UNSTRUCTURED_FILE_PATH)


def refresh_data_table():
    """Refresh structured tables"""
    return os.listdir(STRUCTURED_FILE_PATH)


def upload_unstructured_file(files, label_name):
    """Upload unstructured data"""
    if not files:
        gr.Info("Please upload files")
        return

    if not label_name:
        gr.Info("Please enter category name")
        return

    if label_name in os.listdir(UNSTRUCTURED_FILE_PATH):
        gr.Info(f"Category '{label_name}' already exists")
        return

    try:
        os.makedirs(os.path.join(UNSTRUCTURED_FILE_PATH, label_name), exist_ok=True)
        for file in files:
            dest_path = os.path.join(
                UNSTRUCTURED_FILE_PATH, label_name, os.path.basename(file.name)
            )
            shutil.move(file.name, dest_path)

        gr.Info(f"Files uploaded to category '{label_name}'. Proceed to create knowledge base")

    except FileExistsError:
        gr.Info("Duplicate files detected")


def upload_structured_file(files, label_name):
    """Upload structured data"""
    if not files:
        gr.Info("Please upload files")
        return

    if not label_name:
        gr.Info("Please enter table name")
        return

    if label_name in os.listdir(STRUCTURED_FILE_PATH):
        gr.Info(f"Table '{label_name}' already exists")
        return

    try:
        os.makedirs(os.path.join(STRUCTURED_FILE_PATH, label_name), exist_ok=True)
        for file in files:
            file_path = file.name
            dest_path = os.path.join(STRUCTURED_FILE_PATH, label_name, os.path.basename(file_path))
            shutil.move(file_path, dest_path)

            # Convert to structured text format
            if dest_path.endswith(".xlsx"):
                df = pd.read_excel(dest_path)
            elif dest_path.endswith(".csv"):
                df = pd.read_csv(dest_path)

            txt_path = os.path.splitext(dest_path)[0] + ".txt"
            with open(txt_path, "w") as f:
                for idx, row in df.iterrows():
                    record = "【" + ",".join([f"{col}:{val}" for col, val in row.items()]) + "】"
                    f.write(f"{record}\n" if idx < len(df) - 1 else record)

            os.remove(dest_path)

        gr.Info(f"Files uploaded to table '{label_name}'. Proceed to create knowledge base")

    except Exception as e:
        gr.Info(f"Upload error: {str(e)}")


def update_datatable():
    """Update structured tables dropdown"""
    return gr.update(choices=os.listdir(STRUCTURED_FILE_PATH))


def update_label():
    """Update unstructured categories dropdown"""
    return gr.update(choices=os.listdir(UNSTRUCTURED_FILE_PATH))


def delete_label(label_name):
    """Delete unstructured categories"""
    if label_name:
        for label in label_name:
            path = os.path.join(UNSTRUCTURED_FILE_PATH, label)
            if os.path.exists(path):
                shutil.rmtree(path)
                gr.Info(f"Category '{label}' deleted")


def delete_data_table(table_name):
    """Delete structured tables"""
    if table_name:
        for table in table_name:
            path = os.path.join(STRUCTURED_FILE_PATH, table)
            if os.path.exists(path):
                shutil.rmtree(path)
                gr.Info(f"Table '{table}' deleted")
