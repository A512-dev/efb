# POST /api/v1/manuals/{manual_id}/read

# Backend behavior:

# 1. Get current user from JWT.
# 2. Get manual by manual_id.
# 3. If manual does not exist or manual.org_id != current_user.org_id:
#        return 404
# 4. Upsert into manual_reads:
#        user_id = current_user.id
#        manual_id = manual.id
#        org_id = current_user.org_id
# 5. Optional: also insert ManualAccessLog(action=view)
# 6. Optional: audit_service.record(action="manual.read")
# 7. db.commit()
# 8. Return read relationship.