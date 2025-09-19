"""
文本分块器
"""
from typing import List, Dict, Any


class TextChunker:
    """文本分块器"""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """将文本分割成块"""
        if not text.strip():
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            # 如果不是最后一块，尝试在句号、换行符处分割
            if end < len(text):
                # 向后查找合适的分割点
                for i in range(end, max(start + self.chunk_size // 2, end - 100), -1):
                    if text[i] in '.!?\n':
                        end = i + 1
                        break

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunk_metadata = metadata.copy() if metadata else {}
                chunk_metadata.update({
                    'chunk_index': len(chunks),
                    'chunk_start': start,
                    'chunk_end': end,
                    'chunk_size': len(chunk_text)
                })

                chunks.append({
                    'text': chunk_text,
                    'metadata': chunk_metadata
                })

            start = end - self.chunk_overlap

        return chunks