"""Reserved module for request-level audit middleware.

Audit records are currently written explicitly through
:mod:`app.services.audit_service`, which has access to the feature-specific
target and metadata. No middleware is registered from this module yet.
"""
