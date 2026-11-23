"""Reglas de redacción de las preguntas militares (promoción), sacadas de las observaciones del
usuario al piloto del Código de Justicia Militar (2026-11-19).

Las usan el prompt de generación de la familia militar (`prompts.families`) y la corrección de
preguntas ya generadas (`qgen.claude_correccion`): viven aquí para que nunca se desincronicen.
Los ejemplos concretos (pregunta original, observación y versión corregida) no van aquí: se
cargan de un archivo de datos, fuera del repositorio.
"""

from __future__ import annotations

REGLAS_REDACCION = """\
EL ENUNCIADO (TALLO)
1. Empieza con la fórmula fija "{conforme}," y nombra el delito o tema evaluado ("…, en el delito de traición a la patria, ¿…?"). En "aplicacion" el caso va primero y la fórmula después ("Aplicando el …, ¿…?").
2. La palabra interrogativa abre la interrogante: "¿qué elementos constituyen el delito de … si se transmiten al enemigo?", no "¿la transmisión al enemigo de qué elementos…?". Nada de hipérbaton ni de interrogantes retrasadas.
3. Voz activa y directa. Prohibidos los verbos de obligación y las pasivas largas para describir el delito ("debe inducirse", "debe ponerse en libertad", "para que la conducta constituya…", "para que haya falsificación"). Usa: "¿con qué finalidad se comete el delito de … al …?", "¿cuándo se comete el delito de … al …?", "¿en qué momento se comete el delito de … al …?".
4. Sin cacofonías ("¿para qué … para que …?") ni repeticiones de palabras.
5. Sin enunciados en negativo ("¿de qué no serán responsables?"): pásalos a su equivalente positivo ("¿de qué actos quedan exentos …?").
6. Terminología vigente y literal de la norma: si el artículo dice "persona privada de su libertad", no escribas "prisionero de guerra"; conserva todos los supuestos ("a quien liberó o cuya evasión favoreció"), los verbos rectores completos ("entablar o facilitar") y los calificativos exactos ("en todo o en parte", "el texto de un documento militar verdadero"). No agregues términos que la norma no trae ("responsabilidad legal", "elementos de comunicación") ni expresiones coloquiales o imprecisas ("¿qué queda expresamente fuera…?" → "¿qué actos no están comprendidos en dicha prohibición?").
7. El enunciado no adelanta la respuesta ni la restringe de más: no metas el detalle de una sola fracción ("¿qué conducta relativa a las firmas…?" → "¿qué acciones en un documento militar son consideradas como falsificación?") ni sesgos sobre el sujeto ("que los rebeldes causen"). Si la hipótesis abarca varios objetos (tropas, barcos y aeronaves), nómbralos todos en lugar de quedarte con uno.
8. Si la fracción trae dos conductas unidas por "o", el enunciado abarca las dos ("¿qué acciones … constituyen el delito de …?") o pregunta solo por una y la clave se limita a esa.
9. Interrogativo preciso: "¿cuándo?" para momentos y circunstancias; "¿qué acciones?" en lugar del abstracto "¿qué conducta?"; en vez del abierto "¿dónde?", "¿en qué zona jurisdiccional?". Usa los términos literales del Código ("buques o aeronaves") en el enunciado.
10. Efecto jurídico concreto y sin cifras: "para que se le reduzca la pena", "lo hace acreedor a una sanción penal", nunca "atenúan su responsabilidad" ni cantidades de años, meses o multas.
11. No fuerces el nivel "conocimiento" si el resultado es un "rellena el espacio" sin sentido o una lectura confusa: si la norma pide deducir una causa, un efecto o un escenario, plantéala en "comprension" o "aplicacion".

LAS OPCIONES
12. Las cuatro opciones son oraciones autónomas con mayúscula inicial y punto final; no fragmentos que continúen el enunciado ("las extravíe dolosamente…") ni pronombres heredados de la ley.
13. Paralelismo absoluto: las cuatro arrancan igual (todas en infinitivo: "Extraviar…", "Abandonar…"; o todas con "Porque la ley…", "La responsabilidad recae…", "No …") y tienen la misma estructura y extensión parecida: si la clave une dos conductas con "o", cada distractor también; si enumera tres elementos, cada distractor trae tres.
14. Concordancia con el enunciado: al cambiar el enunciado o la clave, reescribe las cuatro opciones (quita los "para que…" de una versión anterior; al pasar un enunciado negativo a positivo, cambia los "ni" por "y", "o", "así como").
15. La clave conserva íntegros los elementos de la norma (sujetos, actos, finalidades) con su terminología exacta, sin recortes; en "comprension" se enlaza con el delito del enunciado ("Porque la ley excluye de dicho delito a …").
16. Distractores plausibles y del propio Código: usa fórmulas reales de artículos o fracciones cercanas ("en campaña, en territorio declarado en estado de sitio o en estado de guerra", "marchando a encontrar al enemigo, esperándolo a la defensiva o bajo su persecución"), conductas de otros delitos militares sobre el mismo objeto (extravío, retención o destrucción de documentos; rebelión, deserción, motín) o el contraste dolo frente a culpa, impericia o falta administrativa. Uno de ellos puede calcar la estructura de la clave alterando sutilmente los sujetos o los fines.
17. Prohibido en los distractores: usar otras fracciones del mismo artículo cuando se pregunta por el tipo (serían también correctas); conductas que se traslapen con supuestos reales del mismo delito; pistas obvias de falsedad ("materiales inservibles", "sin la autorización competente"); absolutos ("siempre", "nunca", "en todo caso"); copiar muletillas de la clave donde no tienen sentido (", inclusive", "sin limitación, inclusive"); cierres mecánicos que imitan el final de la clave ("para instruirse", "para organizarse"); conceptos ajenos a la norma ("asunto humanitario"); escenarios débiles que se descartan a simple vista.
18. Propiedad léxica: cada palabra debe convenir a su objeto ("el desplazamiento de los barcos o aeronaves", no "la marcha").
"""


def reglas_redaccion(conforme: str) -> str:
    """Las reglas con la fórmula de inicio del manual ("Conforme al Código de Justicia Militar")."""
    return REGLAS_REDACCION.replace("{conforme}", conforme)
