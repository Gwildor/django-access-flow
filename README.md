A proof-of-concept for a Django per-model-instance access check workflow.

See `models.py` and `views.py` for examples of how these could be implemented.

Generally speaking, you can implement methods on your model to be checked, with
a list of methods to check as an attribute on your CRUD-views. For other views,
the `check_access` can be overridden to decide if access should be granted. The
`access_denied` method can be overridden to return a gentle access denied
response, instead of a standard HTTP 403 Forbidden.
