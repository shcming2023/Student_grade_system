
import os

file_path = '/opt/Way To Future考试管理系统/Student_grade_system/wtf_app_simple.py'

new_function = r'''def generate_report_card_pdf(student_id, exam_session_id, template_id=None):
    """生成学生成绩单PDF - Refactored v5 (Beautified)"""
    print(f"DEBUG: Generating PDF for student {student_id}, session {exam_session_id}, template {template_id} - NEW LOGIC v5")
    try:
        # 注册中文字体
        try:
            pdfmetrics.registerFont(TTFont('DroidSansFallback', '/usr/share/fonts/google-droid/DroidSansFallback.ttf'))
            font_name = 'DroidSansFallback'
        except Exception:
            font_name = 'Helvetica' # Fallback
            
        # 获取学生信息
        student = Student.query.get(student_id)
        if not student:
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
        # Reduce margins slightly to give more space
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                              rightMargin=15*mm, leftMargin=15*mm,
                              topMargin=15*mm, bottomMargin=15*mm)
        
        story = []
        styles = getSampleStyleSheet()
        
        # 自定义样式
        # Title Style
        title_style = styles['Title']
        title_style.fontName = font_name
        title_style.fontSize = 22
        title_style.leading = 28
        title_style.alignment = 1  # Center
        title_style.spaceAfter = 10
        
        # Section Heading Style
        heading_style = styles['Heading3']
        heading_style.fontName = font_name
        heading_style.fontSize = 14
        heading_style.textColor = colors.HexColor('#333333')
        # Remove background for cleaner look, or use very light grey
        # heading_style.backColor = colors.HexColor('#F5F5F5') 
        heading_style.borderPadding = 0
        heading_style.spaceBefore = 15
        heading_style.spaceAfter = 8
        
        # Normal Text Style
        normal_style = styles['Normal']
        normal_style.fontName = font_name
        normal_style.fontSize = 10
        normal_style.leading = 14
        
        # Small Text Style
        small_style = styles['Normal']
        small_style.fontName = font_name
        small_style.fontSize = 9
        small_style.leading = 12
        
        # Header Styles
        header_left_style = styles['Normal']
        header_left_style.fontName = font_name
        header_left_style.fontSize = 11
        header_left_style.alignment = 0 # Left
        
        header_center_style = styles['Normal']
        header_center_style.fontName = font_name
        header_center_style.fontSize = 14
        header_center_style.alignment = 1 # Center
        header_center_style.fontName = font_name # Bold if possible? TTFont usually regular.
        
        # Get System Settings and Session Settings
        setting = SystemSetting.query.first()
        system_company_name_zh = setting.company_name_zh if setting else '橡心国际'
        system_logo_path = setting.logo_path if setting else None
        
        # Determine Header Content
        header_left_text = exam_session.exam_name_en or 'Way To Future'
        header_middle_text = exam_session.company_brand or system_company_name_zh
        
        # Prepare Logo
        header_right_logo = ''
        if system_logo_path:
             abs_logo_path = os.path.join(app.static_folder, system_logo_path)
             if os.path.exists(abs_logo_path):
                 try:
                     # Create Image object, max height 15mm
                     img = Image(abs_logo_path)
                     img_height = 12*mm
                     img.drawHeight = img_height
                     img.drawWidth = img_height * (img.imageWidth / img.imageHeight)
                     header_right_logo = img
                 except:
                     pass

        # 遍历每门科目 (生成一页)
        for exam_reg, template, subject in registrations:
            if exam_reg != registrations[0][0]:
                story.append(PageBreak())
                
            # --- Header (Logo) ---
            # 3 Columns: Left (EN Name), Center (Brand), Right (Logo)
            # Widths: Total ~180mm. 50, 80, 50
            header_data = [[
                Paragraph(header_left_text, header_left_style), 
                Paragraph(header_middle_text, header_center_style), 
                header_right_logo
            ]]
            
            header_table = Table(header_data, colWidths=[55*mm, 70*mm, 55*mm])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
            ]))
            story.append(header_table)
            story.append(Spacer(1, 15))
            
            # --- Title ---
            # Format: "{Company} - {Template Name} - 测评报告"
            # e.g. "橡心国际 - G2中数 - 测评报告"
            report_title = f"{header_middle_text} - {template.name} - 测评报告"
            story.append(Paragraph(report_title, title_style))
            story.append(Spacer(1, 15))
            
            # --- Basic Info (Compact Row) ---
            # 考生姓名、测评名称、测评时间
            # Use bold for labels
            basic_info_data = [
                [
                    Paragraph(f"<b>考生姓名：</b> {student.name}", normal_style),
                    Paragraph(f"<b>测评名称：</b> {template.name}", normal_style),
                    Paragraph(f"<b>测评时间：</b> {exam_session.exam_date.strftime('%Y-%m-%d')}", normal_style)
                ]
            ]
            
            basic_info_table = Table(basic_info_data, colWidths=[60*mm, 60*mm, 60*mm])
            basic_info_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                # Add a light border or background to separate?
                # Let's keep it clean as requested, maybe just bottom line
                # ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.grey),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            story.append(basic_info_table)
            # story.append(Spacer(1, 10))
            
            # --- Analysis Section ---
            story.append(Paragraph("测评分析", heading_style))
            # Draw a line under heading?
            # story.append(Drawing(width=180*mm, height=1)) # Line
            
            # Fetch Questions
            questions = Question.query.filter_by(exam_template_id=template.id).all()
            
            # Natural Sort
            def natural_sort_key(q):
                import re
                parts = re.split(r'(\d+)', q.question_number)
                return [int(p) if p.isdigit() else p for p in parts]
            questions.sort(key=natural_sort_key)
            
            # Fetch Scores
            q_ids = [q.id for q in questions]
            scores_map = {} 
            if q_ids:
                found_scores = Score.query.filter(
                    Score.student_id == student.id,
                    Score.question_id.in_(q_ids)
                ).all()
                scores_map = {s.question_id: s for s in found_scores}
            
            # Build Detail Data
            detail_rows = []
            total_score = 0
            correct_count = 0
            
            for q in questions:
                score_obj = scores_map.get(q.id)
                if score_obj:
                    # is_correct_text = '√' if score_obj.is_correct else '×'
                    is_correct_text = '正确' if score_obj.is_correct else '错误'
                    color = colors.green if score_obj.is_correct else colors.red
                    if score_obj.is_correct:
                        correct_count += 1
                    total_score += float(score_obj.score)
                else:
                    is_correct_text = '-'
                    color = colors.black
                
                # Truncate knowledge point if too long?
                kp = q.knowledge_point or '-'
                if len(kp) > 15: kp = kp[:14] + '...'
                
                detail_rows.append([
                    f"Q{q.question_number}",
                    Paragraph(q.module or '-', small_style),
                    Paragraph(kp, small_style),
                    Paragraph(f'<font color="{color}">{is_correct_text}</font>', small_style)
                ])

            # Layout: 2 Columns side by side
            mid = (len(detail_rows) + 1) // 2
            left_data = detail_rows[:mid]
            right_data = detail_rows[mid:]
            
            # Pad right data if shorter
            while len(right_data) < len(left_data):
                right_data.append(['', '', '', ''])
                
            # Combine
            # Header: [Q, Mod, KP, Res] spacer [Q, Mod, KP, Res]
            header_row = ['题号', '模块', '知识点', '结果', '', '题号', '模块', '知识点', '结果']
            
            table_data = [header_row]
            for l, r in zip(left_data, right_data):
                table_data.append(l + [''] + r)
                
            # Widths: 
            # Total ~180mm. Gap 5mm. Left 87.5mm, Right 87.5mm.
            # Col: 12, 20, 40, 15.5
            col_w = [12*mm, 20*mm, 40*mm, 15.5*mm]
            gap_w = 5*mm
            full_col_widths = col_w + [gap_w] + col_w
            
            detail_table = Table(table_data, colWidths=full_col_widths, repeatRows=1)
            detail_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                
                # Header Background
                ('BACKGROUND', (0, 0), (3, 0), colors.HexColor('#E8F4FC')), # Light Blue
                ('BACKGROUND', (5, 0), (8, 0), colors.HexColor('#E8F4FC')),
                
                # Borders
                ('GRID', (0, 0), (3, -1), 0.5, colors.grey),
                ('GRID', (5, 0), (8, -1), 0.5, colors.grey),
                
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(detail_table)
            story.append(Spacer(1, 10))
            
            # --- Analysis Summary Table ---
            # 4 Columns centered
            total_questions = len(questions)
            incorrect_count = total_questions - correct_count
            accuracy_pct = (correct_count / total_questions * 100) if total_questions > 0 else 0
            
            analysis_data = [
                ['测评总题数', '正确题数', '错误题数', '正确率'],
                [str(total_questions), str(correct_count), str(incorrect_count), f"{accuracy_pct:.1f}%"]
            ]
            
            # Width to match the two columns above roughly? 
            # Above total width is 87.5 * 2 + 5 = 180mm.
            # 180 / 4 = 45mm.
            analysis_table = Table(analysis_data, colWidths=[45*mm]*4)
            analysis_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8F4FC')), # Match header color
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(analysis_table)
            story.append(Spacer(1, 20))
            
            # --- 3. 测评评价 (Teacher Comment) ---
            story.append(Paragraph("测评评价", heading_style))
            # story.append(Spacer(1, 5))
            
            report_card = ReportCard.query.filter_by(registration_id=exam_reg.id).first()
            comment_text = ""
            if report_card and (report_card.teacher_comment or report_card.ai_comment):
                comment_text = report_card.teacher_comment or report_card.ai_comment
            
            # Box style
            comment_data = [[Paragraph(comment_text, normal_style)]]
            comment_table = Table(comment_data, colWidths=[180*mm], rowHeights=[40*mm])
            comment_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ]))
            story.append(comment_table)
            
            # Footer
            story.append(Spacer(1, 10))
            footer_text = f"{header_left_text} | {header_middle_text}"
            story.append(Paragraph(footer_text, small_style))
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

# Read original file
with open(file_path, 'r') as f:
    lines = f.readlines()

# Find function to replace
start_line = -1
end_line = -1

for i, line in enumerate(lines):
    if line.strip().startswith('def generate_report_card_pdf('):
        start_line = i
        break

if start_line != -1:
    # Look for end of function (before next decorator)
    for i in range(start_line + 1, len(lines)):
        if lines[i].startswith('@app.route'):
            end_line = i
            break
            
    if end_line == -1:
        end_line = len(lines)
        
    if not new_function.endswith('\n'):
        new_function += '\n'
        
    lines[start_line:end_line] = [new_function]
    
    with open(file_path, 'w') as f:
        f.writelines(lines)
    print("Function replaced with v5.")
else:
    print("Function not found.")
