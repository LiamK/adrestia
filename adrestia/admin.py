from django.contrib import admin
from .models import *


class CandidateAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all':('admin/css/adrestia_admin.css',)
        }
    list_display = (
        'name',
        'state',
        'district',
        'level',
        'office',
        'party',
        'serving',
        'running',
        'winner',
        'website_url',
        'facebook_id',
        'twitter_id',
        'donate_url',
        'endorsement_url',
        'image_url',
        'image',
        )
    list_filter = ('level', 'office', 'status', 'serving', 'running',
            'winner', 'state')
    list_editable = (
        'office',
        'level',
        'serving',
        'running',
        'winner',
        'party',
        'website_url',
        'facebook_id',
        'twitter_id',
        'donate_url',
        'endorsement_url',
        'image_url',
        'image',
        )
    search_fields = ('name',)

class FootnoteAdmin(admin.ModelAdmin):
    list_display = ('text', 'url')
    search_fields = ('text',)

class FootnoteInline(admin.TabularInline):
    verbose_name = 'footnote'
    can_delete = False
    model = Delegate.footnotes.through
    raw_id_fields = ('footnote',)
    extra = 0

class DelegateSummaryAdmin(admin.ModelAdmin):
    list_display = (
        'state',
        'allocation_pledged',
        'allocation_unpledged',
        'available_pledged',
        'available_unpledged',
        'sanders_pledged',
        'sanders_unpledged',
        'clinton_pledged',
        'clinton_unpledged',
    )

class DelegateAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', 'group', 'candidate')
    list_filter = ('group', 'candidate', 'state')
    search_fields = ('name',)
    inlines = [ FootnoteInline ]
    exclude = ('footnotes',)

class LegislatorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'state', 'district')
    list_filter = ('party', 'senate_class', 'title', 'state')
    search_fields = ('firstname', 'lastname', 'nickname')

class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', 'census_region_name', 'primary_date', 'general_date')
    list_editable = ('primary_date', 'general_date')
    list_filter = ('census_region_name',)
    search_fields = ('name',)

class OfficeInline(admin.TabularInline):
    verbose_name = 'office'
    can_delete = False
    model = StateLegislator.offices.through
    raw_id_fields = ('office',)
    extra = 0
class OfficeAdmin(admin.ModelAdmin):
    inlines = [ OfficeInline ]

class StateLegislatorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'state', 'district', 'chamber', 'level')
    list_filter = ('chamber', 'level', 'party', 'active', 'state')
    search_fields = ('full_name',)
    inlines = [ OfficeInline ]
    exclude = ('offices',)

admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Delegate, DelegateAdmin)
admin.site.register(DelegateSummary, DelegateSummaryAdmin)
admin.site.register(Legislator, LegislatorAdmin)
admin.site.register(StateLegislator, StateLegislatorAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(Footnote, FootnoteAdmin)

admin.site.register(DNCGroup)
admin.site.register(PresidentialCandidate)
