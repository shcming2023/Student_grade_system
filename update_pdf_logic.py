
import os

file_path = '/opt/Way To Future考试管理系统/Student_grade_system/wtf_app_simple.py'

with open(file_path, 'r') as f:
    lines = f.readlines()

# Find the range to replace
start_line = -1
end_line = -1

# We look for the "if scores:" line after the query, and the matching else block end
# Based on previous reads, it's around line 1326
for i, line in enumerate(lines):
    if 'if scores:' in line and i > 1320:
        start_line = i
        break

# Find the end of the block. It ends with "story.append(Spacer(1, 20))" indented same as "if scores:"?
# No, "if scores:" is at indent 12. "story.append(Spacer(1, 20))" at 1476 is at indent 12.
# The else block ends at 1474/1475. 1476 is outside the else block?
# Let's check the indentation of line 1476 in the Read output.
# 1476→            story.append(Spacer(1, 20)) -> 12 spaces.
# 1326→            if scores: -> 12 spaces.
# So 1476 is at the SAME level as "if scores:", meaning it is AFTER the if/else block.
# Wait, looking at the Read output:
# 1473→            else:
# 1474→                story.append(Paragraph("暂无成绩数据", normal_style))
# 1475→                
# 1476→            story.append(Spacer(1, 20))
# Yes, 1476 is the spacer *after* the if/else block in the OLD code?
# Or is it part of the else block? Indentation 12 means it's outside the else (which is 16).
# So the if/else block ends at 1474.

if start_line != -1:
    # Look for the else block
    for i in range(start_line, len(lines)):
        if 'else:' in lines[i] and len(lines[i]) - len(lines[i].lstrip()) == 12:
            # This is the else for "if scores:"
            # The next lines are the else body.
            # We want to find where the indent goes back to 12 or less (but inside the loop).
            pass
        if i > start_line and len(lines[i].strip()) > 0 and len(lines[i]) - len(lines[i].lstrip()) <= 12:
            if 'story.append(Spacer(1, 20))' in lines[i]:
                end_line = i # This line is included in the replacement or not?
                # I want to replace UP TO this line, or including it?
                # The new code generates this spacer too.
                # Let's replace UP TO this line (exclusive) and let the existing spacer be, 
                # OR replace it all.
                # Let's verify what the new code does.
                # My new code ends with story.append(Spacer(1, 20)) as well.
                # So I can replace inclusive.
                end_line = i + 1
                break

if start_line != -1 and end_line != -1:
    print(f"Replacing lines {start_line} to {end_line}")
    
    new_content = '''            # --- 1. 成绩明细 (Table) ---
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
'''
    
    # Check if we need to add a newline at the end
    if not new_content.endswith('\n'):
        new_content += '\n'

    lines[start_line:end_line] = [new_content]
    
    with open(file_path, 'w') as f:
        f.writelines(lines)
    
    print("Successfully replaced content.")
else:
    print("Could not find the block to replace.")
