#Recommended functions:

# mark_read(db, user, manual)
# list_for_user(db, user)
# get_read_manual_ids_for_user(db, user)

# The mark_read logic should be idempotent:

# If row does not exist:
#     create row with read_count = 1
# If row exists:
#     update last_read_at
#     increment read_count