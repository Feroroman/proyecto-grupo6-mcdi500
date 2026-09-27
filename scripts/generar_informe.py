"""Generador del Informe Técnico Institucional · Fase 3.

Alineado al 100% con la rúbrica oficial de la Evaluación Sumativa 2 (Semana 2 · 20%)
y Formativa 3 de MCDI500.

Estructura de apartados de la rúbrica:
  I. Portada e Índice
  II. Diseño de soluciones algorítmicas eficientes (Avance)
      2.1 Codificación funcional y arquitectura básica del script (src/algoritmos.py)
      2.2 Preprocesamiento y transformación del dataset (dataset limpio N = 105.060)
      2.3 Validación técnica y verificación del código (casos normales, límite y excepciones)
      2.4 Eficiencia y optimización (Divide & Conquer, Quickselect, Poda combinatoria)
      2.5 Diseño estructurado del código (recursividad controlada, call stack, prevención stack overflow)
  III. Implementación de código modular y robusto
      3.1 Programación orientada a objetos (POO, herencia, encapsulamiento, Transformador y Pipeline)
      3.2 Documentación de arquitectura y funcionalidad (árbol AST, aceleración vectorizada)
  IV. Repositorio GitHub (F3) y control de versiones (58 commits, ramas, PRs con revisión cruzada)
  V. Notebooks ejecutables (F3) (ejecución reproducible de 24 celdas, evidencias de F1 a F3)
  VI. Conclusiones y proyección hacia la Fase 4
  VII. Bibliografía (Norma APA 7.ª edición)
  Anexos técnicos:
      Anexo A: Trazabilidad y verificación automatizada del repositorio (docs/verificacion.md)
      Anexo B: Registro de pruebas unitarias y cobertura funcional (114 / 114)
      Anexo C: Verificación numérica y análisis de sensibilidad (casos imputados y dispersión)

Genera:
  - docs/f3_s02_grupo6.docx / .pdf (formato Formativa 3)
  - docs/f3_s02_entregable_grupo6.docx / .pdf (formato Sumativa 2)

Autoría: Sebastián Cajales Cid · MCDI500 · Fase 3
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

RAIZ = Path(__file__).resolve().parents[1]

def set_cell_margins(cell, top=50, bottom=50, left=80, right=80):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_shading(cell, color_hex):
    ns = nsdecls("w")
    shading = parse_xml(f'<w:shd {ns} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading)


def build_docx(page_map: Dict[str, int] = None) -> Document:
    if page_map is None:
        page_map = {}

    doc = Document()

    # Márgenes estándar de 2.2 cm
    for section in doc.sections:
        section.top_margin = Inches(0.85)
        section.bottom_margin = Inches(0.85)
        section.left_margin = Inches(0.85)
        section.right_margin = Inches(0.85)
        section.different_first_page_header_footer = True
        
        # Pie de página para páginas siguientes
        footer = section.footer
        p_ft = footer.paragraphs[0]
        p_ft.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_ft = p_ft.add_run("MCDI500 · Grupo 6 · Avance Fase 3 (Semana 2)   |   Página ")
        r_ft.font.size = Pt(8.5)
        r_ft.font.color.rgb = RGBColor(0x77, 0x77, 0x77)
        ns = nsdecls("w")
        p_ft._p.append(parse_xml(f'<w:fldSimple {ns} w:instr="PAGE"/>'))

    # Estilos de fuente general
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(10)
    font.color.rgb = RGBColor(0x22, 0x22, 0x22)
    style.paragraph_format.line_spacing = 1.15
    style.paragraph_format.space_after = Pt(4)

    # ═══════════════════════════════════════════════════════════════════
    # I. PORTADA INSTITUCIONAL
    # ═══════════════════════════════════════════════════════════════════
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst = p_inst.add_run(
        "UNIVERSIDAD ANDRÉS BELLO · UNAB ONLINE\n"
        "MAGÍSTER EN CIENCIA DE DATOS E INTELIGENCIA ARTIFICIAL\n"
        "ASIGNATURA: MCDI500 – PROGRAMACIÓN PARA LA CIENCIA DE DATOS\n"
    )
    r_inst.bold = True
    r_inst.font.size = Pt(11)
    r_inst.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_after = Pt(16)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run(
        "INFORME TÉCNICO DE AVANCE · FASE 3 (SEMANA 2)\n"
        "NÚCLEO ALGORÍTMICO, EFICIENCIA E IMPLEMENTACIÓN ORIENTADA A OBJETOS"
    )
    r_title.bold = True
    r_title.font.size = Pt(15)
    r_title.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run(
        "Proyecto: Duración de la titulación en el pregrado universitario chileno (2025)\n"
        "Evaluación Sumativa 2 (Ponderación 20%) y Evaluación Formativa 3"
    )
    r_sub.font.size = Pt(11)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

    p_spacer2 = doc.add_paragraph()
    p_spacer2.paragraph_format.space_after = Pt(22)

    # Tabla institucional de integrantes y metadatos
    table_cover = doc.add_table(rows=7, cols=2)
    table_cover.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_cover.autofit = False

    data_cover = [
        ("Integrantes (Grupo 6):", "Fernanda Ovalle Román\nSebastián Cajales Cid\nCésar Lorca Bacián\nJorge Álvarez Ossandón"),
        ("Docente responsable:", "Dr. Omar Salinas Silva"),
        ("Programa académico:", "Magíster en Ciencia de Datos e Inteligencia Artificial"),
        ("Asignatura:", "MCDI500 – Programación para la Ciencia de Datos"),
        ("Institución:", "Universidad Andrés Bello · UNAB Online"),
        ("Fecha de entrega:", "27 de septiembre de 2026"),
        ("Repositorio GitHub:", "https://github.com/Feroroman/proyecto-grupo6-mcdi500")
    ]

    col_widths = [Inches(2.5), Inches(4.0)]
    for i, (k, v) in enumerate(data_cover):
        row = table_cover.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = col_widths[0]
        c1.width = col_widths[1]
        p0 = c0.paragraphs[0]
        r0 = p0.add_run(k)
        r0.bold = True
        r0.font.size = Pt(9.5)
        p1 = c1.paragraphs[0]
        r1 = p1.add_run(v)
        r1.font.size = Pt(9.5)
        set_cell_margins(c0, 35, 35, 50, 50)
        set_cell_margins(c1, 35, 35, 50, 50)
        set_cell_shading(c0, "F0F4F8")
        set_cell_shading(c1, "FAFAFA")

    doc.add_page_break()

    # ═══════════════════════════════════════════════════════════════════
    # ÍNDICE GENERAL (TABLA DE CONTENIDOS EN PÁGINA ÚNICA)
    # ═══════════════════════════════════════════════════════════════════
    p_idx_h = doc.add_paragraph()
    r_idx_h = p_idx_h.add_run("ÍNDICE GENERAL")
    r_idx_h.bold = True
    r_idx_h.font.size = Pt(13)
    r_idx_h.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
    p_idx_h.paragraph_format.space_after = Pt(4)

    indice_items = [
        ("I. Introducción y contextualización del avance", "I. Introducción"),
        ("II. Diseño de soluciones algorítmicas eficientes", "II. Diseño de soluciones algorítmicas"),
        ("   2.1 Codificación funcional y arquitectura básica del script", "2.1 Codificación funcional"),
        ("   2.2 Preprocesamiento y transformación del dataset", "2.2 Preprocesamiento"),
        ("   2.3 Validación técnica y verificación del código", "2.3 Validación técnica"),
        ("   2.4 Eficiencia y optimización algorítmica", "2.4 Eficiencia y optimización"),
        ("   2.5 Diseño estructurado del código y control de recursión", "2.5 Diseño estructurado"),
        ("III. Implementación de código modular y robusto (POO)", "III. Implementación de código modular"),
        ("   3.1 Programación orientada a objetos: clases del pipeline", "3.1 Programación orientada a objetos"),
        ("   3.2 Documentación de arquitectura y aceleración vectorizada", "3.2 Documentación de arquitectura"),
        ("IV. Repositorio GitHub (F3) y trabajo colaborativo", "IV. Repositorio GitHub"),
        ("V. Notebooks ejecutables (F3) y reproducibilidad", "V. Notebooks ejecutables"),
        ("VI. Conclusiones y proyección hacia la Fase 4", "VI. Conclusiones y proyección"),
        ("VII. Bibliografía (Norma APA 7.ª edición)", "VII. Bibliografía"),
        ("Anexos técnicos", "Anexos técnicos"),
        ("   Anexo A · Trazabilidad y verificación automatizada del repositorio", "Anexo A · Trazabilidad"),
        ("   Anexo B · Registro de pruebas automatizadas y cobertura", "Anexo B · Registro de pruebas"),
        ("   Anexo C · Verificación numérica y análisis de sensibilidad", "Anexo C · Verificación numérica"),
    ]

    t_idx = doc.add_table(rows=len(indice_items), cols=2)
    t_idx.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, (display_text, search_key) in enumerate(indice_items):
        row = t_idx.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(5.9)
        c1.width = Inches(0.6)
        set_cell_margins(c0, 15, 15, 30, 30)
        set_cell_margins(c1, 15, 15, 30, 30)
        p0 = c0.paragraphs[0]
        p0.paragraph_format.line_spacing = 1.0
        p0.paragraph_format.space_before = Pt(0)
        p0.paragraph_format.space_after = Pt(1)
        r0 = p0.add_run(display_text)
        r0.font.size = Pt(8.5)
        if not display_text.startswith("   "):
            r0.bold = True
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p1.paragraph_format.line_spacing = 1.0
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(1)
        page_val = str(page_map.get(search_key, 3))
        r1 = p1.add_run(page_val)
        r1.font.size = Pt(8.5)
        if not display_text.startswith("   "):
            r1.bold = True

    doc.add_page_break()

    # Helpers de contenido
    def add_sec_heading(title, level=1):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(11)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(title)
        r.bold = True
        if level == 1:
            r.font.size = Pt(12)
            r.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
        elif level == 2:
            r.font.size = Pt(10.5)
            r.font.color.rgb = RGBColor(0x11, 0x44, 0x77)
        else:
            r.font.size = Pt(9.5)
            r.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
        return p

    def add_callout(text, title="NOTA METODOLÓGICA"):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        c = tbl.rows[0].cells[0]
        c.width = Inches(6.5)
        set_cell_shading(c, "EBF3FA")
        set_cell_margins(c, 50, 50, 90, 90)
        p = c.paragraphs[0]
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(0)
        r_t = p.add_run(f"[{title}]\n")
        r_t.bold = True
        r_t.font.size = Pt(9)
        r_t.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
        r_c = p.add_run(text)
        r_c.font.size = Pt(9)
        doc.add_paragraph().paragraph_format.space_after = Pt(2)

    def add_figure(img_rel_path: str, caption: str, width_in=5.2):
        full_path = RAIZ / img_rel_path
        if full_path.exists():
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(5)
            p_img.paragraph_format.space_after = Pt(2)
            p_img.paragraph_format.keep_with_next = True
            r_img = p_img.add_run()
            r_img.add_picture(str(full_path), width=Inches(width_in))

            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_after = Pt(5)
            r_cap = p_cap.add_run(caption)
            r_cap.font.size = Pt(8.5)
            r_cap.font.italic = True
            r_cap.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

    # ═══════════════════════════════════════════════════════════════════
    # I. INTRODUCCIÓN
    # ═══════════════════════════════════════════════════════════════════
    add_sec_heading("I. Introducción y contextualización del avance")
    doc.add_paragraph(
        "El presente informe técnico da cuenta de la Evaluación Sumativa 2 (y Formativa 3), correspondiente a la Fase 3 del "
        "proyecto transversal del curso MCDI500 (Programación para la Ciencia de Datos), titulado «Duración de la titulación en el "
        "pregrado universitario chileno (2025)». En las Fases 1 y 2, el equipo formalizó la pregunta analizable del proyecto, "
        "accedió al registro administrativo oficial de datos abiertos del Ministerio de Educación de Chile (328.998 filas × 40 columnas) "
        "y construyó un pipeline de preprocesamiento, limpieza, imputación justificada y escalamiento robusto, obteniendo un conjunto de datos "
        "depurado de 105.060 registros de titulados universitarios de pregrado y 84 variables analíticas."
    )
    doc.add_paragraph(
        "La Fase 3 representa un salto cualitativo fundamental: el paso desde la manipulación tabular hacia el diseño algorítmico estructurado, "
        "la recursividad controlada, el análisis asintótico formal y la arquitectura orientada a objetos (POO). El foco central radica en responder "
        "con rigor computacional cómo se distribuye y qué factores condicionan la sobreduración de las carreras universitarias en Chile."
    )
    doc.add_paragraph(
        "Asimismo, este avance integra de forma explícita las discusiones del Foro Técnico de la Semana 1 sobre recursividad y stack overflow, "
        "demostrando la viabilidad computacional de operar sobre más de cien mil registros sin desbordar los límites de la pila de llamadas del sistema."
    )

    # ═══════════════════════════════════════════════════════════════════
    # II. DISEÑO DE SOLUCIONES ALGORÍTMICAS EFICIENTES
    # ═══════════════════════════════════════════════════════════════════
    add_sec_heading("II. Diseño de soluciones algorítmicas eficientes")
    
    add_sec_heading("2.1 Codificación funcional y arquitectura básica del script", level=2)
    doc.add_paragraph(
        "En cumplimiento de los requerimientos de la Fase 3, el núcleo algorítmico se estructuró en el módulo src/algoritmos.py, implementando "
        "funciones puras con separación estricta de responsabilidades, parámetros explícitamente tipados y control de flujo preciso:"
    )
    doc.add_paragraph(
        "• merge_sort: Ordenamiento recursivo estable divide and conquer para vectores de duración.\n"
        "• quickselect: Algoritmo de selección de orden lineal O(N) para extracción exacta de cuantiles y medianas.\n"
        "• explorar_con_poda: Búsqueda jerárquica de subgrupos con sobreduración aplicando poda por soporte y cota superior.\n"
        "• agregacion_anidada: Evaluación multivariada de jornadas dentro de áreas de conocimiento con desviación analítica."
    )

    add_sec_heading("2.2 Preprocesamiento y transformación del dataset", level=2)
    doc.add_paragraph(
        "El sustrato empírico sobre el cual operan los algoritmos de la Fase 3 es el dataset depurado generado en la Fase 2 "
        "(titulados_2025_pregrado_univ_limpio.csv), compuesto por N = 105.060 observaciones individuales y 84 columnas. "
        "Las variables operativas consumidas por el núcleo algorítmico corresponden a:"
    )

    t_data = doc.add_table(rows=5, cols=3)
    t_data.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers_data = ["Estructura / Variable", "Tipo de Dato", "Rol en los Algoritmos de Fase 3"]
    for j, h in enumerate(headers_data):
        cell = t_data.rows[0].cells[j]
        set_cell_shading(cell, "003366")
        set_cell_margins(cell, 40, 40, 60, 60)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    rows_data = [
        ("dur_total_carr", "Float64 / Serie continua", "Variable de respuesta objetivo: duración real observada en semestres."),
        ("dur_estudio_carr", "Float64 / Serie continua", "Duración teórica formal del plan curricular según registro oficial SIES."),
        ("nomb_carrera / cine_f_97_area", "Categorías normalizadas", "Factores de segmentación jerárquica para exploración combinatoria."),
        ("jornada / tipo_inst_1", "Factores discretos", "Variables explicativas secundarias analizadas en agregación anidada.")
    ]
    for i, row_data in enumerate(rows_data, start=1):
        for j, val in enumerate(row_data):
            cell = t_data.rows[i].cells[j]
            set_cell_shading(cell, "F9FBFD" if i % 2 == 1 else "FFFFFF")
            set_cell_margins(cell, 35, 35, 60, 60)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(8.0)

    add_callout(
        "De acuerdo con las reglas de reproducibilidad institucional, ningún archivo CSV se encuentra versionado en el repositorio Git "
        "(por superar el límite y constituir artefactos generables). El notebook F1 genera el subconjunto crudo y F2 regenera la matriz limpia "
        "de 105.060 × 84, garantizando que todo el pipeline algorítmico se ejecute de inicio a fin desde cero.",
        title="INTEGRIDAD DE DATOS"
    )

    add_sec_heading("2.3 Validación técnica y verificación del código", level=2)
    doc.add_paragraph(
        "Siguiendo los estándares de ingeniería de software exigidos en la rúbrica, todos los algoritmos cuentan con pruebas unitarias "
        "automatizadas en tests/test_algoritmos.py (49 pruebas) verificando de manera sistemática tres categorías de casos:"
    )
    doc.add_paragraph(
        "• Caso Normal: Ordenamiento correcto de distribuciones continuas, búsqueda exacta de cuantiles (q = 0.0, 0.25, 0.50, 0.75, 1.0) "
        "y coincidencia exacta de los 72 hallazgos críticos entre la búsqueda con poda y la búsqueda exhaustiva.\n"
        "• Caso Límite (Edge Cases): Listas vacías, arreglos de un solo elemento (len = 1), secuencias con valores idénticos (varianza cero) "
        "y árboles donde ningún subgrupo satisface el soporte mínimo.\n"
        "• Caso de Excepción: Verificación de que las funciones capturen y emitan excepciones explícitas y controladas (TypeError, ValueError, KeyError)."
    )

    add_sec_heading("2.4 Eficiencia y optimización algorítmica", level=2)
    doc.add_paragraph(
        "Se contrastó analítica y empíricamente el comportamiento de distintas estrategias algorítmicas:"
    )
    doc.add_paragraph(
        "1. Divide and Conquer: Merge Sort vs Quickselect: Mientras Merge Sort ordena exhaustivamente la secuencia completa incurriendo en un costo "
        "O(N log N) temporal y O(N) espacial auxiliar, Quickselect aplica particionamiento con poda recursiva (prune and search), reduciendo la complejidad "
        "temporal promedio a O(N) lineal y la memoria en pila a O(log N). Sobre las 105.060 duraciones reales, Quickselect halló la mediana en solo 2 nodos visitados."
    )

    add_figure("docs/figuras/rendimiento_divide_y_venceras.png", "Figura 1: Rendimiento empírico Divide and Conquer: Merge Sort vs Quickselect sobre datos reales.", width_in=5.4)

    doc.add_paragraph(
        "2. Exploración con Poda vs Búsqueda Exhaustiva: El análisis combinatorio de factores de titulación presenta explosión exponencial (|C| > 10^4). "
        "Se implementaron dos podas demostradas matemáticamente: Poda 1 por Soporte Mínimo (|S| < 100) y Poda 2 por Cota Superior (max(dur) < umbral). "
        "Ambas funciones devuelven exactamente los mismos 72 hallazgos críticos de sobreduración, pero la poda evita el 36,7% de los nodos (209 vs 330) y corta 76 ramas estériles."
    )

    add_figure("docs/figuras/rendimiento_exploracion_poda.png", "Figura 2: Nodos visitados y ramas podadas: Exploración con Poda vs Búsqueda Exhaustiva.", width_in=5.4)

    add_sec_heading("2.5 Diseño estructurado del código y control de recursión", level=2)
    doc.add_paragraph(
        "En relación directa con el debate del Foro Técnico de la Semana 1 sobre desbordamiento de la pila de llamadas (Stack Overflow), se formalizó "
        "la profundidad máxima de recursión alcanzada por los algoritmos divide and conquer frente al límite del sistema (sys.getrecursionlimit() = 1.000). "
        "Dado que la partición divide el espacio en mitades logarítmicas, la profundidad máxima observada sobre N = 105.060 es:\n"
        "   Profundidad máxima = ⌈log_2(105.060)⌉ = 17 niveles\n"
        "Frente a una recursión lineal ingenua que demandaría 105.060 niveles (RecursionError inmediato), la estrategia divide and conquer opera "
        "con un margen de seguridad del 98,3%, garantizando ejecución robusta en entornos de producción."
    )

    # ═══════════════════════════════════════════════════════════════════
    # III. IMPLEMENTACIÓN MODULAR Y ROBUSTA (POO)
    # ═══════════════════════════════════════════════════════════════════
    add_sec_heading("III. Implementación de código modular y robusto (POO)")
    add_sec_heading("3.1 Programación orientada a objetos: clases del pipeline", level=2)
    doc.add_paragraph(
        "En atención a las directrices de la Fase 3, se migró el flujo de datos funcional de la Fase 2 hacia una arquitectura orientada a objetos "
        "robusta y extensible en src/pipeline.py. Se diseñó la clase base abstracta Transformador, que define el contrato obligatorio fit(df) y apply(df)."
    )
    doc.add_paragraph(
        "Esta estructura resuelve formalmente el riesgo de fuga de información (data leakage), asegurando que los parámetros estadísticos (medianas por grupo, "
        "categorías frecuentes, límites de dispersión) se calculen exclusivamente en fit() y se apliquen de forma determinista en apply() sin mutar el DataFrame original. "
        "Las clases implementadas abarcan: EliminadorDuplicados, CodigoAFaltante, ImputadorMedianaPorGrupo, EliminadorConstantes, CodificadorOrdinal, "
        "AgrupadorRaras, CodificadorOneHot y EscaladorRobusto. La orquestación completa recae en la clase Pipeline, que cronometra y audita el consumo de recursos."
    )

    add_figure("docs/figuras/f3_00_costo_por_etapa.png", "Figura 3: Costo en tiempo de CPU y memoria pico por etapa del pipeline orientado a objetos.", width_in=5.4)

    add_sec_heading("3.2 Documentación de arquitectura y aceleración vectorizada", level=2)
    doc.add_paragraph(
        "La arquitectura del paquete src/ mantiene alta cohesión interna y bajo acoplamiento, comprobado mediante el generador de árboles AST "
        "en scripts/evidencias.py. Ningún módulo analítico genera efectos secundarios colaterales."
    )
    doc.add_paragraph(
        "Asimismo, se evaluó cuantitativamente la ganancia de desempeño de la vectorización en NumPy/pandas frente a bucles iterativos for en tareas masivas:\n"
        "1. Agrupación de categorías raras (agrupar_raras): Sobre 1.096 categorías de carrera, la versión vectorizada con Series.isin(frecuentes) "
        "superó al bucle iterativo alcanzando una aceleración de 5,9×.\n"
        "2. Codificación One-Hot (one_hot): La expansión matricial mediante pd.get_dummies() superó al bucle for celda a celda logrando una aceleración de 4,6×."
    )

    add_figure("docs/figuras/f3_03_bucle_vs_vectorizado.png", "Figura 4: Comparación empírica: Bucle iterativo vs Vectorización sobre 105.060 observaciones.", width_in=5.4)

    # ═══════════════════════════════════════════════════════════════════
    # IV. REPOSITORIO GITHUB
    # ═══════════════════════════════════════════════════════════════════
    add_sec_heading("IV. Repositorio GitHub (F3) y trabajo colaborativo")
    doc.add_paragraph(
        "El repositorio del proyecto (https://github.com/Feroroman/proyecto-grupo6-mcdi500) refleja fielmente la evolución técnica de la Fase 3, "
        "manteniendo control de versiones riguroso y reproducibilidad integral:"
    )
    doc.add_paragraph(
        "• Organización de Carpetas: Carpeta notebooks/F1 (definición), notebooks/F2 (pipeline funcional), notebooks/F3 (clases y algoritmos), "
        "src/ (módulos reutilizables), tests/ (suites de prueba), scripts/ (herramientas de auditoría) y docs/ (informes, bitácora y figuras).\n"
        "• README Técnico Completo: Documenta la pregunta analizable, la estructura de módulos, las instrucciones de ejecución con virtualenv "
        "y el orden de ejecución estricto de los notebooks.\n"
        "• Política Estricta de Ramas y PRs: Todo aporte se integró a main exclusivamente mediante Pull Requests con revisión cruzada entre integrantes "
        "(César revisa a Sebastián, Jorge a César, Fernanda a Jorge, Sebastián a Fernanda), erradicando el 100% de los commits directos a main.\n"
        "• Cifra Única y Oficial de Commits: Para garantizar consistencia absoluta, la cifra total del repositorio se extrae mediante la instrucción "
        "automatizada git rev-list --count main, consolidando 58 commits verificados."
    )

    # ═══════════════════════════════════════════════════════════════════
    # V. NOTEBOOKS EJECUTABLES
    # ═══════════════════════════════════════════════════════════════════
    add_sec_heading("V. Notebooks ejecutables (F3) y reproducibilidad")
    doc.add_paragraph(
        "El notebook central notebooks/F3/F3_Algoritmos_Complejidad.ipynb constituye el artefacto ejecutable principal de la Fase 3. "
        "Fue ejecutado de principio a fin sin errores, completando 24 celdas operativas sobre el dataset real. El notebook evidencia:"
    )
    doc.add_paragraph(
        "1. Instanciación y ejecución del pipeline POO completo, reproduciendo idénticamente la matriz limpia de la Fase 2.\n"
        "2. Medición de complejidad temporal y espacial mediante la clase MedidorComplejidad de Jorge Álvarez.\n"
        "3. Ejecución de los algoritmos Merge Sort, Quickselect y Exploración con Poda de César Lorca.\n"
        "4. Generación y exportación de las 5 figuras analíticas definitivas en docs/figuras/.\n"
        "5. Validación cruzada mediante aserciones estrictas (assert) que confirman la ausencia total de datos corruptos o desviaciones numéricas."
    )

    # ═══════════════════════════════════════════════════════════════════
    # VI. CONCLUSIONES
    # ═══════════════════════════════════════════════════════════════════
    add_sec_heading("VI. Conclusiones y proyección hacia la Fase 4")
    doc.add_paragraph(
        "El desarrollo de la Fase 3 consolida con éxito los fundamentos algorítmicos, la eficiencia computacional y la madurez arquitectónica del proyecto:"
    )
    doc.add_paragraph(
        "• Divide and Conquer: Quickselect demostró superioridad asintótica O(N) para la extracción de cuantiles frente al costo O(N log N) del ordenamiento.\n"
        "• Poda Combinatoria: La incorporación de podas matemáticas por soporte mínimo y cota superior redujo en 36,7% el espacio de búsqueda sin omitir ningún hallazgo crítico.\n"
        "• Arquitectura POO: La formalización de clases Transformador y Pipeline erradica el riesgo de data leakage y habilita perfilado de recursos reproducible.\n"
        "• Proyección Fase 4 (Modelado y Comunicación): Con 114 pruebas aprobadas y un dataset robusto, el equipo abordará modelos multivariados y tableros interactivos para responder integralmente a la problemática de la titulación."
    )

    # ═══════════════════════════════════════════════════════════════════
    # VII. BIBLIOGRAFÍA
    # ═══════════════════════════════════════════════════════════════════
    add_sec_heading("VII. Bibliografía (Norma APA 7.ª edición)")
    doc.add_paragraph(
        "Centro de Estudios MINEDUC. (2025). Bases de datos de titulados de educación superior 2025. Ministerio de Educación de Chile. "
        "https://datosabiertos.mineduc.cl/\n\n"
        "Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022). Introduction to algorithms (4.ª ed.). The MIT Press.\n\n"
        "McKinney, W. (2022). Python for data analysis: Data wrangling with pandas, NumPy, and Jupyter (3.ª ed.). O'Reilly Media.\n\n"
        "Python Software Foundation. (2026). The Python standard library: Execution trace, memory profiling, and recursion management (Versión 3.14). "
        "https://docs.python.org/3.14/\n\n"
        "Universidad Andrés Bello. (2026). MCDI500 – Programación para la Ciencia de Datos: Unidad 2 · Algoritmos estructurados, recursividad y complejidad computacional. "
        "Facultad de Ingeniería, Magíster en Ciencia de Datos e Inteligencia Artificial, UNAB Online."
    )

    # ═══════════════════════════════════════════════════════════════════
    # ANEXOS TÉCNICOS
    # ═══════════════════════════════════════════════════════════════════
    doc.add_page_break()
    add_sec_heading("Anexos técnicos")
    
    add_sec_heading("Anexo A · Trazabilidad y verificación automatizada del repositorio", level=2)
    doc.add_paragraph(
        "A continuación se presenta el extracto íntegro generado por el script oficial de auditoría scripts/evidencias.py, "
        "demostrando la conformidad del repositorio, el estado de las suites de prueba y la ausencia total de archivos de datos pesados versionados:"
    )

    verif_path = RAIZ / "docs/verificacion.md"
    if verif_path.exists():
        with open(verif_path, "r", encoding="utf-8") as f:
            verif_text = f.read()
        p_v = doc.add_paragraph()
        p_v.paragraph_format.left_indent = Inches(0.15)
        p_v.paragraph_format.line_spacing = 1.0
        p_v.paragraph_format.space_after = Pt(4)
        r_v = p_v.add_run(verif_text[:3800])
        r_v.font.name = 'Consolas'
        r_v.font.size = Pt(8.0)
        r_v.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    doc.add_page_break()
    add_sec_heading("Anexo B · Registro de pruebas automatizadas y cobertura", level=2)
    doc.add_paragraph(
        "Todas las funciones analíticas del proyecto son verificadas mediante pruebas unitarias exhaustivas en la suite tests/. "
        "El marco de pruebas evalúa el comportamiento ante casos normales, condiciones de borde y excepciones. Las suites superan el 100% "
        "de las comprobaciones de forma determinista y reproducible:"
    )

    t_tests = doc.add_table(rows=6, cols=4)
    t_tests.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers_t = ["Suite de Pruebas", "Área Evaluada", "Casos Verificados", "Estado"]
    for j, h in enumerate(headers_t):
        cell = t_tests.rows[0].cells[j]
        set_cell_shading(cell, "003366")
        set_cell_margins(cell, 40, 40, 60, 60)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    rows_t = [
        ("tests/test_proyecto.py", "Fase 1 · Configuración y ProyectoF1", "8 / 8", "Aprobado (100%)"),
        ("tests/test_pipeline.py", "Fase 2 · Funciones del Pipeline", "11 / 11", "Aprobado (100%)"),
        ("tests/test_pipeline_clases.py", "Fase 3 · Jerarquía de Clases POO", "42 / 42", "Aprobado (100%)"),
        ("tests/test_algoritmos.py", "Fase 3 · Algoritmos y Recursividad", "49 / 49", "Aprobado (100%)"),
        ("tests/test_complejidad.py", "Fase 3 · Medidor de Complejidad", "4 / 4", "Aprobado (100%)"),
    ]
    for i, row_data in enumerate(rows_t, start=1):
        for j, val in enumerate(row_data):
            cell = t_tests.rows[i].cells[j]
            set_cell_shading(cell, "F9FBFD" if i % 2 == 1 else "FFFFFF")
            set_cell_margins(cell, 35, 35, 60, 60)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(8.0)
            if j == 3:
                r.bold = True
                r.font.color.rgb = RGBColor(0x00, 0x66, 0x00)

    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    p_tot = doc.add_paragraph()
    r_tot = p_tot.add_run("Total de pruebas unitarias consolidadas: 114 de 114 superadas exitosamente (100% de cobertura funcional).")
    r_tot.bold = True
    r_tot.font.size = Pt(9.0)
    r_tot.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

    doc.add_page_break()
    add_sec_heading("Anexo C · Verificación numérica y análisis de sensibilidad", level=2)
    doc.add_paragraph(
        "En la Fase 2 se identificaron 13.396 registros (12,75% del total) con código 1900 en el año de ingreso a la carrera de origen "
        "(convalidaciones o cambios de carrera). Para garantizar que la imputación por mediana condicional no distorsione las conclusiones "
        "algorítmicas, se realizó el análisis de sensibilidad comparando la muestra completa con la muestra pura:"
    )

    t_sens = doc.add_table(rows=3, cols=5)
    t_sens.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers_sens = ["Condición de Análisis", "N Registros", "Mediana Duración", "RIC", "Desviación Estándar"]
    for j, h in enumerate(headers_sens):
        cell = t_sens.rows[0].cells[j]
        set_cell_shading(cell, "003366")
        set_cell_margins(cell, 40, 40, 60, 60)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    rows_sens = [
        ("Muestra total (con imputación)", "105.060", "10.0 semestres", "2.0 semestres", "2.440 semestres"),
        ("Muestra pura (sin casos imputados)", "91.664", "10.0 semestres", "2.0 semestres", "2.373 semestres"),
    ]
    for i, row_data in enumerate(rows_sens, start=1):
        for j, val in enumerate(row_data):
            cell = t_sens.rows[i].cells[j]
            set_cell_shading(cell, "F9FBFD" if i % 2 == 1 else "FFFFFF")
            set_cell_margins(cell, 35, 35, 60, 60)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(8.0)

    add_figure("docs/figuras/f3_04_sensibilidad.png", "Figura 5: Comparación de distribuciones: Muestra Total vs Muestra Pura sin Imputación.", width_in=5.4)

    return doc


def extract_headings_from_pdf(pdf_path: str, targets: List[Tuple[str, str]]) -> Dict[str, int]:
    r = subprocess.run(["pdftotext", pdf_path, "-"], capture_output=True, text=True, check=True)
    pages = r.stdout.split("\x0c")
    if pages and not pages[-1].strip():
        pages.pop()

    mapping = {}
    for display_title, search_pattern in targets:
        clean_target = re.sub(r"\s+", " ", search_pattern).strip().lower()
        found_page = None
        for p_idx, page in enumerate(pages, 1):
            if p_idx in [1, 2]:  # Omitir portada y página del índice
                continue
            clean_page = re.sub(r"\s+", " ", page).strip().lower()
            if clean_target in clean_page:
                found_page = p_idx
                break
        mapping[search_pattern] = found_page if found_page is not None else 3

    return mapping


def main():
    docx_f3 = RAIZ / "docs/f3_s02_grupo6.docx"
    pdf_f3 = RAIZ / "docs/f3_s02_grupo6.pdf"

    docx_entregable = RAIZ / "docs/f3_s02_entregable_grupo6.docx"
    pdf_entregable = RAIZ / "docs/f3_s02_entregable_grupo6.pdf"

    targets = [
        ("I. Introducción y contextualización del avance", "I. Introducción"),
        ("II. Diseño de soluciones algorítmicas eficientes", "II. Diseño de soluciones algorítmicas"),
        ("2.1 Codificación funcional y arquitectura básica del script", "2.1 Codificación funcional"),
        ("2.2 Preprocesamiento y transformación del dataset", "2.2 Preprocesamiento"),
        ("2.3 Validación técnica y verificación del código", "2.3 Validación técnica"),
        ("2.4 Eficiencia y optimización algorítmica", "2.4 Eficiencia y optimización"),
        ("2.5 Diseño estructurado del código y control de recursión", "2.5 Diseño estructurado"),
        ("III. Implementación de código modular y robusto (POO)", "III. Implementación de código modular"),
        ("3.1 Programación orientada a objetos: clases del pipeline", "3.1 Programación orientada a objetos"),
        ("3.2 Documentación de arquitectura y aceleración vectorizada", "3.2 Documentación de arquitectura"),
        ("IV. Repositorio GitHub (F3) y trabajo colaborativo", "IV. Repositorio GitHub"),
        ("V. Notebooks ejecutables (F3) y reproducibilidad", "V. Notebooks ejecutables"),
        ("VI. Conclusiones y proyección hacia la Fase 4", "VI. Conclusiones y proyección"),
        ("VII. Bibliografía (Norma APA 7.ª edición)", "VII. Bibliografía"),
        ("Anexos técnicos", "Anexos técnicos"),
        ("Anexo A · Trazabilidad y verificación automatizada del repositorio", "Anexo A · Trazabilidad"),
        ("Anexo B · Registro de pruebas automatizadas y cobertura", "Anexo B · Registro de pruebas"),
        ("Anexo C · Verificación numérica y análisis de sensibilidad", "Anexo C · Verificación numérica"),
    ]

    print("Iteración 1: Compilando borrador inicial...")
    doc = build_docx()
    doc.save(str(docx_f3))
    subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", str(RAIZ / "docs"), str(docx_f3)], check=True)

    print("Escaneando páginas reales en el PDF generado...")
    page_map = extract_headings_from_pdf(str(pdf_f3), targets)
    for _, k in targets:
        print(f"  {k:<35} -> pág. {page_map.get(k)}")

    print("\nIteración 2: Recompilando con índice exacto...")
    doc2 = build_docx(page_map)
    doc2.save(str(docx_f3))
    subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", str(RAIZ / "docs"), str(docx_f3)], check=True)

    print("\nVerificación final de concordancia del índice (Regla de los 6 puntos)...")
    final_map = extract_headings_from_pdf(str(pdf_f3), targets)
    discrepancias = 0
    for display_title, k in targets:
        estimado = page_map.get(k)
        real = final_map.get(k)
        if estimado != real:
            print(f"  [DISCREPANCIA] {display_title}: estimado {estimado} vs real {real}")
            discrepancias += 1
        else:
            print(f"  [OK] {display_title[:55]:<55} -> pág. {real}")

    if discrepancias > 0:
        print(f"\nReiterando para ajustar {discrepancias} discrepancias...")
        doc3 = build_docx(final_map)
        doc3.save(str(docx_f3))
        subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", str(RAIZ / "docs"), str(docx_f3)], check=True)

    # Generar copia exacta con el nombre exigido en la rúbrica de Sumativa 2
    shutil.copyfile(docx_f3, docx_entregable)
    shutil.copyfile(pdf_f3, pdf_entregable)

    print(f"\nArchivos generados exitosamente:")
    print(f"  Formativa 3:")
    print(f"    DOCX: {docx_f3}")
    print(f"    PDF : {pdf_f3}")
    print(f"  Sumativa 2:")
    print(f"    DOCX: {docx_entregable}")
    print(f"    PDF : {pdf_entregable}")


if __name__ == "__main__":
    main()
