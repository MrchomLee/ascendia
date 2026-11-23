"""Conversión de bundles y perfiles a los bancos del juego."""

import gzip
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from qgen.bundle.spec import BUNDLE_VERSION
from qgen.cli.bancos_juego import app
from qgen.juego.bancos import (
    DIFICULTAD,
    FAMILIAS,
    banco_de_escuela,
    cargar_bundles,
    cargar_perfil,
    convertir_pregunta,
    escribir_banco,
    escribir_indice,
    leer_indice,
    motivo_de_descarte,
    mundo_id,
    pertenece,
    refs_de_capitulos,
    tema_de,
    ultimos_bundles,
)


def _toca(carpeta: Path, nombre: str, contenido: str = "{}") -> Path:
    path = carpeta / nombre
    path.write_text(contenido, encoding="utf-8")
    return path


def _nodo(ref: str, parent_ref: str | None, ordinal: str, title: str) -> dict:
    nivel = ref.count(".")
    return {
        "ref": ref, "parent_ref": parent_ref, "level": nivel,
        "level_label": "Parte" if nivel else "Bloque",
        "ordinal": ordinal, "title": title,
        "breadcrumb": f"Parte {ordinal}" if nivel else f"Bloque {ordinal}",
        "page_start": None, "page_end": None, "is_anexo": False, "metadata": {},
    }


def bundle_min() -> dict:
    """Bundle de TLR1: tres capítulos (ordinales 1, 3 y 2), un tema y tres preguntas.

    En el tema `01.01` hay una válida de comprensión y una rechazada; en `02`
    (capítulo 3) hay una de análisis.
    """
    return {
        "bundle_version": BUNDLE_VERSION,
        "generated_at": "2026-10-13T10:15:00Z",
        "generator": {"tool": "qgen", "version": "0.1.0", "pipeline_commit": "abc1234"},
        "manual": {
            "code": "TLR1",
            "edition": None,
            "title": "Taller de lectura y redacción 1",
            "branch": None,
            "source_path": "data/raw_pdfs/tlr1.pdf",
            "source_sha256": None,
            "page_count": 200,
            "extractor_used": "pymupdf",
            "ingested_at": "2026-10-12T22:04:11Z",
            "metadata": {},
        },
        "catalog_hint": {"grado_code": None, "materia_code": None},
        "nodes": [
            _nodo("01", None, "1", "Proceso comunicativo"),
            _nodo("01.01", "01", "1.1", "Los elementos del proceso comunicativo"),
            _nodo("02", None, "3", "Proceso de escritura"),
            _nodo("03", None, "2", "Proceso de lectura"),
        ],
        "runs": [],
        "questions": [
            pregunta(),
            pregunta(generation_order=18, validation_status="rejected"),
            pregunta(generation_order=19, node_ref="02", cognitive_level="analisis"),
        ],
    }


def _opcion(role: str, orden: int, texto: str) -> dict:
    return {
        "role": role, "order_in_question": orden, "text": texto,
        "is_correct": role == "correct", "metadata": {},
    }


def pregunta(**cambios) -> dict:
    """Pregunta válida del tema `01.01` de `bundle_min`, con `cambios` aplicados.

    `opcion_<i>` cambia el texto de la opción con `order_in_question == i`;
    `sin_correcta` marca todas como incorrectas; `solo_tres` quita la última.
    Cualquier otra clave reemplaza ese campo de la pregunta.
    """
    q = {
        "run_ref": "r1",
        "node_ref": "01.01",
        "generation_order": 17,
        "question_text": "¿Qué tienen en común…?",
        "justification": "«…» (Zarzar, Taller…, p. 9)",
        "question_type": "teoria",
        "source_quote": "Al escribir a mano…",
        "cognitive_level": "comprension",
        "validation_status": "valid",
        "validated_at": "2026-10-04T05:30:00Z",
        "created_at": "2026-10-04T05:07:59Z",
        "metadata": {},
        "options": [
            _opcion("confusa", 0, "B"),
            _opcion("distractor", 1, "C"),
            _opcion("correct", 2, "A correcta"),
            _opcion("distractor", 3, "D"),
        ],
    }
    for clave, valor in cambios.items():
        if clave.startswith("opcion_"):
            orden = int(clave.removeprefix("opcion_"))
            opcion = next(o for o in q["options"] if o["order_in_question"] == orden)
            opcion["text"] = valor
        elif clave == "sin_correcta":
            for opcion in q["options"]:
                opcion["is_correct"] = False
        elif clave == "solo_tres":
            q["options"].pop()
        else:
            q[clave] = valor
    return q


def bundle_alg() -> dict:
    """Bundle de ALG1: un capítulo (ordinal I) con dos preguntas válidas de conocimiento."""
    bundle = bundle_min()
    bundle["manual"].update(code="ALG1", title="Álgebra", source_path="data/raw_pdfs/alg1.pdf")
    bundle["nodes"] = [_nodo("01", None, "I", "Operaciones algebraicas")]
    bundle["questions"] = [
        pregunta(generation_order=orden, node_ref="01", cognitive_level="conocimiento")
        for orden in (1, 2)
    ]
    return bundle


def perfil_min() -> dict:
    """Perfil con la forma de `perfiles/ASP_HCM.json`.

    Dos materias: Español (TLR1, capítulo 1) y Álgebra (ALG1 completo).
    """
    return {
        "formato": 1,
        "perfil": {
            "code": "ASP_HCM",
            "name": "Aspirante al Heroico Colegio Militar",
            "track": "aspirantes",
            "description": "Examen de admisión a los planteles militares",
            "planteles": ["colegio_militar"],
        },
        "convocatoria": {"code": "2026", "name": "Convocatoria 2026", "vigente": True},
        "materias": [
            {"code": "ESP-01-2026", "name": "Español",
             "description": "Proceso comunicativo",
             "temario": [{"manual": "TLR1", "capitulos": ["1"]}]},
            {"code": "ALG-02-2026", "name": "Álgebra",
             "description": "Operaciones algebraicas",
             "temario": [{"manual": "ALG1", "capitulos": []}]},
        ],
    }


def test_ultimos_bundles_toma_la_version_mayor_por_manual(tmp_path):
    _toca(tmp_path, "tlr1--20261013--v4.json")
    v5 = _toca(tmp_path, "tlr1--20261013--v5.json")
    v9 = _toca(tmp_path, "alg1--20261013--v9.json")
    _toca(tmp_path, "alg1--20261013--v9.json.sha256")
    _toca(tmp_path, "notas.txt")
    (tmp_path / "tlr1--20261013--v6.json").mkdir()  # una carpeta no es un bundle
    assert ultimos_bundles(tmp_path) == {"TLR1": v5, "ALG1": v9}


def test_ultimos_bundles_acepta_gz_y_prefiere_la_version_mas_alta(tmp_path):
    _toca(tmp_path, "bio1--20261013--v5.json")
    gz = tmp_path / "bio1--20261014--v6.json.gz"
    gz.write_bytes(b"")
    assert ultimos_bundles(tmp_path) == {"BIO1": gz}


def test_cargar_bundles_indexa_por_el_codigo_real_del_manual(tmp_path):
    ley = {"bundle_version": BUNDLE_VERSION, "manual": {"code": "LEY DISC"}}
    espanol = {"bundle_version": BUNDLE_VERSION, "manual": {"code": "ESPAÑOL1"}}
    _toca(tmp_path, "ley-disc--20261013--v1.json", json.dumps(ley))
    gz = tmp_path / "espa-ol1--20261013--v2.json.gz"
    gz.write_bytes(gzip.compress(json.dumps(espanol).encode("utf-8")))
    rutas = ultimos_bundles(tmp_path)
    assert set(rutas) == {"LEY-DISC", "ESPA-OL1"}
    assert cargar_bundles(rutas) == {"LEY DISC": ley, "ESPAÑOL1": espanol}


def test_cargar_bundles_exige_la_version_del_bundle(tmp_path):
    viejo = bundle_min() | {"bundle_version": 2}
    path = _toca(tmp_path, "tlr1--20261013--v5.json", json.dumps(viejo))
    with pytest.raises(ValueError, match=r"tlr1--20261013--v5\.json.*bundle_version"):
        cargar_bundles({"TLR1": path})


def test_cargar_bundles_exige_el_codigo_del_manual(tmp_path):
    sin_codigo = bundle_min()
    del sin_codigo["manual"]["code"]
    path = _toca(tmp_path, "tlr1--20261013--v5.json", json.dumps(sin_codigo))
    with pytest.raises(ValueError, match=r"tlr1--20261013--v5\.json.*manual\.code"):
        cargar_bundles({"TLR1": path})
    path.write_text(json.dumps(bundle_min() | {"manual": None}), encoding="utf-8")
    with pytest.raises(ValueError, match=r"tlr1--20261013--v5\.json.*manual\.code"):
        cargar_bundles({"TLR1": path})


@pytest.mark.parametrize("contenido", [
    b"no es gzip",
    gzip.compress(json.dumps(bundle_min()).encode("utf-8"))[:-12],  # truncado
], ids=["no_gzip", "truncado"])
def test_cargar_bundles_nombra_el_archivo_de_un_gz_roto(tmp_path, contenido):
    gz = tmp_path / "tlr1--20261013--v5.json.gz"
    gz.write_bytes(contenido)
    with pytest.raises(ValueError, match=r"tlr1--20261013--v5\.json\.gz"):
        cargar_bundles({"TLR1": gz})


def test_cargar_bundles_rechaza_dos_bundles_del_mismo_manual(tmp_path):
    uno = _toca(tmp_path, "tlr1--20261013--v5.json", json.dumps(bundle_min()))
    otro = _toca(tmp_path, "tlr-1--20261013--v2.json", json.dumps(bundle_min()))
    with pytest.raises(ValueError, match=r"TLR1.*tlr1--20261013--v5\.json.*tlr-1--20261013--v2\.json"):
        cargar_bundles({"TLR1": uno, "TLR-1": otro})


def test_cargar_perfil_rechaza_otro_formato(tmp_path):
    with pytest.raises(ValueError, match=r"ASP_HCM\.json.*formato"):
        cargar_perfil(_toca(tmp_path, "ASP_HCM.json", json.dumps({"formato": 2})))


def test_cargar_perfil_nombra_el_archivo_si_el_json_es_ilegible(tmp_path):
    with pytest.raises(ValueError, match=r"ASP_HCM\.json"):
        cargar_perfil(_toca(tmp_path, "ASP_HCM.json", "{no es json"))


@pytest.mark.parametrize("falta", ["perfil", "materias"])
def test_cargar_perfil_exige_perfil_y_materias(tmp_path, falta):
    perfil = perfil_min()
    del perfil[falta]
    with pytest.raises(ValueError, match=rf"ASP_HCM\.json.*{falta}"):
        cargar_perfil(_toca(tmp_path, "ASP_HCM.json", json.dumps(perfil)))


def test_refs_de_capitulos_resuelve_ordinales_de_primer_nivel():
    assert refs_de_capitulos(bundle_min(), ["1", "3"]) == ["01", "02"]
    assert refs_de_capitulos(bundle_min(), []) == ["01", "02", "03"]


def test_refs_de_capitulos_falla_si_el_ordinal_no_existe():
    with pytest.raises(ValueError, match=r"TLR1.*'9'"):
        refs_de_capitulos(bundle_min(), ["1", "9"])


def test_pertenece_distingue_prefijos():
    assert pertenece("01", ["01"]) and pertenece("01.02", ["01"])
    assert not pertenece("010", ["01"]) and not pertenece("02.01", ["01"])


def test_tema_de_une_capitulo_y_tema():
    assert tema_de(bundle_min(), "01.01") == "Proceso comunicativo · Los elementos del proceso comunicativo"
    assert tema_de(bundle_min(), "01") == "Proceso comunicativo"


def test_tema_de_falla_si_el_nodo_no_existe():
    with pytest.raises(ValueError, match=r"TLR1.*'99'"):
        tema_de(bundle_min(), "99")


def test_convertir_pregunta_mapea_los_campos_del_bundle():
    q = convertir_pregunta(bundle_min(), pregunta())
    assert q == {
        "id": "TLR1:r1:17",
        "t": "Proceso comunicativo · Los elementos del proceso comunicativo",
        "p": "¿Qué tienen en común…?",
        "c": "A correcta",
        "d": ["B", "C", "D"],
        "x": "Al escribir a mano…",
        "f": "«…» (Zarzar, Taller…, p. 9)",
        "n": 1,
        "nivel": "comprension",
    }


def test_convertir_pregunta_tolera_nivel_nulo():
    assert convertir_pregunta(bundle_min(), pregunta(cognitive_level=None))["n"] == 0


def test_dificultad_por_nivel_cognitivo():
    assert DIFICULTAD == {"conocimiento": 0, "comprension": 1, "analisis": 2, "aplicacion": 2}


@pytest.mark.parametrize("cambios, motivo", [
    ({"validation_status": "rejected"}, "no_valida"),
    ({"question_text": "Según la figura 3, ¿cuál…?"}, "figura"),
    ({"opcion_1": "Ver la tabla 2"}, "figura"),
    ({"opcion_1": "La tabla periódica"}, None),
    ({"question_text": "¿Qué figura retórica…?"}, None),
    ({"question_text": "Observa la gráfica y di…"}, "figura"),
    ({"opcion_1": "la gráfica de f es una parábola"}, None),
    ({"question_text": "¿Qué muestra el mapa anterior?"}, "figura"),
    ({"opcion_1": "Se construyen tablas o gráficas"}, None),
    ({"question_text": "Según la figura A, ¿cuál…?"}, "figura"),
    ({"opcion_1": "la figura a la derecha"}, None),
    ({"question_text": "Con la siguiente tabla, ¿cuál…?"}, "figura"),
    ({"opcion_1": "Lo muestra la imagen adjunta"}, "figura"),
    ({"question_text": "Observa las imágenes y di…"}, "figura"),
    ({"opcion_1": "Lo dicen las tablas anteriores"}, "figura"),
    ({"opcion_1": "Lo dicen las anteriores gráficas"}, "figura"),
    ({"opcion_1": "Todas las anteriores"}, "orden"),
    ({"opcion_3": "La opción b es falsa"}, "orden"),
    ({"opcion_1": "El inciso va entre comas"}, None),
    ({"opcion_1": "ver el inciso b"}, "orden"),
    ({"opcion_1": "Ambas producen melatonina"}, None),
    ({"opcion_1": "A y B son conjuntos"}, None),
    ({"opcion_1": " a correcta "}, "repetida"),
    ({"sin_correcta": True}, "opciones"),
    ({"solo_tres": True}, "opciones"),
    ({}, None),
])
def test_motivo_de_descarte(cambios, motivo):
    assert motivo_de_descarte(pregunta(**cambios)) == motivo


def test_mundo_id_normaliza_el_nombre_de_la_materia():
    assert mundo_id("Álgebra") == "algebra"
    assert mundo_id("Historia de México") == "historia_de_mexico"


def test_banco_de_escuela_agrupa_por_materia_en_orden_del_perfil():
    banco, resumen = banco_de_escuela(perfil_min(), {"TLR1": bundle_min(), "ALG1": bundle_alg()})
    assert banco["escuela"] == {"code": "ASP_HCM", "name": "Aspirante al Heroico Colegio Militar"}
    assert [m["id"] for m in banco["mundos"]] == ["espanol", "algebra"]
    assert banco["mundos"][0] == {"id": "espanol", "materia": "Español", "manual": "TLR1",
                                  "familia": "espanol", "rango": 1, "capitulos": ["1"]}
    assert banco["mundos"][1]["familia"] == "mate" and banco["mundos"][1]["rango"] == 2
    assert [q["id"] for q in banco["bancos"]["espanol"]] == ["TLR1:r1:17"]
    assert len(banco["bancos"]["algebra"]) == 2
    assert resumen["mundos"]["espanol"] == {"total": 1, "por_n": [0, 1, 0], "descartadas": {"no_valida": 1}}


def test_banco_de_escuela_falla_si_falta_un_manual_o_se_repite_un_mundo():
    with pytest.raises(ValueError, match="ALG1"):
        banco_de_escuela(perfil_min(), {"TLR1": bundle_min()})
    perfil = perfil_min()
    perfil["materias"][1]["name"] = "Español"
    with pytest.raises(ValueError, match="espanol"):
        banco_de_escuela(perfil, {"TLR1": bundle_min(), "ALG1": bundle_alg()})


def test_banco_de_escuela_avisa_si_un_manual_no_tiene_familia():
    perfil = perfil_min()
    perfil["materias"][1]["temario"][0]["manual"] = "LEY1"
    ley = bundle_alg()
    ley["manual"]["code"] = "LEY1"
    with pytest.warns(UserWarning, match="LEY1"):
        banco, _ = banco_de_escuela(perfil, {"TLR1": bundle_min(), "LEY1": ley})
    assert banco["mundos"][1]["familia"] == "humanidades"


def test_familias_cubren_los_15_manuales():
    assert len(FAMILIAS) == 15 and FAMILIAS["TLR1"] == "espanol" and FAMILIAS["BIO1"] == "ciencias"


def test_escribir_banco_e_indice(tmp_path):
    banco, _ = banco_de_escuela(perfil_min(), {"TLR1": bundle_min(), "ALG1": bundle_alg()})
    ruta = escribir_banco(tmp_path, banco)
    assert ruta == tmp_path / "ASP_HCM.json"
    assert json.loads(ruta.read_text(encoding="utf-8"))["bancos"]["espanol"][0]["id"] == "TLR1:r1:17"
    assert ruta.read_bytes()[:1] == b"{"  # sin BOM
    indice = json.loads(escribir_indice(tmp_path, [banco]).read_text(encoding="utf-8"))
    assert indice["escuelas"] == [{"code": "ASP_HCM", "name": "Aspirante al Heroico Colegio Militar",
                                   "archivo": "ASP_HCM.json", "mundos": 2, "preguntas": 3}]


def _carpetas(tmp_path):
    bundles, perfiles, out = tmp_path / "b", tmp_path / "p", tmp_path / "o"
    bundles.mkdir()
    perfiles.mkdir()
    (bundles / "tlr1--20261013--v5.json").write_text(json.dumps(bundle_min()), encoding="utf-8")
    (bundles / "alg1--20261013--v9.json").write_text(json.dumps(bundle_alg()), encoding="utf-8")
    (perfiles / "ASP_HCM.json").write_text(json.dumps(perfil_min()), encoding="utf-8")
    return bundles, perfiles, out


def test_cli_escribe_un_banco_por_perfil(tmp_path):
    bundles, perfiles, out = _carpetas(tmp_path)
    r = CliRunner().invoke(app, ["--bundles", str(bundles), "--perfiles", str(perfiles), "--out", str(out)])
    assert r.exit_code == 0, r.output
    assert (out / "ASP_HCM.json").exists() and (out / "index.json").exists()
    assert "menos de 30" in r.output


def test_cli_check_no_escribe_y_falla_con_mundo_vacio(tmp_path):
    bundles, perfiles, out = _carpetas(tmp_path)
    r = CliRunner().invoke(app, ["--bundles", str(bundles), "--perfiles", str(perfiles), "--out", str(out), "--check"])
    assert r.exit_code == 0 and not out.exists()
    perfil = perfil_min()
    perfil["materias"][0]["temario"][0]["capitulos"] = ["2"]  # capítulo sin preguntas
    (perfiles / "ASP_HCM.json").write_text(json.dumps(perfil), encoding="utf-8")
    r = CliRunner().invoke(app, ["--bundles", str(bundles), "--perfiles", str(perfiles), "--out", str(out)])
    assert r.exit_code == 1 and "espanol" in r.output and not out.exists()


def _bancos_hcm_y_ema() -> tuple[dict, dict]:
    hcm, _ = banco_de_escuela(perfil_min(), {"TLR1": bundle_min(), "ALG1": bundle_alg()})
    otro = perfil_min()
    otro["perfil"].update(code="ASP_EMA", name="Aspirante Escuela Militar de Aviación")
    otro["materias"].pop()  # solo Español
    ema, _ = banco_de_escuela(otro, {"TLR1": bundle_min()})
    return hcm, ema


def _indice(out: Path) -> dict:
    return json.loads((out / "index.json").read_text(encoding="utf-8"))


def test_escribir_indice_fusiona_por_escuela(tmp_path):
    hcm, ema = _bancos_hcm_y_ema()
    escribir_banco(tmp_path, hcm)
    escribir_banco(tmp_path, ema)
    escribir_indice(tmp_path, [hcm])
    escribir_indice(tmp_path, [ema], fusionar=True)
    assert [(e["code"], e["mundos"], e["preguntas"]) for e in _indice(tmp_path)["escuelas"]] == [
        ("ASP_EMA", 1, 1), ("ASP_HCM", 2, 3)]
    escribir_indice(tmp_path, [hcm | {"mundos": hcm["mundos"][:1]}], fusionar=True)  # la nueva reemplaza
    assert [(e["code"], e["mundos"]) for e in _indice(tmp_path)["escuelas"]] == [
        ("ASP_EMA", 1), ("ASP_HCM", 1)]


def test_escribir_indice_sin_fusionar_reemplaza_el_previo(tmp_path):
    hcm, ema = _bancos_hcm_y_ema()
    escribir_banco(tmp_path, hcm)
    escribir_banco(tmp_path, ema)
    escribir_indice(tmp_path, [hcm, ema])
    escribir_indice(tmp_path, [ema])
    assert [e["code"] for e in _indice(tmp_path)["escuelas"]] == ["ASP_EMA"]


def test_escribir_indice_al_fusionar_descarta_entradas_sin_archivo(tmp_path):
    hcm, ema = _bancos_hcm_y_ema()
    escribir_banco(tmp_path, ema)
    escribir_indice(tmp_path, [hcm, ema])  # ASP_HCM.json no existe en la carpeta
    escribir_indice(tmp_path, [ema], fusionar=True)
    assert [e["code"] for e in _indice(tmp_path)["escuelas"]] == ["ASP_EMA"]


def test_escribir_indice_fusiona_con_las_previas_que_se_le_dan(tmp_path):
    hcm, ema = _bancos_hcm_y_ema()
    escribir_banco(tmp_path, hcm)
    escribir_banco(tmp_path, ema)
    previas = [{"code": "ASP_HCM", "name": "x", "archivo": "ASP_HCM.json", "mundos": 2, "preguntas": 3}]
    _toca(tmp_path, "index.json", "{roto")  # se ignora: manda `previas`
    escribir_indice(tmp_path, [ema], fusionar=True, previas=previas)
    assert [e["code"] for e in _indice(tmp_path)["escuelas"]] == ["ASP_EMA", "ASP_HCM"]


@pytest.mark.parametrize("contenido", [
    "{roto",
    "[]",
    json.dumps({"escuelas": []}),
    json.dumps({"formato": 1, "escuelas": {}}),
    json.dumps({"formato": 1, "escuelas": [{"name": "sin code"}]}),
    json.dumps({"formato": 1, "escuelas": ["ASP_HCM"]}),
])
def test_leer_indice_rechaza_un_indice_ilegible_o_con_otra_forma(tmp_path, contenido):
    _toca(tmp_path, "index.json", contenido)
    with pytest.raises(ValueError, match=r"index\.json"):
        leer_indice(tmp_path)


def test_leer_indice_ausente_es_lista_vacia(tmp_path):
    assert leer_indice(tmp_path) == []
    hcm, _ = _bancos_hcm_y_ema()
    escribir_indice(tmp_path, [hcm])
    assert [e["code"] for e in leer_indice(tmp_path)] == ["ASP_HCM"]


def _corre(*args: str):
    return CliRunner().invoke(app, list(args))


def _args(bundles: Path, perfiles: Path, out: Path) -> list[str]:
    return ["--bundles", str(bundles), "--perfiles", str(perfiles), "--out", str(out)]


def _perfil_ema() -> dict:
    otro = perfil_min()
    otro["perfil"].update(code="ASP_EMA", name="Aspirante Escuela Militar de Aviación")
    otro["materias"].pop()
    return otro


def test_cli_corrida_completa_reemplaza_el_indice(tmp_path):
    bundles, perfiles, out = _carpetas(tmp_path)
    out.mkdir()
    _toca(out, "ASP_EXTRA.json")  # su archivo existe, pero ya no tiene perfil
    extra = {"code": "ASP_EXTRA", "name": "Extra", "archivo": "ASP_EXTRA.json", "mundos": 1, "preguntas": 1}
    _toca(out, "index.json", json.dumps({"formato": 1, "escuelas": [extra]}))
    r = _corre(*_args(bundles, perfiles, out))
    assert r.exit_code == 0, r.output
    assert [e["code"] for e in _indice(out)["escuelas"]] == ["ASP_HCM"]


def test_cli_escuela_fusiona_con_el_indice_previo(tmp_path):
    bundles, perfiles, out = _carpetas(tmp_path)
    (perfiles / "ASP_EMA.json").write_text(json.dumps(_perfil_ema()), encoding="utf-8")
    assert _corre(*_args(bundles, perfiles, out)).exit_code == 0
    r = _corre(*_args(bundles, perfiles, out), "--escuela", "ASP_EMA")
    assert r.exit_code == 0, r.output
    assert [e["code"] for e in _indice(out)["escuelas"]] == ["ASP_EMA", "ASP_HCM"]


def test_cli_escuela_con_indice_previo_corrupto_avisa_y_lo_reconstruye(tmp_path):
    bundles, perfiles, out = _carpetas(tmp_path)
    out.mkdir()
    _toca(out, "index.json", "{roto")
    r = _corre(*_args(bundles, perfiles, out), "--escuela", "ASP_HCM")
    assert r.exit_code == 0, r.output
    assert "aviso" in r.output and "index.json" in r.output and "Traceback" not in r.output
    assert [e["code"] for e in _indice(out)["escuelas"]] == ["ASP_HCM"]


def test_cli_falla_sin_traceback_con_un_perfil_ilegible(tmp_path):
    bundles, perfiles, out = _carpetas(tmp_path)
    (perfiles / "ASP_ROTO.json").write_text("{no es json", encoding="utf-8")
    r = _corre(*_args(bundles, perfiles, out))
    assert r.exit_code == 1 and isinstance(r.exception, SystemExit)
    assert "ASP_ROTO.json" in r.output and "Traceback" not in r.output
    assert not out.exists()


def test_cli_no_escribe_nada_si_falla_una_de_las_escuelas(tmp_path):
    bundles, perfiles, out = _carpetas(tmp_path)
    mala = _perfil_ema()
    mala["materias"][0]["temario"][0]["capitulos"] = ["9"]  # TLR1 no tiene capítulo 9
    (perfiles / "ASP_EMA.json").write_text(json.dumps(mala), encoding="utf-8")
    r = _corre(*_args(bundles, perfiles, out))
    assert r.exit_code == 1 and "'9'" in r.output
    assert not out.exists()


def test_cli_escapa_el_codigo_en_el_error_de_mundo_vacio(tmp_path):
    bundles, perfiles, out = _carpetas(tmp_path)
    perfil = perfil_min()
    perfil["perfil"]["code"] = "ASP_[red]X"
    perfil["materias"][0]["temario"][0]["capitulos"] = ["2"]  # capítulo sin preguntas
    (perfiles / "ASP_HCM.json").write_text(json.dumps(perfil), encoding="utf-8")
    r = _corre(*_args(bundles, perfiles, out), "--check")
    assert r.exit_code == 1
    assert "ASP_[red]X · espanol: el mundo quedó sin preguntas" in r.output


def test_cli_falla_sin_traceback_con_un_bundle_ilegible(tmp_path):
    bundles, perfiles, out = _carpetas(tmp_path)
    (bundles / "tlr1--20261013--v6.json").write_text("{no es json", encoding="utf-8")
    r = CliRunner().invoke(app, ["--bundles", str(bundles), "--perfiles", str(perfiles), "--out", str(out)])
    assert r.exit_code == 1 and isinstance(r.exception, SystemExit)
    assert "tlr1--20261013--v6.json" in r.output and "Traceback" not in r.output
    assert not out.exists()
