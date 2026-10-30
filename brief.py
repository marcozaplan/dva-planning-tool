from datetime import date
from html import escape
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (HRFlowable, KeepTogether, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

BLUE = colors.HexColor("#00A6E6")
INK = colors.HexColor("#2B3A42")
MUTED = colors.HexColor("#7A868E")
RULE = colors.HexColor("#DDE3E7")
TINT = colors.HexColor("#E8F6FD")
ROLES = ["Primary", "Text", "Accent", "Background", "Highlight"]

W, H = A4
MARGIN = 18 * mm
WIDTH = W - 2 * MARGIN

body = ParagraphStyle("body", fontName="Helvetica", fontSize=10, leading=14, textColor=INK)
small = ParagraphStyle("small", parent=body, fontSize=8.5, leading=11)
empty = ParagraphStyle("empty", parent=body, fontName="Helvetica-Oblique", textColor=MUTED)
label = ParagraphStyle("label", parent=body, fontName="Helvetica-Bold", fontSize=7.5, leading=14, textColor=MUTED)
heading = ParagraphStyle("heading", parent=body, fontName="Helvetica-Bold", fontSize=13, leading=16)
question = ParagraphStyle("question", parent=body, fontName="Helvetica-Oblique", fontSize=9, textColor=MUTED)
quote = ParagraphStyle("quote", parent=body, fontName="Helvetica-Bold", fontSize=15, leading=20, textColor=INK)
banner = ParagraphStyle("banner", parent=body, fontName="Helvetica-Bold", fontSize=22, leading=26, textColor=colors.white)


def text(value, style=body):
    if isinstance(value, list):
        value = ", ".join(value)
    value = str(value or "").strip()
    if not value:
        return Paragraph("Not specified", ParagraphStyle("e", parent=empty, fontSize=style.fontSize))
    return Paragraph(escape(value).replace("\n", "<br/>"), style)


def pairs(rows):
    t = Table([[Paragraph(k.upper(), label), text(v)] for k, v in rows],
              colWidths=[36 * mm, WIDTH - 36 * mm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def section(n, title, ask, *content):
    head = [
        Spacer(1, 14),
        Paragraph(f'<font color="#00A6E6">{n:02d}</font>&nbsp;&nbsp;{title}', heading),
        Paragraph(ask, question),
        Spacer(1, 4),
        HRFlowable(width="100%", thickness=0.6, color=RULE, spaceAfter=8),
    ]
    return [KeepTogether(head + [content[0]])] + list(content[1:])


def data_table(rows):
    if not rows:
        return text("")
    cols = ["Dataset", "Source", "Period", "Notes"]
    data = [[Paragraph(f"<b>{c}</b>", small) for c in cols]]
    data += [[text(r.get(c), small) for c in cols] for r in rows]
    t = Table(data, colWidths=[w * WIDTH for w in (0.3, 0.3, 0.12, 0.28)], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TINT),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, RULE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def palette(hexes):
    names = [Paragraph(f"<b>{r}</b><br/>{h.upper()}", small) for r, h in zip(ROLES, hexes)]
    t = Table([[""] * 5, names], colWidths=[WIDTH / 5] * 5, rowHeights=[16 * mm, None])
    style = [("BACKGROUND", (i, 0), (i, 0), colors.HexColor(h)) for i, h in enumerate(hexes)]
    style += [("BOX", (0, 0), (-1, 0), 0.5, RULE),
              ("LEFTPADDING", (0, 1), (-1, 1), 0),
              ("TOPPADDING", (0, 1), (-1, 1), 5)]
    t.setStyle(TableStyle(style))
    return t


def key_fact(fact):
    t = Table([[Paragraph("THE ONE THING TO REMEMBER", label)], [text(fact, quote)]],
              colWidths=[WIDTH])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), TINT),
        ("LINEBEFORE", (0, 0), (0, -1), 3, BLUE),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 12),
    ]))
    return t


def footer(c, doc):
    c.saveState()
    c.setFont("Helvetica", 7.5)
    c.setFillColor(MUTED)
    c.drawString(MARGIN, 10 * mm, "Prepared with DVa, the data visualisation planning tool by Marco Zaplan & Eddie Shin (2016)")
    c.drawRightString(W - MARGIN, 10 * mm, f"Page {doc.page}")
    c.restoreState()


def build_pdf(b):
    project = b["project"].strip() or "Untitled visualisation"
    meta = " · ".join(x for x in [b["organisation"].strip(), f"Brief prepared {date.today():%d %B %Y}"] if x)

    def cover(c, doc):
        c.saveState()
        c.setFillColor(BLUE)
        c.rect(0, H - 50 * mm, W, 50 * mm, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(MARGIN, H - 16 * mm, "DATA VISUALISATION BRIEF")
        p = Paragraph(escape(project), banner)
        _, h = p.wrap(WIDTH, 30 * mm)
        p.drawOn(c, MARGIN, H - 21 * mm - h)
        c.setFont("Helvetica", 9)
        c.drawString(MARGIN, H - 27 * mm - h, meta)
        c.restoreState()
        footer(c, doc)

    deadline = b["deadline"]
    if isinstance(deadline, date):
        deadline = f"{deadline:%d %B %Y}"

    story = [
        Spacer(1, 36 * mm),
        pairs([
            ("Deliverable", b["format"]),
            ("Deadline", deadline),
            ("Contact", b["contact"]),
            ("Working title", b["title"]),
        ]),
        Spacer(1, 6),
    ]
    if b["fact"].strip():
        story.append(key_fact(b["fact"]))

    story += section(1, "Objective", "Why are we making this?",
                     pairs([("Purpose", b["objective"])]))
    story += section(2, "Data", "What data do we have to deliver the message?",
                     data_table(b["data"]))
    story += section(3, "Audience", "Who are we targeting?",
                     pairs([("Who", b["audience"]),
                            ("Data familiarity", b["literacy"]),
                            ("Languages", b["languages"])]))
    story += section(4, "Key fact", "What is the interesting, relevant fact our users care about?",
                     pairs([("Fact", b["fact"])]))
    story += section(5, "Story", "What is the story we want to deliver?",
                     pairs([("Story", b["story"]), ("Takeaway", b["takeaway"])]))
    story += section(6, "What to show", "From the data, what should be visually presented?",
                     pairs([("Elements", b["elements"]), ("Chart types", b["charts"])]))
    story += section(7, "Visual direction", "Layout, type, colour and text.",
                     pairs([("Title", b["title"]),
                            ("Subtitle", b["subtitle"]),
                            ("Orientation", b["orientation"]),
                            ("Layout", b["layout"]),
                            ("Heading font", b["heading_font"]),
                            ("Body font", b["body_font"])]),
                     Spacer(1, 4),
                     Paragraph("COLOUR SCHEME", label),
                     Spacer(1, 4),
                     palette(b["colors"]))
    story += section(8, "Distribution", "How do we reach our users?",
                     pairs([("Channels", b["channels"]),
                            ("Sizes and specs", b["dimensions"]),
                            ("Plan", b["distribution"])]))

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
                            topMargin=MARGIN, bottomMargin=20 * mm,
                            title=f"{project} — data visualisation brief", author=b["contact"] or "DVa")
    doc.build(story, onFirstPage=cover, onLaterPages=footer)
    return buf.getvalue()
