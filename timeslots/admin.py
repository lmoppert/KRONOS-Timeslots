from timeslots.models import Station, Dock, Line, Slot, UserProfile
from django.contrib import admin

class SlotInline(admin.TabularInline):
    model = Slot
    extra = 1
    
class DockAdmin(admin.ModelAdmin):
    inlines = [SlotInline]

class DockInline(admin.TabularInline):
    model = Rampe
    extra = 1
    show_edit_link = True
    
class StationAdmin(admin.ModelAdmin):
    inlines = [DockInline]

admin.site.register(Station, StationAdmin)
admin.site.register(Dock, DockAdmin)
