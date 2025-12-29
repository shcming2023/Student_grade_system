
import os

file_path = '/opt/Way To Future考试管理系统/Student_grade_system/wtf_app_simple.py'

new_function = r'''def generate_report_card_pdf(student_id, exam_session_id, template_id=None):
    """生成学生成绩单PDF - Refactored v4"""
    print(f"DEBUG: Generating PDF for student {student_id}, session {exam_session_id}, template {template_id} - NEW LOGIC v4")
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
        heading_style.backColor = colors.HexColor('#E0E0E0') 
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
        
        # Get System Settings and Session Settings
        setting = SystemSetting.query.first()
        system_company_name_zh = setting.company_name_zh if setting else '橡心国际'
        system_logo_path = setting.logo_path if setting else None
        
        # Determine Header Content
        # Left: Session English Name (e.g. Way To Future VII)
        header_left = exam_session.exam_name_en or 'Way To Future'
        # Middle: Company Brand (Session override or System default)
        header_middle = exam_session.company_brand or system_company_name_zh
        # Right: Logo
        header_right_logo = None
        if system_logo_path:
             abs_logo_path = os.path.join(app.static_folder, system_logo_path)
             if os.path.exists(abs_logo_path):
                 try:
                     # Create Image object
                     # Resize to fit height ~15mm
                     img = Image(abs_logo_path)
                     img.drawHeight = 12*mm
                     img.drawWidth = img.drawHeight * (img.imageWidth / img.imageHeight)
                     header_right_logo = img
                 except:
                     pass

        # 遍历每门科目 (生成一页)
        for exam_reg, template, subject in registrations:
            if exam_reg != registrations[0][0]:
                story.append(PageBreak())
                
            # --- Header (Logo) ---
            # [Left: Exam Name EN] [Middle: Company Brand] [Right: Logo]
            # Use a Table
            header_data = [[
                Paragraph(header_left, small_style), 
                Paragraph(header_middle, small_style), 
                header_right_logo if header_right_logo else ''
            ]]
            
            header_table = Table(header_data, colWidths=[60*mm, 70*mm, 60*mm])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(header_table)
            story.append(Spacer(1, 15))
            
            # --- 标题 ---
            story.append(Paragraph(f"{exam_session.name}成绩单", title_style))
            story.append(Spacer(1, 20))
            
            # --- 1. 基本信息 (Basic Info - No Title) ---
            # 考生姓名、测评名称、测评时间 (One Row)
            basic_info_data = [
                [
                    Paragraph(f"<b>考生姓名：</b>{student.name}", normal_style),
                    Paragraph(f"<b>测评名称：</b>{template.name}", normal_style),
                    Paragraph(f"<b>测评时间：</b>{exam_session.exam_date.strftime('%Y-%m-%d')}", normal_style)
                ]
            ]
            
            basic_info_table = Table(basic_info_data, colWidths=[50*mm, 80*mm, 60*mm])
            basic_info_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(basic_info_table)
            story.append(Spacer(1, 15))
            
            # --- 2. 测评分析 (Combined Detail + Analysis) ---
            story.append(Paragraph("测评分析", heading_style))
            story.append(Spacer(1, 10))
            
            # Fetch ALL questions for this template (defined structure)
            questions = Question.query.filter_by(exam_template_id=template.id).all()
            
            # Sort questions
            def natural_sort_key(q):
                import re
                parts = re.split(r'(\d+)', q.question_number)
                return [int(p) if p.isdigit() else p for p in parts]
            questions.sort(key=natural_sort_key)
            
            # Fetch Scores
            q_ids = [q.id for q in questions]
            scores_map = {} # q_id -> score obj
            if q_ids:
                found_scores = Score.query.filter(
                    Score.student_id == student.id,
                    Score.question_id.in_(q_ids)
                ).all()
                scores_map = {s.question_id: s for s in found_scores}
            
            # Build Detail Table Data
            detail_rows = []
            total_score = 0
            total_possible = 0
            correct_count = 0
            
            for q in questions:
                score_obj = scores_map.get(q.id)
                
                if score_obj:
                    is_correct_text = '正确' if score_obj.is_correct else '错误'
                    color = colors.green if score_obj.is_correct else colors.red
                    score_val = float(score_obj.score)
                    if score_obj.is_correct:
                        correct_count += 1
                    total_score += score_val
                else:
                    # No score yet
                    is_correct_text = '-'
                    color = colors.black
                    score_val = 0
                    
                total_possible += float(q.score)
                
                detail_rows.append([
                    f"Q{q.question_number}",
                    Paragraph(q.module or '-', small_style),
                    Paragraph(q.knowledge_point or '-', small_style),
                    Paragraph(f'<font color="{color}">{is_correct_text}</font>', small_style)
                ])

            # Split into two columns
            mid_point = (len(detail_rows) + 1) // 2
            left_rows = detail_rows[:mid_point]
            right_rows = detail_rows[mid_point:]
            
            header_row = ['题号', '模块', '知识点', '结果', '', '题号', '模块', '知识点', '结果']
            combined_data = [header_row]
            
            for i in range(len(left_rows)):
                left = left_rows[i]
                right = right_rows[i] if i < len(right_rows) else ['', '', '', '']
                combined_data.append(left + [''] + right)
            
            col_widths = [12*mm, 18*mm, 45*mm, 15*mm, 5*mm, 12*mm, 18*mm, 45*mm, 15*mm]
            
            detail_table = Table(combined_data, colWidths=col_widths)
            detail_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (3, 0), colors.HexColor('#F5F5F5')),
                ('BACKGROUND', (5, 0), (8, 0), colors.HexColor('#F5F5F5')),
                ('LINEBELOW', (0, 0), (3, 0), 1, colors.black),
                ('LINEBELOW', (5, 0), (8, 0), 1, colors.black),
                ('GRID', (0, 0), (3, -1), 0.5, colors.grey),
                ('GRID', (5, 0), (8, -1), 0.5, colors.grey),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(detail_table)
            story.append(Spacer(1, 10))
            
            # --- Analysis Table (Immediately below detail) ---
            total_questions = len(questions)
            # incorrect_count = total_questions - correct_count # Only counts attempted? 
            # If scores not present, treat as 0?
            # Let's count actual incorrect (score present but wrong) + missing (if any? usually 0 if all loaded)
            # Simplification: incorrect = total - correct
            incorrect_count = total_questions - correct_count
            accuracy_pct = (correct_count / total_questions * 100) if total_questions > 0 else 0
            
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
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F0F8FF')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(analysis_table)
            story.append(Spacer(1, 15))
            
            # --- 3. 测评评价 (Teacher Comment) ---
            story.append(Paragraph("测评评价", heading_style))
            story.append(Spacer(1, 5))
            
            report_card = ReportCard.query.filter_by(registration_id=exam_reg.id).first()
            comment_text = ""
            if report_card and (report_card.teacher_comment or report_card.ai_comment):
                comment_text = report_card.teacher_comment or report_card.ai_comment
            
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
            story.append(Paragraph(f"{header_left} - {header_middle}", small_style))
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
    print("Function replaced.")
else:
    print("Function not found.")
