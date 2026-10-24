import os
import subprocess
import sys
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class PDFReceiptGenerator:
    @staticmethod
    def generar_comprobante_cita(detalle_cita: dict) -> str:
        os.makedirs("comprobantes_pdf", exist_ok=True)
        folio = f"PC-{detalle_cita['id']:05d}"
        filename = os.path.join("comprobantes_pdf", f"Comprobante_{folio}.pdf")

        doc = SimpleDocTemplate(
            filename,
            pagesize=letter,
            rightMargin=45,
            leftMargin=45,
            topMargin=45,
            bottomMargin=45,
        )
        elements = []
        styles = getSampleStyleSheet()

        COLOR_TURQUESA = colors.HexColor("#008B8B")
        COLOR_MENTA = colors.HexColor("#E0F2F1")
        COLOR_NARANJA = colors.HexColor("#FF7F50")
        COLOR_TEXTO = colors.HexColor("#1E293B")

        title_style = ParagraphStyle(
            "VetTitle",
            parent=styles["Heading1"],
            fontSize=20,
            textColor=COLOR_TURQUESA,
            spaceAfter=4,
        )
        subtitle_style = ParagraphStyle(
            "VetSub",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#64748B"),
            spaceAfter=16,
        )

        elements.append(Paragraph("CLÍNICA VETERINARIA PETCARE ENTERPRISE", title_style))
        elements.append(
            Paragraph(
                f"Comprobante Oficial de Cita y Servicio Médico | Emitido: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                subtitle_style,
            )
        )

        header_data = [
            ["FOLIO DE ATENCIÓN", "FECHA PROGRAMADA", "HORA", "ESTADO ACTUAL"],
            [
                folio,
                detalle_cita.get("fecha", ""),
                detalle_cita.get("hora", ""),
                detalle_cita.get("estado", "Programada").upper(),
            ],
        ]
        header_table = Table(header_data, colWidths=[130, 130, 100, 150])
        header_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), COLOR_TURQUESA),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("BACKGROUND", (0, 1), (-1, 1), COLOR_MENTA),
                    ("TEXTCOLOR", (0, 1), (-1, 1), COLOR_TEXTO),
                    ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOX", (0, 0), (-1, -1), 1, COLOR_TURQUESA),
                ]
            )
        )
        elements.append(header_table)
        elements.append(Spacer(1, 18))

        body_data = [
            ["DATOS DEL PROPIETARIO (CLIENTE)", "DATOS DEL PACIENTE (MASCOTA)"],
            [
                f"Nombre: {detalle_cita.get('dueno_nombre', '')}\n"
                f"Teléfono: {detalle_cita.get('dueno_telefono', '')}\n"
                f"Domicilio: {detalle_cita.get('dueno_domicilio', '')}",
                f"Nombre: {detalle_cita.get('mascota_nombre', '')} ({detalle_cita.get('especie', 'Mascota')})\n"
                f"Raza: {detalle_cita.get('raza', '')} | Edad: {detalle_cita.get('edad', '')}\n"
                f"Alergias: {detalle_cita.get('alergias', 'Ninguna')}\n"
                f"Vacunas: {detalle_cita.get('vacunas', 'Al día')}",
            ],
        ]
        body_table = Table(body_data, colWidths=[255, 255])
        body_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), COLOR_NARANJA),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("PADDING", (0, 0), (-1, -1), 10),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        elements.append(body_table)
        elements.append(Spacer(1, 18))

        clinical_data = [
            ["MOTIVO DE LA CONSULTA / SERVICIO REGISTRADO"],
            [detalle_cita.get("motivo", "Consulta general")],
            ["NOTAS CLÍNICAS / DIAGNÓSTICO"],
            [detalle_cita.get("notas_clinicas") or "Sin observaciones adicionales registradas."],
        ]
        clinical_table = Table(clinical_data, colWidths=[510])
        clinical_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), COLOR_TURQUESA),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BACKGROUND", (0, 2), (-1, 2), COLOR_TURQUESA),
                    ("TEXTCOLOR", (0, 2), (-1, 2), colors.white),
                    ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
                    ("PADDING", (0, 0), (-1, -1), 9),
                    ("BOX", (0, 0), (-1, -1), 1, COLOR_TURQUESA),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ]
            )
        )
        elements.append(clinical_table)
        elements.append(Spacer(1, 35))

        footer_style = ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontSize=9,
            alignment=1,
            textColor=colors.HexColor("#64748B"),
        )
        elements.append(
            Paragraph(
                "Gracias por confiar la salud de su mascota a PetCare Enterprise. Presente este comprobante al llegar a recepción.",
                footer_style,
            )
        )

        doc.build(elements)

        try:
            if sys.platform.startswith("win"):
                os.startfile(filename)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", filename])
            else:
                subprocess.Popen(["xdg-open", filename])
        except Exception:
            pass

        return filename