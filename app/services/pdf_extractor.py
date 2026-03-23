import io

import pdfplumber


class PDFExtractorService:
    def extract_text(self, file_bytes: bytes) -> str:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = [page.extract_text() for page in pdf.pages if page.extract_text()]

        if not pages:
            raise ValueError("No readable text found in the PDF file.")

        return "\n".join(pages)
