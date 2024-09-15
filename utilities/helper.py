def remove_field_document(document: dict, fields: list):
    for field in fields:
        document.pop(field, None)
        return document
    