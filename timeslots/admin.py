from timeslots.models import Station, Dock, Line, Slot, UserProfile
from django.contrib import admin

class DockAdmin(admin.ModelAdmin):
    list_display = ('station', 'name', 'description', 'linecount')

class DockInline(admin.TabularInline):
    model = Dock
    extra = 1
    
class StationAdmin(admin.ModelAdmin):
    list_display = ('name', 'shortdescription')
    fieldsets = [
        ('Basic information', {'fields': ['name','shortdescription','longdescription']}),
        ('Booking deadlines', {'fields': ['booking_deadline', 'rnvp']})
    ]
    inlines = [DockInline]

class LineAdmin(admin.ModelAdmin):
    list_display = ('dock', 'start', 'end')

class UserAdmin(admin.ModelAdmin):
    list_display = ('user', 'company')

admin.site.register(Station, StationAdmin)
admin.site.register(Dock, DockAdmin)
admin.site.register(Line, LineAdmin)
admin.site.register(UserProfile, UserAdmin)
