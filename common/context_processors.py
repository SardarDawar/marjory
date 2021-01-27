from django.contrib.sites.models import Site

def site_processor(request):
    site = Site.objects.get_current()
    try:
        site_settings = site.settings
        return {
            'domain': site.domain,
            'site_settings': site_settings,
        }
    except AttributeError:
        return {
            'domain': site.domain,
        }