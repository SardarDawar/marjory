from django.db import models
from django.contrib.sites.models import Site
from django.conf import settings
from colorfield.fields import ColorField

# Create your models here.

class Setting(models.Model):
    # only for use in code
    LANG_ENG = 'EN'
    LANG_POR = 'PT'
    LANGUAGE_CHOICES = [
        (LANG_ENG, 'English'),
        (LANG_POR, 'Portuguese'),
    ]

    # site-url can be set in corresponding Site-table entry
    site = models.OneToOneField(Site, on_delete=models.CASCADE, related_name='settings', default=settings.SITE_ID)

    # app basic-info
    app_name = 'Marjory'
    tagline_ENG = models.CharField(max_length=200, blank=True, null=True, verbose_name="Tagline (English)")
    tagline_POR = models.CharField(max_length=200, blank=True, null=True, verbose_name="Tagline (Portuguese)")
    about_ENG = models.CharField(max_length=2500, blank=True, null=True, verbose_name="About (English)")
    about_POR = models.CharField(max_length=2500, blank=True, null=True, verbose_name="About (Portuguese)")
    contact_address = models.CharField(max_length=500, blank=True, null=True)
    contact_tel = models.CharField(max_length=25, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)

    # app social-links
    social_link_facebook = models.CharField(max_length=1000, blank=True, null=True) 
    social_link_twitter = models.CharField(max_length=1000, blank=True, null=True) 
    social_link_instagram = models.CharField(max_length=1000, blank=True, null=True) 

    # frontend script style variables
    color_header_font = ColorField(default='#FFD966', verbose_name='Header font color')
    color_header_bg = ColorField(default='#417690', verbose_name='Header background color')
    color_nav_foot_font = ColorField(default='#FFFFFF', verbose_name='Nav/footer font color')
    color_nav_foot_bg = ColorField(default='#79AEC8', verbose_name='Nav/footer background color')

    # app params/settings
    session_timeout = models.IntegerField(default=60, help_text="Session Timeout (Minutes)")

    def __str__(self):
        return f'Settings for site {self.site.domain}'

class Link(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='links', default=settings.SITE_ID)
    name_ENG = models.CharField(max_length=100, blank=True, null=True, verbose_name="Link Name (English)")
    name_POR = models.CharField(max_length=100, blank=True, null=True, verbose_name="Link Name (Portuguese)")
    url = models.URLField(max_length=500, verbose_name="Link URL")

    class Meta:
        ordering = ['id']

    def __str__(self):
        name = ''
        if self.name_ENG and self.name_POR:
            name = f' [{self.name_ENG}/{self.name_POR}]'
        elif self.name_ENG:
            name = f' [{self.name_ENG}]'
        elif self.name_POR:
            name = f' [{self.name_POR}]'
        return f'({self.site.domain}) {self.url}{name}'
    
    def get_display_name_eng(self):
        return self.name_ENG if self.name_ENG else self.get_stripped_url()

    def get_display_name_por(self):
        return self.name_POR if self.name_POR else self.get_stripped_url()
    
    def get_stripped_url(self):
        return self.url.replace("https://", "").replace("http://", "")
