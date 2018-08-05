from django.shortcuts import render
from django.shortcuts import redirect
from event.models import Event
from tag.models import Tag
from django.conf import settings


def index(request):
    if request.user.is_anonymous or request.user.role == "helper":
        return redirect('/event/top')
    else:
        return redirect('/user/top/list')


def index_event(request):
    context = {}

    """All Tags
    全てのタグ
    """
    context['all_tags'] = Tag.objects.all()

    """New Events
    新規イベント
    """
    context['new_events'] = [event for event
                             in Event.objects.all().order_by('-created')
                             if not event.is_over()][:10]

    """Prefectures
    日本の(!)県名
    """
    # FIXME: i18n, how?
    # XXX: PREFECTURES must be sorted right out of the box
    prefs = settings.PREFECTURES.items()
    prefs = sorted(prefs, key=lambda x: x[1][1])
    prefs = [(k, v[0]) for k, v in prefs]
    context['prefectures'] = prefs

    """Google MAP KEY
    MAP KEY from settings
    """
    context['google_map_key'] = settings.GOOGLE_MAP_KEY


    return render(request, 'top.html', context)


def show_map(request):
    context = {}
    context['all_tags'] = Tag.objects.all()

    return render(request, 'map.html', context)


def index_user(request):
    context = {}

    context['all_tags'] = Tag.objects.all()
    context['new_events']  = [event for event in Event.objects.all().order_by('-created') if not event.is_over()][:10]

    prefs = settings.PREFECTURES.items()
    prefs = sorted(prefs, key=lambda x: x[1][1])
    prefs = [(k, v[0]) for k, v in prefs]
    context['prefectures'] = prefs

    """Google MAP KEY
    MAP KEY from settings
    """
    context['google_map_key'] = settings.GOOGLE_MAP_KEY

    return render(request, 'top_user.html', context)
