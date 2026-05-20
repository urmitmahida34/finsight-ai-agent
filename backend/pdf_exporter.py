import re
from datetime import datetime

from fpdf import FPDF


class ReportPDF(FPDF):
    def __init__(self, company: str, ticker: str):
        super().__init__()
        self.company = company
        self.ticker = ticker
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_fill_color(30, 58, 138)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, f"  FinSight AI  |  {self.company} ({self.ticker})  |  Investment Research Report", fill=True, ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"FinSight AI  |  {datetime.now().strftime('%d %b %Y')}  |  Not Financial Advice  |  Page {self.page_no()}", align="C")

    def section_header(self, title: str):
        self.ln(3)
        self.set_font("Helvetica", "B", 11)
        self.set_fill_color(239, 246, 255)
        self.set_text_color(30, 58, 138)
        self.cell(0, 8, f"  {title}", fill=True, ln=True)
        self.set_text_color(40, 40, 40)
        self.ln(1)

    def body(self, text: str):
        self.set_font("Helvetica", "", 9)
        clean = text.encode("latin-1", errors="replace").decode("latin-1")
        self.multi_cell(0, 5, clean)
        self.ln(1)


def _strip_md(text: str) -> str:
    text = re.sub(r"#{1,6}\s+", "", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = re.sub(r"^\s*[-*]\s+", "• ", text, flags=re.MULTILINE)
    return text


def generate_pdf(report_md: str, company: str, ticker: str) -> bytes:
    pdf = ReportPDF(company, ticker)
    pdf.add_page()

    current_body: list[str] = []

    def flush():
        body = "\n".join(current_body).strip()
        if body:
            pdf.body(_strip_md(body))
        current_body.clear()

    for line in report_md.split("\n"):
        if re.match(r"^#{1,3}\s+", line):
            flush()
            pdf.section_header(re.sub(r"^#+\s+", "", line).strip())
        else:
            current_body.append(line)

    flush()
    return bytes(pdf.output())
