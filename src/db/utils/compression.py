import brotli


def compress_html(html: str) -> bytes:
    return brotli.compress(html.encode('utf-8'))

def decompress_html(compressed_html: bytes) -> str:
    return brotli.decompress(compressed_html).decode('utf-8')