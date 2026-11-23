"""Conversión de bundles y perfiles a los bancos del juego.

El módulo localiza el bundle más reciente de cada manual, lo carga, resuelve los
capítulos que pide un perfil de escuela a los nodos de ese bundle, convierte
cada pregunta al formato del juego web (o dice por qué la descarta), con todo
eso arma el banco de una escuela, un mundo por materia, y escribe los bancos y
su índice a disco. El comando `qgen-bancos-juego` (`qgen.cli.bancos_juego`)
solo orquesta estas funciones.
"""

from __future__ import annotations

import json
import re
import unicodedata
import warnings
import zlib
from pathlib import Path
from typing import Any

from qgen.bundle.spec import BUNDLE_VERSION, OPTIONS_PER_QUESTION, read_bundle

# Mismo patrón que `_FILENAME_RE` de `qgen.bundle.spec`:
# `{code}--{AAAAMMDD}--v{n}.json`, o `.json.gz` si el bundle se comprimió.
_NOMBRE_BUNDLE_RE = re.compile(
    r"^(?P<code>[a-z0-9._-]+)--(?P<date>\d{8})--v(?P<version>\d+)\.json(\.gz)?$"
)

#: Dificultad `n` de una pregunta en el juego, según su nivel cognitivo.
DIFICULTAD: dict[str, int] = {
    "conocimiento": 0,
    "comprension": 1,
    "analisis": 2,
    "aplicacion": 2,
}

#: Familia de cada manual; el juego elige por ella el escenario de su mundo.
FAMILIAS: dict[str, str] = {
    "ALG1": "mate",
    "CALC1": "mate",
    "CALC2": "mate",
    "TRIG_GEO1": "mate",
    "PRECALC1": "mate",
    "FIS1": "ciencias",
    "FIS2": "ciencias",
    "QUIM1": "ciencias",
    "BIO1": "ciencias",
    "GEO1": "humanidades",
    "GEO_MEX1": "humanidades",
    "HIST_UNI1": "humanidades",
    "HIST_MEX1": "humanidades",
    "MET_INV1": "humanidades",
    "TLR1": "espanol",
}
# La de un manual que no está en `FAMILIAS`, con un aviso.
_FAMILIA_POR_OMISION = "humanidades"

# Remite a algo que el juego no muestra; se busca en el enunciado y las opciones.
# Solo cuentan las referencias deícticas: la palabra seguida de lo que apunta
# fuera del texto («la figura 3», «la tabla A», «el mapa anterior»), un verbo de
# mirar delante («observa la gráfica») o «siguiente/anterior» delante («la
# siguiente tabla»). «La gráfica de f» o «la tabla periódica» nombran un
# concepto y se quedan. La letra de «figura A» tiene que ir en mayúscula: con
# `re.IGNORECASE` también entrarían «tablas o gráficas» y «la gráfica y su tangente».
_OBJETO_VISUAL = r"(?:figuras?|tablas?|mapas?|gr[aá]ficas?|im[aá]gen(?:es)?|diagramas?)"
_FIGURA_RE = re.compile(
    rf"\b{_OBJETO_VISUAL}\s+(?:\d+|(?-i:[A-Z])|siguientes?|anterior(?:es)?|adjunt[ao]s?"
    r"|que se muestra|mostrad[ao]s?|de arriba|de abajo)\b"
    rf"|\b(?:observ[ae]|v[eé]ase|mir[ae]|consult[ae])\s+(?:la|el|las|los)\s+{_OBJETO_VISUAL}\b"
    rf"|\b(?:siguientes?|anterior(?:es)?)\s+{_OBJETO_VISUAL}\b",
    re.IGNORECASE,
)
# Una opción que depende del orden de las demás; el juego las baraja.
_ORDEN_RE = re.compile(
    r"\b(todas las anteriores|ninguna de las anteriores"
    r"|ambas (opciones|respuestas|anteriores|son correctas)|opci[oó]n [a-d]|incisos? [a-d])\b",
    re.IGNORECASE,
)


def ultimos_bundles(carpeta: Path) -> dict[str, Path]:
    """El bundle de mayor `v{n}` de cada manual que hay en `carpeta`.

    La clave es el código del nombre de archivo en mayúsculas (`tlr1` → `TLR1`).
    Ese código es el `slug` del código real, así que puede no coincidir con él:
    `cargar_bundles` lo sustituye por el que trae el propio bundle. Lo que no
    es un archivo con nombre de bundle (los `.sha256`, notas sueltas, carpetas…)
    se ignora.
    """
    mejores: dict[str, tuple[int, Path]] = {}
    for path in sorted(carpeta.iterdir()):
        match = _NOMBRE_BUNDLE_RE.match(path.name)
        if not match or not path.is_file():
            continue
        code = match.group("code").upper()
        version = int(match.group("version"))
        if code not in mejores or version > mejores[code][0]:
            mejores[code] = (version, path)
    return {code: path for code, (_, path) in mejores.items()}


def cargar_bundles(rutas: dict[str, Path]) -> dict[str, dict[str, Any]]:
    """Lee cada bundle y lo indexa por el código real del manual (`manual.code`).

    Da un `ValueError` con el nombre del archivo si el bundle no es JSON válido
    (o su `.gz` está roto o truncado),
    si su `bundle_version` no es `BUNDLE_VERSION` (el conversor lee los campos de
    la v3) o si no trae `manual.code`; y otro si dos bundles son del mismo manual.
    No se verifica el `.sha256`: los bundles los escribe este mismo repo, y
    `json.loads` ya detecta una corrupción grosera.
    """
    bundles: dict[str, dict[str, Any]] = {}
    archivos: dict[str, str] = {}
    for path in rutas.values():
        try:
            bundle = read_bundle(path)
        except (ValueError, OSError, EOFError, zlib.error) as error:
            raise ValueError(f"{path.name}: {error or type(error).__name__}") from error
        version = bundle.get("bundle_version")
        if version != BUNDLE_VERSION:
            raise ValueError(
                f"{path.name}: bundle_version {version!r} no soportado (se espera {BUNDLE_VERSION})."
            )
        manual = bundle.get("manual")
        code = manual.get("code") if isinstance(manual, dict) else None
        if not isinstance(code, str) or not code:
            raise ValueError(f"{path.name}: el bundle no trae manual.code.")
        if code in bundles:
            raise ValueError(
                f"{code}: hay dos bundles del mismo manual, {archivos[code]} y {path.name}."
            )
        bundles[code] = bundle
        archivos[code] = path.name
    return bundles


def cargar_perfil(path: Path) -> dict[str, Any]:
    """Lee un perfil de escuela (`perfiles/*.json`) tal cual.

    Solo se entiende el `formato: 1`; cualquier otro es un error, para no leer a
    medias un perfil cuya forma ya cambió. Un JSON ilegible o sin `perfil` o sin
    `materias` también es un `ValueError`, siempre con el nombre del archivo.
    """
    try:
        perfil = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as error:
        raise ValueError(f"{path.name}: el perfil no es JSON válido ({error}).") from error
    formato = perfil.get("formato") if isinstance(perfil, dict) else None
    if formato != 1:
        raise ValueError(f"{path.name}: formato de perfil {formato!r} no soportado (se espera 1).")
    if not isinstance(perfil.get("perfil"), dict):
        raise ValueError(f"{path.name}: al perfil le falta el objeto perfil.")
    if not isinstance(perfil.get("materias"), list):
        raise ValueError(f"{path.name}: al perfil le falta la lista materias.")
    return perfil


def refs_de_capitulos(bundle: dict[str, Any], capitulos: list[str]) -> list[str]:
    """Los `ref` de los capítulos que pide el temario, en el orden del bundle.

    Un capítulo es un nodo de primer nivel (`parent_ref` nulo) y se nombra por su
    `ordinal`, que es el número del libro (`"3"`, `"IV"`), no por su `ref`. Una
    lista vacía quiere decir el manual completo. Si el temario pide un capítulo
    que el bundle no tiene, es un error: mejor parar que dejar un hueco callado.
    """
    raices = [nodo for nodo in bundle["nodes"] if nodo["parent_ref"] is None]
    if not capitulos:
        return [nodo["ref"] for nodo in raices]
    ordinales = {nodo["ordinal"] for nodo in raices}
    faltan = [ordinal for ordinal in capitulos if ordinal not in ordinales]
    if faltan:
        code = bundle["manual"]["code"]
        raise ValueError(
            f"{code}: el bundle no tiene los capítulos {', '.join(map(repr, faltan))}."
        )
    pedidos = set(capitulos)
    return [nodo["ref"] for nodo in raices if nodo["ordinal"] in pedidos]


def pertenece(node_ref: str, refs: list[str]) -> bool:
    """Si el nodo es uno de `refs` o cuelga de alguno (`01.02` cuelga de `01`; `010`, no)."""
    return any(node_ref == ref or node_ref.startswith(ref + ".") for ref in refs)


def tema_de(bundle: dict[str, Any], node_ref: str) -> str:
    """«Capítulo · Tema»: el título del nodo de primer nivel y luego el del nodo.

    Un nodo de primer nivel es su propio capítulo y da solo su título.
    """
    por_ref = {nodo["ref"]: nodo for nodo in bundle["nodes"]}
    if node_ref not in por_ref:
        code = bundle["manual"]["code"]
        raise ValueError(f"{code}: el bundle no tiene el nodo {node_ref!r}.")
    nodo = por_ref[node_ref]
    capitulo = nodo
    while capitulo["parent_ref"] is not None:
        capitulo = por_ref[capitulo["parent_ref"]]
    if capitulo is nodo:
        return nodo["title"]
    return f"{capitulo['title']} · {nodo['title']}"


def motivo_de_descarte(q: dict[str, Any]) -> str | None:
    """Por qué una pregunta del bundle no entra al juego, o `None` si entra.

    Gana el primer motivo, en este orden: `no_valida` (`validation_status` no es
    `valid`), `opciones` (no son 4 con exactamente una correcta), `figura` (el
    enunciado o una opción señala una figura, tabla, mapa, gráfica, imagen o
    diagrama que está fuera del texto: «la figura 3», «observa la gráfica», «el
    mapa anterior»), `orden` (una opción depende del orden de las demás) y `repetida`
    (dos opciones con el mismo texto, sin contar espacios ni mayúsculas: el juego
    reconoce la respuesta por su texto).
    """
    if q["validation_status"] != "valid":
        return "no_valida"
    opciones = q["options"]
    if len(opciones) != OPTIONS_PER_QUESTION or sum(o["is_correct"] for o in opciones) != 1:
        return "opciones"
    textos = [o["text"] for o in opciones]
    if any(_FIGURA_RE.search(texto) for texto in [q["question_text"], *textos]):
        return "figura"
    if any(_ORDEN_RE.search(texto) for texto in textos):
        return "orden"
    if len({" ".join(texto.split()).casefold() for texto in textos}) != len(textos):
        return "repetida"
    return None


def convertir_pregunta(bundle: dict[str, Any], q: dict[str, Any]) -> dict[str, Any]:
    """La pregunta en el formato del banco del juego; solo para las que no se descartan.

    `x` es la explicación corta y `f` la cita con su referencia: en el bundle v3
    vienen en `source_quote` y `justification`, al revés que en la base (ver
    `qgen.bundle.build`). `d` son las incorrectas en el orden de `order_in_question`.
    Un nivel cognitivo nulo (pregunta anterior a los niveles) o desconocido vale
    `n = 0`; `nivel` lo conserva tal cual.
    """
    opciones = sorted(q["options"], key=lambda o: o["order_in_question"])
    return {
        "id": f"{bundle['manual']['code']}:{q['run_ref']}:{q['generation_order']}",
        "t": tema_de(bundle, q["node_ref"]),
        "p": q["question_text"],
        "c": next(o["text"] for o in opciones if o["is_correct"]),
        "d": [o["text"] for o in opciones if not o["is_correct"]],
        "x": q["source_quote"],
        "f": q["justification"],
        "n": DIFICULTAD.get(q["cognitive_level"], 0),
        "nivel": q["cognitive_level"],
    }


def mundo_id(nombre: str) -> str:
    """El id del mundo de una materia: su nombre sin acentos, en minúsculas y con `_`.

    Cualquier tramo que no sea letra o dígito ASCII se vuelve un `_`, y se quitan
    los de los extremos: `"Historia de México"` → `"historia_de_mexico"`.
    """
    descompuesto = unicodedata.normalize("NFKD", nombre)
    sin_acentos = "".join(c for c in descompuesto if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "_", sin_acentos.lower()).strip("_")


def banco_de_escuela(
    perfil: dict[str, Any], bundles: dict[str, dict[str, Any]]
) -> tuple[dict[str, Any], dict[str, Any]]:
    """El banco del juego de una escuela y su resumen, como `(banco, resumen)`.

    Cada materia del perfil es un mundo, en el orden del perfil (`rango` 1, 2…),
    con las preguntas de los capítulos de su temario que no se descartan. El
    resumen da por mundo cuántas entran (`total`), cuántas de cada `n` (`por_n`)
    y los descartes por motivo; las preguntas de otros capítulos no cuentan como
    descartadas. `bundles` va indexado por código de manual, como lo deja
    `cargar_bundles`.

    Es un error que una materia no tenga exactamente un manual en su temario, que
    falte el bundle de un manual o que dos materias den el mismo id de mundo (una
    pisaría a la otra). Los errores al resolver capítulos o temas anteponen la
    escuela y la materia al mensaje.
    """
    escuela = perfil["perfil"]
    code = escuela["code"]
    mundos: list[dict[str, Any]] = []
    bancos: dict[str, list[dict[str, Any]]] = {}
    resumen: dict[str, dict[str, Any]] = {}
    for rango, materia in enumerate(perfil["materias"], start=1):
        nombre = materia["name"]
        id_mundo = mundo_id(nombre)
        if id_mundo in bancos:
            previa = next(m["materia"] for m in mundos if m["id"] == id_mundo)
            raise ValueError(
                f"{code}: las materias {previa!r} y {nombre!r} dan el mismo mundo {id_mundo!r}."
            )
        temario = materia["temario"]
        if len(temario) != 1:
            raise ValueError(
                f"{code}, {nombre}: el temario trae {len(temario)} manuales; "
                "el juego usa uno por materia."
            )
        manual = temario[0]["manual"]
        capitulos = list(temario[0]["capitulos"])
        if manual not in bundles:
            raise ValueError(f"{code}, {nombre}: no hay bundle del manual {manual!r}.")
        familia = FAMILIAS.get(manual)
        if familia is None:
            familia = _FAMILIA_POR_OMISION
            warnings.warn(
                f"{manual}: el manual no tiene familia; se usa {familia!r}.", stacklevel=2
            )
        try:
            preguntas, cuenta = _preguntas_del_mundo(bundles[manual], capitulos)
        except ValueError as error:
            raise ValueError(f"{code}, {nombre}: {error}") from error
        mundos.append({
            "id": id_mundo,
            "materia": nombre,
            "manual": manual,
            "familia": familia,
            "rango": rango,
            "capitulos": capitulos,
        })
        bancos[id_mundo] = preguntas
        resumen[id_mundo] = cuenta
    banco = {
        "formato": 1,
        "escuela": {"code": code, "name": escuela["name"]},
        "mundos": mundos,
        "bancos": bancos,
    }
    return banco, {"escuela": code, "mundos": resumen}


def _preguntas_del_mundo(
    bundle: dict[str, Any], capitulos: list[str]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Las preguntas convertidas de `capitulos` y su cuenta para el resumen."""
    refs = refs_de_capitulos(bundle, capitulos)
    preguntas: list[dict[str, Any]] = []
    por_n = [0] * (max(DIFICULTAD.values()) + 1)
    descartadas: dict[str, int] = {}
    for q in bundle["questions"]:
        if not pertenece(q["node_ref"], refs):
            continue
        motivo = motivo_de_descarte(q)
        if motivo is not None:
            descartadas[motivo] = descartadas.get(motivo, 0) + 1
            continue
        convertida = convertir_pregunta(bundle, q)
        preguntas.append(convertida)
        por_n[convertida["n"]] += 1
    return preguntas, {"total": len(preguntas), "por_n": por_n, "descartadas": descartadas}


def escribir_banco(out: Path, banco: dict[str, Any]) -> Path:
    """Escribe el banco de una escuela en `<out>/<CODE>.json` y devuelve esa ruta."""
    return _escribir_json(out / _archivo_de(banco), banco)


def leer_indice(out: Path) -> list[dict[str, Any]]:
    """Las escuelas de `<out>/index.json`, o `[]` si no existe.

    Un índice que no es JSON válido o no tiene la forma esperada (`formato` y
    `escuelas`, una lista de objetos con `code`) da un `ValueError` que nombra
    el archivo; quien llama decide si lo trata como ausente.
    """
    path = out / "index.json"
    if not path.is_file():
        return []
    try:
        indice = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as error:
        raise ValueError(f"{path.name}: el índice no es JSON válido ({error}).") from error
    escuelas = indice.get("escuelas") if isinstance(indice, dict) else None
    if (
        not isinstance(indice, dict)
        or "formato" not in indice
        or not isinstance(escuelas, list)
        or not all(isinstance(e, dict) and isinstance(e.get("code"), str) for e in escuelas)
    ):
        raise ValueError(
            f"{path.name}: el índice no tiene la forma esperada "
            "(formato y escuelas con code)."
        )
    return escuelas


def escribir_indice(
    out: Path,
    bancos: list[dict[str, Any]],
    *,
    fusionar: bool = False,
    previas: list[dict[str, Any]] | None = None,
) -> Path:
    """Escribe `<out>/index.json` con las escuelas de `bancos`, ordenadas por código.

    Por escuela da su código, su nombre, el archivo de su banco, cuántos mundos
    tiene y cuántas preguntas suman entre todos. Sin `fusionar` (una corrida
    completa) el índice se reemplaza. Con `fusionar` (una corrida con
    `--escuela`) las escuelas de `bancos` reemplazan a las del mismo código en
    el índice previo y las demás se conservan, salvo las cuyo `archivo` ya no
    existe en `out`. El índice previo es `previas` si se da (el CLI lo lee antes
    de escribir los bancos) o, si no, el que haya en disco (`leer_indice`).
    """
    path = out / "index.json"
    anteriores: dict[str, dict[str, Any]] = {}
    if fusionar:
        if previas is None:
            previas = leer_indice(out)
        anteriores = {
            escuela["code"]: escuela
            for escuela in previas
            if _archivo_en(out, escuela.get("archivo"))
        }
    nuevas = [
        {
            "code": banco["escuela"]["code"],
            "name": banco["escuela"]["name"],
            "archivo": _archivo_de(banco),
            "mundos": len(banco["mundos"]),
            "preguntas": sum(len(preguntas) for preguntas in banco["bancos"].values()),
        }
        for banco in bancos
    ]
    por_code = anteriores | {escuela["code"]: escuela for escuela in nuevas}
    escuelas = [por_code[code] for code in sorted(por_code)]
    return _escribir_json(path, {"formato": 1, "escuelas": escuelas})


def _archivo_en(out: Path, archivo: Any) -> bool:
    """Si `archivo` es el nombre (sin carpetas) de un archivo que existe en `out`."""
    return isinstance(archivo, str) and Path(archivo).name == archivo and (out / archivo).is_file()


def _archivo_de(banco: dict[str, Any]) -> str:
    """El nombre del archivo del banco de una escuela: `<CODE>.json`."""
    return f"{banco['escuela']['code']}.json"


def _escribir_json(path: Path, datos: dict[str, Any]) -> Path:
    """JSON en UTF-8 sin BOM, sin escapar acentos y sin sangría; crea la carpeta."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(datos, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return path
