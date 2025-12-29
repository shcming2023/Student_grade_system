
import os

file_path = '/opt/Way To Future考试管理系统/Student_grade_system/wtf_app_simple.py'

with open(file_path, 'r') as f:
    lines = f.readlines()

# Find the function definition
start_line = -1
end_line = -1

for i, line in enumerate(lines):
    if line.strip().startswith('def generate_report_card_pdf('):
        start_line = i
        break

if start_line != -1:
    # Find the end of the function (look for the next function definition or EOF)
    # Actually, we can look for the "except Exception as e:" block and the return None inside it
    # My previous read showed it ends at 1474 (return None) inside the except block.
    # The next function starts at 1476 (@app.route).
    for i in range(start_line + 1, len(lines)):
        if line.strip().startswith('@app.route'):
             # This is NOT the next function, but the decorator of the next function.
             pass
        if lines[i].startswith('@app.route') or lines[i].startswith('def '):
            end_line = i
            break
    
    # If not found (last function), go to end
    if end_line == -1:
        end_line = len(lines)
        
    # Check if there are decorators above the next function that we shouldn't overwrite
    # The read output shows:
    # 1474->        return None
    # 1475->
    # 1476->@app.route(...)
    # So we should stop before @app.route
    
    # Let's verify end_line
    print(f"Replacing lines {start_line} to {end_line}")
    
    new_content = r'''def generate_report_card_pdf(student_id, exam_session_id, template_id=None):
    """生成学生成绩单PDF"""
    print(f"DEBUG: Generating PDF for student {student_id}, session {exam_session_id}, template {template_id} - NEW LOGIC v3")
    try:
        # 注册中文字体
        try:
            pdfmetrics.registerFont(TTFont('DroidSansFallback', '/usr/share/fonts/google-droid/DroidSansFallback.ttf'))
            font_name = 'DroidSansFallback'
        except Exception:
            font_name = 'Helvetica' # Fallback
            
        # 获取学生信息 (支持 ID 或 学号)
        student = Student.query.get(student_id)
        if not student:
            # 尝试按学号查找
            student = Student.query.filter_by(student_id=str(student_id)).first()
            
        if not student:
            print(f"Student not found: {student_id}")
            return None
            
        # 获取考试场次信息
        exam_session = ExamSession.query.get(exam_session_id)
        
        # 获取该场次下该学生的所有报名信息
        query = db.session.query(ExamRegistration, ExamTemplate, Subject)\
            .join(ExamTemplate, ExamRegistration.exam_template_id == ExamTemplate.id)\
            .join(Subject, ExamTemplate.subject_id == Subject.id)\
            .filter(ExamRegistration.student_id == student.id)\
            .filter(ExamRegistration.exam_session_id == exam_session_id)
            
        if template_id:
            query = query.filter(ExamTemplate.id == template_id)
            
        registrations = query.all()
        
        if not registrations:
            return None
            
        # 创建PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                              rightMargin=20*mm, leftMargin=20*mm,
                              topMargin=20*mm, bottomMargin=20*mm)
        
        story = []
        styles = getSampleStyleSheet()
        
        # 自定义样式
        title_style = styles['Title']
        title_style.fontName = font_name
        title_style.fontSize = 24
        title_style.leading = 30
        title_style.alignment = 1  # Center
        
        heading_style = styles['Heading3']
        heading_style.fontName = font_name
        heading_style.fontSize = 14
        heading_style.textColor = colors.HexColor('#000000')
        heading_style.backColor = colors.HexColor('#E0E0E0') # Light grey background for section headers
        heading_style.borderPadding = (5, 2, 5, 2)
        heading_style.spaceBefore = 12
        heading_style.spaceAfter = 6
        
        normal_style = styles['Normal']
        normal_style.fontName = font_name
        normal_style.fontSize = 10
        normal_style.leading = 14
        
        small_style = styles['Normal']
        small_style.fontName = font_name
        small_style.fontSize = 9
        small_style.leading = 12

        # 遍历每门科目 (生成一页)
        for exam_reg, template, subject in registrations:
            if exam_reg != registrations[0][0]:
                story.append(PageBreak())
                
            # --- Header (Logo) ---
            # 预留 Logo 区域 (Left aligned logo, Right aligned text)
            header_data = [
                ['Way To Future IV', '', '橡心国际'] # Placeholder for Image
            ]
            header_table = Table(header_data, colWidths=[60*mm, 60*mm, 70*mm])
            header_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#333333')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            story.append(header_table)
            story.append(Spacer(1, 15))
            
            # --- 标题 ---
            story.append(Paragraph(f"{exam_session.name}成绩单", title_style))
            story.append(Spacer(1, 20))
            
            # --- 1. 基本信息 (Basic Info) ---
            # 考生姓名、测评名称（试卷名称）、测评时间
            story.append(Paragraph("基本信息", heading_style))
            story.append(Spacer(1, 5))
            
            basic_info_data = [
                ['考生姓名：', student.name, '测评名称：', template.name],
                ['测评时间：', exam_session.exam_date.strftime('%Y-%m-%d'), '科目：', subject.name]
            ]
            
            basic_info_table = Table(basic_info_data, colWidths=[30*mm, 50*mm, 30*mm, 80*mm])
            basic_info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.grey), # Label color
                ('TEXTCOLOR', (2, 0), (2, -1), colors.grey),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(basic_info_table)
            story.append(Spacer(1, 10))
            
            # --- 2. 测评明细 (Detailed Scores) ---
            # 双栏显示：总宽 ~190mm -> 每栏 ~90mm
            story.append(Paragraph("测评明细", heading_style))
            story.append(Spacer(1, 5))
            
            scores = db.session.query(Score, Question)\
                .join(Question, Score.question_id == Question.id)\
                .filter(Score.student_id == student.id)\
                .filter(Question.exam_template_id == template.id)\
                .all()
            
            # 无论有无成绩，都显示区域
            if scores:
                try:
                    scores.sort(key=lambda x: int(x[1].question_number) if x[1].question_number.isdigit() else x[1].question_number)
                except:
                    pass

                # 准备数据行
                detail_rows = []
                total_score = 0
                total_possible = 0
                correct_count = 0
                
                for score, question in scores:
                    is_correct_text = '正确' if score.is_correct else '错误'
                    color = colors.green if score.is_correct else colors.red
                    
                    if score.is_correct:
                        correct_count += 1
                    total_score += float(score.score)
                    total_possible += float(question.score)
                    
                    # Row: No., Module, Knowledge, Result
                    detail_rows.append([
                        f"Q{question.question_number}",
                        Paragraph(question.module or '-', small_style),
                        Paragraph(question.knowledge_point or '-', small_style),
                        Paragraph(f'<font color="{color}">{is_correct_text}</font>', small_style)
                    ])

                # Split into two columns
                mid_point = (len(detail_rows) + 1) // 2
                left_rows = detail_rows[:mid_point]
                right_rows = detail_rows[mid_point:]
                
                # Combine into one table structure
                # Header: [No, Mod, Know, Res] | Spacer | [No, Mod, Know, Res]
                header_row = ['题号', '模块', '知识点', '结果', '', '题号', '模块', '知识点', '结果']
                combined_data = [header_row]
                
                for i in range(len(left_rows)):
                    left = left_rows[i]
                    right = right_rows[i] if i < len(right_rows) else ['', '', '', '']
                    combined_data.append(left + [''] + right)
                
                # Column widths
                # 15, 20, 40, 15 | 5 | 15, 20, 40, 15 = 185mm total
                col_widths = [12*mm, 18*mm, 45*mm, 15*mm, 5*mm, 12*mm, 18*mm, 45*mm, 15*mm]
                
                detail_table = Table(combined_data, colWidths=col_widths)
                detail_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), font_name),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    # Header style
                    ('BACKGROUND', (0, 0), (3, 0), colors.HexColor('#F5F5F5')),
                    ('BACKGROUND', (5, 0), (8, 0), colors.HexColor('#F5F5F5')),
                    ('LINEBELOW', (0, 0), (3, 0), 1, colors.black),
                    ('LINEBELOW', (5, 0), (8, 0), 1, colors.black),
                    # Borders for left block
                    ('GRID', (0, 0), (3, -1), 0.5, colors.grey),
                    # Borders for right block
                    ('GRID', (5, 0), (8, -1), 0.5, colors.grey),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                ]))
                story.append(detail_table)
            else:
                story.append(Paragraph("暂无测评明细数据", normal_style))
                
            story.append(Spacer(1, 15))
            
            # --- 3. 测评分析 (Analysis) ---
            story.append(Paragraph("测评分析", heading_style))
            story.append(Spacer(1, 5))
            
            if scores:
                total_questions = len(scores)
                incorrect_count = total_questions - correct_count
                accuracy_pct = (correct_count / total_questions * 100) if total_questions > 0 else 0
            else:
                total_questions = 0
                correct_count = 0
                incorrect_count = 0
                accuracy_pct = 0
            
            # 3.1 Data Grid
            analysis_data = [
                ['测评总题数', '正确题数', '错误题数', '正确率'],
                [str(total_questions), str(correct_count), str(incorrect_count), f"{accuracy_pct:.1f}%"]
            ]
            
            analysis_table = Table(analysis_data, colWidths=[47.5*mm]*4)
            analysis_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F0F8FF')), # Light AliceBlue
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(analysis_table)
            story.append(Spacer(1, 15))
            
            # --- 4. 教师评价 (Teacher Comment) ---
            story.append(Paragraph("教师评价", heading_style))
            story.append(Spacer(1, 5))
            
            # Create a box for comments
            # Check if comment exists
            report_card = ReportCard.query.filter_by(registration_id=exam_reg.id).first()
            comment_text = ""
            if report_card and (report_card.teacher_comment or report_card.ai_comment):
                comment_text = report_card.teacher_comment or report_card.ai_comment
            
            # Empty box with height
            comment_data = [[Paragraph(comment_text, normal_style)]]
            comment_table = Table(comment_data, colWidths=[190*mm], rowHeights=[40*mm])
            comment_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ]))
            story.append(comment_table)
            
            # Footer
            story.append(Spacer(1, 10))
            story.append(Paragraph("Way To Future - 橡心国际教育", small_style))
            
            story.append(Spacer(1, 20))
        
        # 生成PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
        
    except Exception as e:
        print(f"生成PDF错误: {e}")
        import traceback
        traceback.print_exc()
        return None
'''
    
    if not new_content.endswith('\n'):
        new_content += '\n'
        
    lines[start_line:end_line] = [new_content]
    
    with open(file_path, 'w') as f:
        f.writelines(lines)
    
    print("Successfully replaced function.")
else:
    print("Function not found.")
