from io import BytesIO
from typing import List

import pdfplumber

from app.core.exceptions import PDFExtractionError


def extract_text_from_pdf(content: bytes) -> str:
    try:
        with pdfplumber.open(BytesIO(content)) as pdf:
            if not pdf.pages:
                raise PDFExtractionError("O arquivo PDF não contém páginas legíveis.")

            pages_text: List[str] = []
            for page in pdf.pages:
                text = page.extract_text()
                if text and text.strip():
                    pages_text.append(text.strip())

            full_text = "\n\n".join(pages_text)

            if not full_text.strip():
                raise PDFExtractionError(
                    "Não foi possível extrair texto do PDF. "
                    "Verifique se o arquivo não é uma imagem digitalizada sem OCR."
                )

            return full_text

    except PDFExtractionError:
        raise
    except Exception as exc:
        raise PDFExtractionError(f"Erro ao processar o arquivo PDF: {str(exc)}")
