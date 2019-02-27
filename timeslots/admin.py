from timeslots import models
from django.contrib import admin
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin


class LoggingAdmin(admin.ModelAdmin):
    list_display = ('time', 'user', 'host', 'task')


class ProductAdmin(admin.ModelAdmin):
    list_display = ('dock', 'date', 'details')


class JobAdmin(admin.ModelAdmin):
    list_display = ('number', 'description')


class JobInline(admin.TabularInline):
    model = models.Job
    extra = 2


class SlotAdmin(admin.ModelAdmin):
    list_display = ('date', 'block', 'times', 'line', 'company')
    inlines = [JobInline]


class BlockAdmin(admin.ModelAdmin):
    list_display = ('dock', 'start', 'end')


class BlockInline(admin.TabularInline):
    model = models.Block
    extra = 1


class DockAdmin(admin.ModelAdmin):
    list_display = ('station', 'name', 'description')
    inlines = [BlockInline]


class DockInline(admin.TabularInline):
    model = models.Dock
    extra = 1


class UserProfileRelated(admin.TabularInline):
    model = models.UserProfile.stations.through
    extra = 0


class StationAdmin(admin.ModelAdmin):
    list_display = ('name', 'shortdescription')
    fieldsets = [
        ('Basic information', {
            'fields': ['name', 'shortdescription', 'longdescription']
        }),
        ('Booking information', {
            'fields': ['multiple_charges', 'opened_on_weekend', 'has_status',
                       'has_klv', 'has_product', 'booking_deadline', 'rnvp']
        })
    ]
    inlines = [DockInline, UserProfileRelated]


class UserProfileInline(admin.StackedInline):
    model = models.UserProfile
    max_num = 1
    can_delete = False
    filter_horizontal = ('stations', )


class UserAdmin(AuthUserAdmin):
    list_display = ('username', 'userprofile', 'first_name', 'last_name',
                    'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email',
                     'userprofile__company')

    def add_view(self, *args, **kwargs):
        self.inlines = []
        return super(UserAdmin, self).add_view(*args, **kwargs)

    def change_view(self, *args, **kwargs):
        self.inlines = [UserProfileInline]
        return super(UserAdmin, self).change_view(*args, **kwargs)


admin.site.register(models.Logging, LoggingAdmin)
admin.site.register(models.Station, StationAdmin)
admin.site.register(models.Dock, DockAdmin)
admin.site.register(models.Block, BlockAdmin)
admin.site.register(models.Slot, SlotAdmin)
admin.site.register(models.Job, JobAdmin)
admin.site.register(models.Product, ProductAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.unregister(Site)
