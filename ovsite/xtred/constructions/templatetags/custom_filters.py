import datetime
from django import template

register = template.Library()


@register.filter
def warranty_status(date_acceptance):
    if not date_acceptance:
        return "Дата приемки не указана"
    now = datetime.date.today()
    warranty_end_date = date_acceptance + datetime.timedelta(days=2*365)
    if now > warranty_end_date:
        return "Не на гарантии"
    else:
        days_left = (warranty_end_date - now).days
        return f"На гарантии ({days_left} дней до окончания)"


@register.filter
def warranty_status_color(date_acceptance):
    if not date_acceptance:
        return "secondary"
    now = datetime.date.today()
    warranty_end_date = date_acceptance + datetime.timedelta(days=2*365)
    if now > warranty_end_date:
        return "danger"
    else:
        return "success"
