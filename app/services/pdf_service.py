import io
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from app.config import STATIC_DIR

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_watermark()
            self.draw_border()
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_watermark(self):
        self.saveState()
        self.setFont("Helvetica-Bold", 42)
        self.setFillColor(colors.Color(0.1, 0.2, 0.3, alpha=0.04))
        self.translate(A4[0] / 2.0, A4[1] / 2.0)
        self.rotate(35)
        self.drawCentredString(0, 0, "LEGAL METROLOGY VERIFIED")
        self.restoreState()

    def draw_border(self):
        self.saveState()
        self.setStrokeColor(colors.HexColor("#0F2942"))
        self.setLineWidth(2)
        self.rect(20, 20, A4[0] - 40, A4[1] - 40)
        self.setStrokeColor(colors.HexColor("#D97706"))
        self.setLineWidth(0.75)
        self.rect(24, 24, A4[0] - 48, A4[1] - 48)
        self.restoreState()

def generate_certificate_pdf(cert) -> io.BytesIO:
    """
    Generates a high-quality, authentic Form-VIII Legal Metrology Certificate PDF.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        alignment=1,
        textColor=colors.HexColor("#0F2942"),
        spaceAfter=3
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        alignment=1,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6
    )

    form_header_style = ParagraphStyle(
        'FormHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        alignment=1,
        textColor=colors.HexColor("#0F2942"),
        spaceAfter=12
    )

    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=13,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=8
    )

    elements = []

    # Header
    elements.append(Paragraph("GOVERNMENT OF INDIA", title_style))
    elements.append(Paragraph("MINISTRY OF CONSUMER AFFAIRS, FOOD & PUBLIC DISTRIBUTION<br/>DEPARTMENT OF CONSUMER AFFAIRS • LEGAL METROLOGY DIVISION", subtitle_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("<b>FORM - VIII: CERTIFICATE OF VERIFICATION</b><br/><font size=7.5 color='#64748B'>[Under Section 24 of Legal Metrology Act, 2009 & Rule 14(1) of Legal Metrology Rules, 2011]</font>", form_header_style))
    elements.append(Spacer(1, 6))

    # Meta banner table (Cert No, Issue, Expiry)
    meta_data = [
        [
            Paragraph(f"<b>Certificate No:</b> <font face='Courier-Bold'>{cert.certificate_number}</font>", body_style),
            Paragraph(f"<b>Stamping Date:</b> {cert.issue_date.strftime('%d-%b-%Y')}", body_style),
            Paragraph(f"<b>Valid Till:</b> <font color='#059669'><b>{cert.expiry_date.strftime('%d-%b-%Y')}</b></font>", body_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[200, 160, 160])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 10))

    # Legal clause text
    inst = cert.instrument
    insp = cert.inspection
    inspector = insp.inspector if insp else None

    legal_text = (
        f"I hereby certify that I have this day examined, tested and verified the commercial weighing/measuring instrument "
        f"detailed hereunder, belonging to <b>{inst.shop_name}</b>, situated at <b>{inst.shop_address}</b>, District <b>{inst.district}</b>, "
        f"State of <b>{inst.state}</b>, and found the same to be compliant with the standards prescribed under the "
        f"<b>Legal Metrology Act, 2009 (1 of 2010)</b> and the Legal Metrology (General) Rules, 2011."
    )
    elements.append(Paragraph(legal_text, body_style))
    elements.append(Spacer(1, 8))

    # Specifications Table
    spec_data = [
        [Paragraph("<b>Parameter</b>", body_style), Paragraph("<b>Statutory Details</b>", body_style)],
        [Paragraph("Instrument Category", body_style), Paragraph(inst.instrument_type, body_style)],
        [Paragraph("Brand Make & Model", body_style), Paragraph(inst.brand_make, body_style)],
        [Paragraph("Government Model Approval No.", body_style), Paragraph(f"<font face='Courier-Bold'>{inst.model_approval_number}</font>", body_style)],
        [Paragraph("Machine Hardware Serial Number", body_style), Paragraph(f"<font face='Courier-Bold'>{inst.serial_number}</font>", body_style)],
        [Paragraph("Maximum Approved Capacity", body_style), Paragraph(f"{inst.max_capacity} ({inst.accuracy_class})", body_style)],
        [Paragraph("Verification Tolerance (MPE)", body_style), Paragraph(f"Observed: ±{insp.max_error_observed} g (Permissible: ±{insp.permissible_error_limit} g)", body_style)],
        [Paragraph("On-Site GPS Verification Check-in", body_style), Paragraph(f"Verified physically on premises (Distance: {insp.distance_from_shop_meters} meters from shop GPS)", body_style)],
    ]

    spec_table = Table(spec_data, colWidths=[190, 330])
    spec_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#94A3B8")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(spec_table)
    elements.append(Spacer(1, 14))

    # Signatures and QR Code Footer
    qr_full_path = STATIC_DIR / cert.qr_code_filename.replace('/static/', '')
    qr_img = None
    if qr_full_path.exists():
        qr_img = RLImage(str(qr_full_path), width=1.1*inch, height=1.1*inch)

    footer_data = [
        [
            qr_img if qr_img else Paragraph("QR SEAL", body_style),
            Paragraph(
                f"<b>CRYPTOGRAPHIC INTEGRITY:</b><br/>"
                f"<font size=7 face='Courier' color='#0284C7'>SHA-256: {cert.data_hash[:32]}...</font><br/>"
                f"<font size=7 color='#64748B'>Under Section 24, using unverified or altered scales carries fines up to ₹25,000 and imprisonment.</font>",
                body_style
            ),
            Paragraph(
                f"<b>Digitally Signed By:</b><br/>"
                f"<b>{inspector.full_name if inspector else 'LMO Officer'}</b><br/>"
                f"<font size=7.5 color='#475569'>Legal Metrology Officer<br/>Badge: {inspector.badge_number if inspector else 'LMO-HQ'}</font>",
                body_style
            )
        ]
    ]

    footer_table = Table(footer_data, colWidths=[100, 260, 160])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEABOVE', (0,0), (-1,0), 1, colors.HexColor("#0F2942")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(footer_table)

    # Build PDF
    doc.build(elements, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer
