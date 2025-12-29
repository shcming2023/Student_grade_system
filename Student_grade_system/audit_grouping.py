
from wtf_app_simple import app, db, ExamTemplate, ExamRegistration, Subject

def audit_grouping():
    with app.app_context():
        print("=== Audit: Dropdown Generation vs API Response ===")
        
        # 1. Replicate score_entry route logic EXACTLY
        all_templates = ExamTemplate.query.join(Subject).order_by(ExamTemplate.name).all()
        
        used_template_groups = db.session.query(
            ExamTemplate.name, ExamTemplate.subject_id, ExamTemplate.grade_level
        ).join(
            ExamRegistration, ExamTemplate.id == ExamRegistration.exam_template_id
        ).distinct().all()
        
        used_keys = set((name, subject_id, grade_level) for name, subject_id, grade_level in used_template_groups)
        print(f"Used Keys Count: {len(used_keys)}")
        
        unique_templates = {}
        for t in all_templates:
            key = (t.name, t.subject.id, t.grade_level)
            if key in used_keys:
                if key not in unique_templates:
                    unique_templates[key] = t
        
        sorted_templates = sorted(unique_templates.values(), key=lambda x: x.name)
        print(f"Dropdown Items: {len(sorted_templates)}")
        
        # 2. Test API for EACH item in the dropdown
        for t in sorted_templates:
            # Simulate API Logic
            related_templates = ExamTemplate.query.filter_by(
                name=t.name,
                subject_id=t.subject_id,
                grade_level=t.grade_level
            ).all()
            related_ids = [rt.id for rt in related_templates]
            
            # Query Students
            count = db.session.query(ExamRegistration).filter(
                ExamRegistration.exam_template_id.in_(related_ids)
            ).count()
            
            print(f"Dropdown Item: [{t.id}] {t.name} (Grade {t.grade_level}) -> Found {count} students.")
            
            if count == 0:
                print(f"❌ ERROR: Item [{t.id}] {t.name} is in dropdown but API finds 0 students!")
                # Analyze why
                # Check if 'used_keys' logic was too loose?
                # No, used_keys implies at least one template in the group has a registration.
                # So 'related_ids' MUST include that template.
                
                # Debug:
                print(f"   Related IDs: {related_ids}")
                # Check registrations for each related ID manually
                for rid in related_ids:
                    c = ExamRegistration.query.filter_by(exam_template_id=rid).count()
                    print(f"   - ID {rid}: {c} regs")

if __name__ == "__main__":
    audit_grouping()
