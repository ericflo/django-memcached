from django.http import Http404
from django.shortcuts import render_to_response
from django.conf import settings
from django.template import RequestContext

from django_memcached.util import get_memcached_stats
from django.contrib.auth.decorators import user_passes_test

SERVERS = settings.CACHE_BACKEND.replace('memcached://', '').replace('/','').split(';')

def server_list(request):
    statuses = zip(range(len(SERVERS)), SERVERS, map(get_memcached_stats, SERVERS))
    context = {
        'statuses': statuses,
    }
    return render_to_response(
        'memcached/server_list.html',
        context,
        context_instance=RequestContext(request)
    )

def server_status(request, index):
    try:
        index = int(index)
    except ValueError:
        raise Http404
    if 'memcached' not in settings.CACHE_BACKEND:
        raise Http404
    if not SERVERS:
        raise Http404
    try:
        server = SERVERS[index]
    except IndexError:
        raise Http404
    stats = get_memcached_stats(server)
    if not stats:
        raise Http404
    context = {
        'server': server,
        'stats': stats.items(),
    }
    return render_to_response(
        'memcached/server_status.html',
        context,
        context_instance=RequestContext(request)
    )

if getattr(settings, 'DJANGO_MEMCACHED_REQUIRE_STAFF', False):
    server_list = user_passes_test(lambda u: u.is_staff)(server_list)
    server_status = user_passes_test(lambda u: u.is_staff)(server_status)