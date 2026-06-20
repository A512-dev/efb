#TODO: response models like this:
# ManualReadOut
# ManualReadResponse
# ManualReadListResponse 
# for example
# {
#   "message": "Manual marked as read",
#   "item": {
#     "id": 10,
#     "manual_id": 5,
#     "user_id": 3,
#     "read_at": "...",
#     "last_read_at": "...",
#     "read_count": 2
#   }
# }

# For the list endpoint:
# {
#   "items": [
#     {
#       "id": 5,
#       "title": "A300 SOP",
#       "original_filename": "A306-310-SOP.pdf",
#       "read_at": "...",
#       "last_read_at": "..."
#     }
#   ]
# }