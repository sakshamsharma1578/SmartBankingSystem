from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import io


BRAND_DARK = colors.HexColor('#0A1628')
BRAND_BLUE = colors.HexColor('#1E40AF')
BRAND_ACCENT = colors.HexColor('#3B82F6')
BRAND_LIGHT = colors.HexColor('#EFF6FF')
BRAND_GRAY = colors.HexColor('#6B7280')


def generate_statement_pdf(account, transactions, start_date=None, end_date=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=0.75*inch, leftMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    elements = []

    # Header
    header_style = ParagraphStyle('Header', fontSize=24, fontName='Helvetica-Bold',
                                  textColor=BRAND_DARK, spaceAfter=2)
    sub_style = ParagraphStyle('Sub', fontSize=10, fontName='Helvetica',
                               textColor=BRAND_GRAY, spaceAfter=20)
    elements.append(Paragraph('SMARTBANK', header_style))
    elements.append(Paragraph('Secure Banking Management System', sub_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=BRAND_BLUE))
    elements.append(Spacer(1, 0.2*inch))

    # Account info
    elements.append(Paragraph('Account Statement', ParagraphStyle('Title', fontSize=16,
                                                                    fontName='Helvetica-Bold', textColor=BRAND_BLUE, spaceAfter=10)))

    acct_data = [
        ['Account Holder:', account.owner.full_name, 'Account Number:', account.account_number],
        ['Account Type:', account.account_type.title(), 'Current Balance:', f'${account.balance:,.2f}'],
        ['Account Status:', account.status.title(), 'Date Generated:', datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')],
    ]
    if start_date or end_date:
        date_range = f"{start_date or 'Beginning'} to {end_date or 'Present'}"
        acct_data.append(['Date Range:', date_range, '', ''])

    acct_table = Table(acct_data, colWidths=[1.4*inch, 2.0*inch, 1.5*inch, 2.1*inch])
    acct_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (-1, -1), BRAND_DARK),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(acct_table)
    elements.append(Spacer(1, 0.25*inch))

    # Summary stats
    total_deposits = sum(t.amount for t in transactions if t.transaction_type == 'deposit')
    total_withdrawals = sum(t.amount for t in transactions if t.transaction_type == 'withdrawal')
    total_transfers_out = sum(t.amount for t in transactions if t.transaction_type == 'transfer_out')
    total_transfers_in = sum(t.amount for t in transactions if t.transaction_type == 'transfer_in')

    summary_data = [
        ['Summary', '', '', ''],
        ['Total Deposits', f'${total_deposits:,.2f}', 'Total Withdrawals', f'${total_withdrawals:,.2f}'],
        ['Transfers In', f'${total_transfers_in:,.2f}', 'Transfers Out', f'${total_transfers_out:,.2f}'],
    ]
    summary_table = Table(summary_data, colWidths=[1.7*inch, 1.8*inch, 1.7*inch, 1.8*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('SPAN', (0, 0), (-1, 0)),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BACKGROUND', (0, 1), (-1, -1), BRAND_LIGHT),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 1), (2, -1), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.25*inch))

    # Transactions table
    elements.append(Paragraph('Transaction History', ParagraphStyle('SectionTitle', fontSize=13,
                                                                      fontName='Helvetica-Bold', textColor=BRAND_BLUE, spaceAfter=8)))

    txn_header = ['Date', 'Type', 'Description', 'Amount', 'Balance']
    txn_rows = [txn_header]

    for txn in transactions:
        amount_str = f'+${txn.amount:,.2f}' if txn.transaction_type in ('deposit', 'transfer_in') else f'-${txn.amount:,.2f}'
        txn_rows.append([
            txn.created_at.strftime('%Y-%m-%d %H:%M'),
            txn.transaction_type.replace('_', ' ').title(),
            (txn.description or '')[:35],
            amount_str,
            f'${txn.balance_after:,.2f}'
        ])

    if len(txn_rows) == 1:
        txn_rows.append(['No transactions found', '', '', '', ''])

    txn_table = Table(txn_rows, colWidths=[1.3*inch, 1.1*inch, 2.3*inch, 1.0*inch, 1.2*inch])
    txn_style = [
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (3, 0), (4, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#E5E7EB')),
    ]
    for i in range(1, len(txn_rows)):
        bg = BRAND_LIGHT if i % 2 == 0 else colors.white
        txn_style.append(('BACKGROUND', (0, i), (-1, i), bg))
        # Color amount column
        if len(txn_rows[i]) > 3 and txn_rows[i][3].startswith('+'):
            txn_style.append(('TEXTCOLOR', (3, i), (3, i), colors.HexColor('#059669')))
        elif len(txn_rows[i]) > 3 and txn_rows[i][3].startswith('-'):
            txn_style.append(('TEXTCOLOR', (3, i), (3, i), colors.HexColor('#DC2626')))

    txn_table.setStyle(TableStyle(txn_style))
    elements.append(txn_table)

    # Footer
    elements.append(Spacer(1, 0.3*inch))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=BRAND_GRAY))
    elements.append(Spacer(1, 0.1*inch))
    footer_style = ParagraphStyle('Footer', fontSize=7, fontName='Helvetica',
                                   textColor=BRAND_GRAY, alignment=TA_CENTER)
    elements.append(Paragraph(
        'This statement is auto-generated by SmartBank. For queries, contact support@smartbank.com',
        footer_style
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer
