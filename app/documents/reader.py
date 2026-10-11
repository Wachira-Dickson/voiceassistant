from pathlib import Path

class DocumentReader:
    """Read plain-text documents from the local filesystem."""

    SUPPORTED_EXTENSIONS = {".txt"}

    def read(self, file_path):
        path = Path(file_path)

        if not path.is_file():
            raise FileNotFoundError(f"Document not found: {path}")
        
        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                "Unsupported document format. Please select a .txt file."
            )
        
        try:
            return path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError as error:
            raise ValueError(
                "Unable to read this file as UTF-8 text."
            )from error
