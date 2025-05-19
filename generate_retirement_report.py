from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def create_retirement_report():
    # Create the PDF document
    doc = SimpleDocTemplate(
        "retirement_analysis_report.pdf",
        pagesize=letter,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    styles = getSampleStyleSheet()
    elements = []

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2C3E50')
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#34495E')
    )

    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=18,
        spaceBefore=20,
        spaceAfter=15,
        textColor=colors.HexColor('#2C3E50')
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12,
        textColor=colors.HexColor('#34495E'),
        alignment=TA_JUSTIFY
    )

    # Add main title and subtitle
    elements.append(Paragraph("Retirement Planning Analysis Report", title_style))
    elements.append(Paragraph(
        "A comprehensive analysis of retirement planning strategies and considerations",
        subtitle_style
    ))
    elements.append(Spacer(1, 20))

    # Add introduction
    elements.append(Paragraph("Introduction", section_title_style))
    intro_text = """
    This report provides a comprehensive analysis of retirement planning strategies, focusing on different retirement age scenarios and their implications. 
    The analysis takes into account various factors including savings requirements, investment strategies, and lifestyle considerations.
    """
    elements.append(Paragraph(intro_text, body_style))
    elements.append(Spacer(1, 20))

    # Add Retirement Age Comparison section
    elements.append(Paragraph("Retirement Age Comparison Analysis", section_title_style))
    elements.append(Paragraph(
        "The following table illustrates different retirement age scenarios and their key considerations:",
        body_style
    ))
    elements.append(Spacer(1, 10))

    # Table data with improved formatting
    data = [
        ['Retirement Age', 'Years to Retirement', 'Potential Retirement Length', 'Savings Needed', 'Key Considerations'],
        ['60', '42', '25 years', 'Significantly Higher', 
         '• Requires very aggressive saving and investment strategies\n• May involve higher risk tolerance\n• Early retirement benefits'],
        ['65', '47', '20 years', 'Higher',
         '• Still requires substantial saving, but less pressure than retiring at 60\n• A balanced investment approach may be suitable\n• Standard retirement age benefits'],
        ['70', '52', '15 years', 'Moderate',
         '• More years to accumulate savings and fewer years in retirement\n• Allows for a more conservative investment approach\n• May not be feasible depending on health and job market\n• Higher social security benefits'],
        ['75', '57', '10 years', 'Lower',
         '• Most years to accumulate savings\n• May require working later in life\n• Potential health considerations\n• Maximum social security benefits']
    ]

    # Create table with adjusted column widths
    table = Table(data, colWidths=[1.2*inch, 1.5*inch, 1.5*inch, 1.5*inch, 3*inch])
    
    # Enhanced table style
    table_style = TableStyle([
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        
        # Body styling
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2C3E50')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        
        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9F9')]),
    ])
    table.setStyle(table_style)
    elements.append(table)

    # Add analysis section
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Analysis and Recommendations", section_title_style))
    analysis_text = """
    Based on the retirement age comparison analysis, several key insights emerge:

    1. Early Retirement (Age 60):
       • Requires the most aggressive saving strategy
       • Offers longest retirement period but highest financial pressure
       • Suitable for those with high income and strong investment portfolio

    2. Standard Retirement (Age 65):
       • Provides a balanced approach to retirement planning
       • Allows for moderate saving rates and investment strategies
       • Most common retirement age with established benefits

    3. Late Retirement (Age 70-75):
       • Offers more time for wealth accumulation
       • May provide higher social security benefits
       • Requires consideration of health and work capacity
    """
    elements.append(Paragraph(analysis_text, body_style))

    # Add notes section with improved styling
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Important Considerations", section_title_style))
    notes_style = ParagraphStyle(
        'Notes',
        parent=styles['Normal'],
        fontSize=11,
        spaceBefore=5,
        spaceAfter=5,
        textColor=colors.HexColor('#34495E'),
        bulletIndent=20
    )
    
    notes = [
        "• This analysis provides illustrative examples and general concepts for retirement planning",
        "• Actual savings needed will depend on individual circumstances, income, and lifestyle goals",
        "• Life expectancy is assumed to be 85 years for calculation purposes",
        "• Investment returns and inflation are not factored into these calculations",
        "• Social security benefits and other retirement income sources should be considered",
        "• Regular review and adjustment of retirement plans is recommended"
    ]
    
    for note in notes:
        elements.append(Paragraph(note, notes_style))

    # Add disclaimer
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=9,
        spaceBefore=20,
        textColor=colors.HexColor('#7F8C8D'),
        alignment=TA_CENTER
    )
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        "This report is for informational purposes only and should not be considered as financial advice. Please consult with a financial advisor for personalized retirement planning.",
        disclaimer_style
    ))

    # Build the PDF
    doc.build(elements)

if __name__ == "__main__":
    create_retirement_report() 