"""Persistence/query layer.

Repository functions accept an existing SQLAlchemy session rather than
opening their own. That lets the calling API/service combine several writes
into one transaction and decide when to commit or roll back.
"""
