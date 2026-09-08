"""Extractor de ejercicios resueltos y problemas prácticos de Álgebra de Baldor."""

from dataclasses import dataclass
import re


@dataclass
class BaldorExercise:
    """Representa un ejercicio o problema extraído de Álgebra de Baldor."""

    number: str
    statement: str
    solution: str = ""
    procedure: str = ""
    topic: str = ""

    def to_prompt_context(self) -> str:
        """Genera el texto estructurado del ejercicio para el prompt de generación de preguntas."""
        partes = [f"Tema: {self.topic}"] if self.topic else []
        partes.append(f"Problema / Ejercicio #{self.number}: {self.statement}")
        if self.procedure:
            partes.append(f"Procedimiento paso a paso:\n{self.procedure}")
        if self.solution:
            partes.append(f"Respuesta / Solución correcta: {self.solution}")
        return "\n".join(partes)


class BaldorExerciseExtractor:
    """Analizador para extraer problemas numerados, procedimientos y soluciones."""

    # Coincide con el inicio de un ejercicio numerado (ej. '1.', '1)', 'Ejercicio 16')
    _ITEM_START_RE = re.compile(
        r"""
        ^\s*
        (?P<num>\d+)
        [\.\)]
        \s+
        (?P<body>.+)
        \s*$
        """,
        re.VERBOSE,
    )

    _SOLUCION_SPLIT_RE = re.compile(
        r"""
        (?:\n|\s+)
        (?:Solución|Procedimiento|R\.|Respuesta)
        \s*:\s*
        """,
        re.VERBOSE | re.IGNORECASE,
    )

    def extract_from_text(self, text: str, default_topic: str = "") -> list[BaldorExercise]:
        """Extrae la lista de ejercicios presentes en un bloque de texto."""
        exercises: list[BaldorExercise] = []
        lines = text.splitlines()

        current_num: str | None = None
        current_lines: list[str] = []

        def flush_current():
            if current_num and current_lines:
                full_block = "\n".join(current_lines).strip()
                ex = self._parse_block(current_num, full_block, default_topic)
                if ex:
                    exercises.append(ex)

        for line in lines:
            m = self._ITEM_START_RE.match(line)
            if m:
                # Si ya veníamos acumulando un ejercicio, lo guardamos
                flush_current()
                current_num = m.group("num")
                current_lines = [m.group("body").strip()]
            else:
                if current_num is not None:
                    # Línea de continuación del ejercicio actual
                    current_lines.append(line)

        flush_current()
        return exercises

    def _parse_block(self, num: str, block: str, topic: str) -> BaldorExercise | None:
        """Parsea el bloque de texto de un ejercicio individual extrayendo enunciado, procedimiento y solución."""
        statement = block
        procedure = ""
        solution = ""

        # Caso 1: Tiene separadores explícitos como 'Solución:' o 'R.:'
        parts = self._SOLUCION_SPLIT_RE.split(block)
        if len(parts) > 1:
            statement = parts[0].strip()
            rest = parts[1].strip()
            # Si hay otra división (ej. procedimiento seguido de R.:)
            sub_parts = re.split(r"(?:\n|\s+)R\.\s*:\s*", rest, flags=re.IGNORECASE)
            if len(sub_parts) > 1:
                procedure = sub_parts[0].strip()
                solution = sub_parts[1].strip()
            else:
                solution = rest
                procedure = rest
        elif "=" in block:
            # Caso 2: Notación matemática de igualdad directa (ej. a^2 + 2ab + b^2 = (a + b)^2)
            eq_parts = block.split("=", 1)
            statement = eq_parts[0].strip()
            solution = eq_parts[1].strip()

        return BaldorExercise(
            number=num,
            statement=statement,
            procedure=procedure,
            solution=solution,
            topic=topic,
        )
