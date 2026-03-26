"""Módulo responsável pela extração de texto de arquivos PDF."""

from io import BytesIO
from typing import List

import pdfplumber

from app.core.exceptions import PDFExtractionError


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extrai o conteúdo textual de um arquivo PDF fornecido como bytes.

    Itera sobre todas as páginas do documento, descarta páginas sem conteúdo
    legível e concatena os textos com separação por linha dupla.

    Args:
        pdf_bytes: Conteúdo binário do arquivo PDF.

    Returns:
        Texto completo extraído do documento, com páginas separadas por linha dupla.

    Raises:
        PDFExtractionError: Se o PDF não contiver páginas, se nenhum texto
            puder ser extraído, ou se ocorrer falha ao processar o arquivo.
    """
    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            if not pdf.pages:
                raise PDFExtractionError("O arquivo PDF não contém páginas legíveis.")

            pages_text: List[str] = []
            for page in pdf.pages:
                page_content = page.extract_text()
                if page_content and page_content.strip():
                    pages_text.append(page_content.strip())

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
        raise PDFExtractionError(f"Erro ao processar o arquivo PDF: {str(exc)}") from exc
