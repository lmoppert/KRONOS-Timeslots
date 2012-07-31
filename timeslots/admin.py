from timeslots.models import Logging, Station, Dock, Block, Slot, Job, UserProfile
from django.contrib import admin
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin


class LoggingAdmin(admin.ModelAdmin):
    list_display = ('time', 'user', 'host', 'task')

class JobAdmin(admin.ModelAdmin):
    list_display = ('number', 'description')

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
        ('Booking information', {'fields': ['opened_on_weekend', 'multiple_charges', 'booking_deadline', 'rnvp']})
    ]
    inlines = [DockInline]

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    max_num = 1
    can_delete = False

class UserAdmin(AuthUserAdmin):
    def add_view(self, *args, **kwargs):
        self.inlines = []
        return super(UserAdmin, self).add_view(*args, **kwargs)

    def change_view(self, *args, **kwargs):
        self.inlines = [UserProfileInline]
        return super(UserAdmin, self).change_view(*args, **kwargs)

admin.site.register(Logging, LoggingAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(Dock, DockAdmin)
admin.site.register(Block, BlockAdmin)
admin.site.register(Slot, SlotAdmin)
admin.site.register(Job, JobAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.unregister(Site)
