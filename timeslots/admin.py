from timeslots.models import Station, Dock, Block, Slot, Job, UserProfile
from django.contrib import admin

class JobInline(admin.TabularInline):
    model = Job
    extra = 2

class SlotAdmin(admin.ModelAdmin):
    inlines = [JobInline]

class BlockAdmin(admin.ModelAdmin):
    list_display = ('dock', 'start', 'end')

class BlockInline(admin.TabularInline):
    model = Block
    extra = 1
    
class DockAdmin(admin.ModelAdmin):
    list_display = ('station', 'name', 'description')
    inlines = [BlockInline]

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

class UserAdmin(admin.ModelAdmin):
    list_display = ('user', 'company')


admin.site.register(Station, StationAdmin)
admin.site.register(Dock, DockAdmin)
admin.site.register(Block, BlockAdmin)
admin.site.register(Slot, SlotAdmin)
admin.site.register(UserProfile, UserAdmin)
