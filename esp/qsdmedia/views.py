from esp.qsdmedia.models import Media
from django.http import HttpResponseRedirect, Http404
from esp.users.models import UserBit
from esp.datatree.models import GetNode


def qsdmedia(request, url, filename):
    """ Return a redirect to a media file """
    try:
        media_rec = Media.find_by_url_parts(url.split('/'), filename)
    except Media.DoesNotExist:
        raise Http404
    
    # aseering 8-7-2006: Add permissions enforcement; Only show the page if the current user has V/Publish on this node
    have_view = UserBit.UserHasPerms( request.user, media_rec.anchor, GetNode('V/Publish') )
    if have_view:
        return HttpResponseRedirect(media_rec.get_target_file_url())
    else:
        raise Http404
