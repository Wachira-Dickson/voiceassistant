from app.documents.reader import DocumentReader

def main():
    reader = DocumentReader()

    file_path = "storage/documents/sample.txt"
    text = reader.read(file_path)

    print("Document loaded successfully.")
    print("-" * 40)
    print(text)

if __name__ == "__main__":
    main()