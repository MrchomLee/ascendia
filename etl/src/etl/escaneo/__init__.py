"""Escaneo de libros sin capa de texto: páginas → maquetación (Docling) → OCR (PaddleOCR-VL en GPU) →
OCR de Windows para contrastar → borrador en Markdown y lista de palabras dudosas.

Cada paso lee y escribe en una carpeta de trabajo por libro (por defecto
`data/processed/escaneo/<nombre del PDF>/`), así que se puede repetir o retomar cualquiera. El OCR
guarda una caché por contenido: al corregir una región solo se vuelve a leer ese recorte.

El ensamble final (folios impresos, títulos, correcciones a mano revisadas en la imagen) no se
automatiza: depende de cada libro.
"""
