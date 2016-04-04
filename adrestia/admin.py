from django.contrib import admin
from .models import *

class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', 'district', 'level', 'office')
    list_filter = ('level', 'office', 'status', 'state')
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
    list_display = ('name', 'state')
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
admin.site.register(Legislator, LegislatorAdmin)
admin.site.register(StateLegislator, StateLegislatorAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(Footnote, FootnoteAdmin)

admin.site.register(DNCGroup)
admin.site.register(PresidentialCandidate)
