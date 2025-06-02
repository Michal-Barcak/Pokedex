def get_first_form_error(form):
    """Získa prvú chybu z Django formu"""
    if form.non_field_errors():
        return form.non_field_errors()[0]
    if form.errors:
        return next(iter(form.errors.values()))[0]
    return "Invalid form data."