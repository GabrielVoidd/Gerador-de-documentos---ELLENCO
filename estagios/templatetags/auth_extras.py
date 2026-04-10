from django import template

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    # O chefão (você) vê tudo
    if user.is_superuser:
        return True
    # Verifica se o usuário comum está no grupo
    return user.groups.filter(name=group_name).exists()
