"""Prueba unitaria del reordenamiento de fracciones romanas."""
from etl.chunking.consolidator import ChunkConsolidator

c = ChunkConsolidator(max_chars=2500, soft_target=2100, overlap=200, merge_under_chars=0)

# Simulación del problema: II y V aparecen después de Artículo 5o
parts = [
    "Artículo 4o.Para ser magistrado, se requiere:",
    "I.Ser mexicano por nacimiento...",
    "III.Ser abogado con título oficial...",
    "IV.Acreditar, cuando menos, diez años...",
    "Artículo 5o.El Tribunal Superior Militar tendrá un secretario...",
    "II.Ser mayor de treinta años;",
    "V.Ser de notoria honorabilidad.",
    "Artículo 6o.Para ser secretario de acuerdos...",
]

result = c._reorder_roman_fractions(parts)

print("=== RESULTADO ===")
for i, p in enumerate(result):
    print(f"[{i}] {p[:80]}")

# Verificar orden correcto
assert "II.Ser mayor" in result[2], f"II debería estar en posición 2, está en {[i for i,p in enumerate(result) if 'II.Ser' in p]}"
assert "V.Ser de notoria" in result[5], f"V debería estar en posición 5, está en {[i for i,p in enumerate(result) if 'V.Ser' in p]}"
assert "Artículo 5o" in result[4], f"Art 5 debería estar en posición 4"

print("\n✅ ¡Todas las verificaciones pasaron!")
