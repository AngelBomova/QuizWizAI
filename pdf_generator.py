from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime

def generate_quiz_pdf(topic, difficulty, score, total_questions, percentage, questions, user_answers):
    """Generate a PDF report of quiz results"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=12,
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=8
    )
    
    # Title
    elements.append(Paragraph("🧠 AI Quiz Results", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Quiz Info
    info_data = [
        ["Topic:", topic],
        ["Difficulty:", difficulty.capitalize()],
        ["Date:", datetime.now().strftime("%Y-%m-%d %H:%M")],
        ["Score:", f"{score}/{total_questions}"],
        ["Percentage:", f"{percentage:.1f}%"]
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Performance Grade
    if percentage >= 80:
        grade = "🏆 Excellent!"
        grade_color = colors.green
    elif percentage >= 60:
        grade = "👍 Good!"
        grade_color = colors.blue
    else:
        grade = "📚 Keep Learning!"
        grade_color = colors.orange
    
    grade_style = ParagraphStyle(
        'Grade',
        parent=styles['Normal'],
        fontSize=16,
        textColor=grade_color,
        alignment=1,
        spaceAfter=12
    )
    elements.append(Paragraph(f"<b>{grade}</b>", grade_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Detailed Results
    elements.append(Paragraph("Detailed Results", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    for i, (question_data, user_answer) in enumerate(zip(questions, user_answers)):
        # Question number and text
        q_text = f"<b>Question {i+1}:</b> {question_data['question']}"
        elements.append(Paragraph(q_text, styles['Normal']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Options with indicators
        options_data = []
        for j, option in enumerate(question_data["options"]):
            option_letter = chr(65 + j)
            
            if j == question_data["correct_answer"]:
                if j == user_answer:
                    # Correct answer selected by user
                    options_data.append([f"✅ {option_letter}.", option, "Your answer - Correct!"])
                else:
                    # Correct answer not selected
                    options_data.append([f"✅ {option_letter}.", option, "Correct answer"])
            elif j == user_answer:
                # Wrong answer selected by user
                options_data.append([f"❌ {option_letter}.", option, "Your answer - Incorrect"])
            else:
                # Other options
                options_data.append([f"{option_letter}.", option, ""])
        
        options_table = Table(options_data, colWidths=[0.5*inch, 4*inch, 1.5*inch])
        options_table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        elements.append(options_table)
        elements.append(Spacer(1, 0.1*inch))
        
        # Explanation
        exp_text = f"<b>Explanation:</b> {question_data['explanation']}"
        elements.append(Paragraph(exp_text, styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Add page break after every 3 questions to avoid overflow
        if (i + 1) % 3 == 0 and i < len(questions) - 1:
            elements.append(PageBreak())
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
