import coreapi
from rest_framework.schemas import AutoSchema
from rest_framework.schemas.inspectors import ViewInspector


class LogsSearchPaginableSchema:
    def get_pagination_fields(self, path, method):
        view = self.view

        pagination = getattr(view, 'service_paginator', None)
        if not pagination:
            return []

        paginator = view.service_paginator
        return paginator.get_schema_fields(view)


class CustomSchema(ViewInspector, LogsSearchPaginableSchema):

    def __init__(self, **kwargs):
        super().__init__()
        manual_fields = kwargs.get('manual_fields', None)
        self.fields_post = []
        self.fields_get = []
        self.autoschema = AutoSchema(manual_fields)
        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_link(self, path, method, base_url):
        self.autoschema.view = self.view
        fields = self.get_path_fields(path, method)
        fields += self.get_pagination_fields(path, method)
        manual_fields = self.autoschema.get_manual_fields(path, method)
        fields = self.autoschema.update_fields(fields, manual_fields)
        link = self.autoschema.get_link(path, method, base_url)
        return coreapi.Link(
            url=link.url,
            action=method.lower(),
            encoding=link.encoding,
            fields=fields,
            description=link.description
        )

    # Implement custom introspection here (or in other sub-methods)
    def get_path_fields(self, path, method):
        lower_method = method.lower()
        fields = getattr(self, "fields_{}".format(lower_method), [])
        return fields
