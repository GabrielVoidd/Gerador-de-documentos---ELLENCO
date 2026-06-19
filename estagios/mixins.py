from .models import RegistroAcao


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def registrar_acao(request, tipo, descricao, objeto=None):
    RegistroAcao.objects.create(
        usuario=request.user if request.user.is_authenticated else None,
        tipo=tipo,
        descricao=descricao,
        objeto_tipo=objeto.__class__.__name__ if objeto else '',
        objeto_id=objeto.pk if objeto else None,
        ip=get_client_ip(request),
    )
