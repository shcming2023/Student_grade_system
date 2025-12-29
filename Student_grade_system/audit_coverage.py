
from wtf_app_simple import app, db, ExamTemplate, ExamRegistration, Subject

def audit_templates():
    with app.app_context():
        print("=== Audit: Templates with Registrations vs API Logic ===")
        
        # 1. Get all template IDs that have at least one registration
        used_ids = db.session.query(ExamRegistration.exam_template_id).distinct().all()
        used_ids = [i[0] for i in used_ids]
        print(f"Templates with registrations: {len(used_ids)}")
        
        # 2. For each used ID, find its 'Representative' (as per score_entry route)
        # and verify if the API logic works for that representative.
        
        # Simulate score_entry logic to build the Unique Map
        all_templates = ExamTemplate.query.join(Subject).order_by(ExamTemplate.name).all()
        unique_templates = {}
        template_to_rep = {} # Map real ID -> Representative ID
        
        for t in all_templates:
            key = (t.name, t.subject.id, t.grade_level)
            if key not in unique_templates:
                unique_templates[key] = t
            
            # Record that this template maps to the representative in unique_templates[key]
            template_to_rep[t.id] = unique_templates[key].id

        print(f"Unique Representatives: {len(unique_templates)}")
        
        # 3. Check coverage
        # For every template that has registrations, can we access it via its Representative?
        
        missing_coverage = []
        for real_id in used_ids:
            if real_id not in template_to_rep:
                # This happens if 'all_templates' query (join Subject) filtered it out?
                # e.g. Template has no Subject?
                t = ExamTemplate.query.get(real_id)
                print(f"⚠️ Template {real_id} ({t.name if t else 'Unknown'}) has registrations but was not in score_entry list!")
                if not t.subject:
                    print(f"   Reason: Missing Subject!")
                continue

            rep_id = template_to_rep[real_id]
            
            # Now simulate API call for rep_id
            rep = ExamTemplate.query.get(rep_id)
            
            # API logic: Find related templates by Name/Subject/Grade
            related = ExamTemplate.query.filter_by(
                name=rep.name,
                subject_id=rep.subject_id,
                grade_level=rep.grade_level
            ).all()
            related_ids = [x.id for x in related]
            
            if real_id not in related_ids:
                print(f"❌ CRITICAL FAIL: Real ID {real_id} has regs, maps to Rep {rep_id}, but Rep's related lookup {related_ids} DOES NOT include {real_id}!")
                # This implies mismatch in Name/Subject/Grade between Real and Rep?
                # But Rep is chosen by key (Name,Subject,Grade), so they MUST match.
            
            # else:
            #     print(f"OK: Real {real_id} -> Rep {rep_id} -> Related includes Real")

        print("Audit Complete.")

if __name__ == "__main__":
    audit_templates()
