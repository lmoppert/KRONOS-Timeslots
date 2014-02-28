"""Admin configuration for the Timeslots application."""

#pep257: disable C0110
from timeslots.models import (Station, Dock, Block, UserProfile, Slot, Job,
                              Logging, Availability, SiloJob, Scale, Product)
from django.contrib import admin
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin


class LoggingAdmin(admin.ModelAdmin):
    """Admin view for the log entries."""

    list_display = ('time', 'user', 'host', 'task')


class ProductAdmin(admin.ModelAdmin):
    """Admin view for the products."""

    list_display = ('name', 'description', 'load_time')


class JobAdmin(admin.ModelAdmin):
    """Admin view for the jobs."""

    list_display = ('number', 'description')


class JobInline(admin.TabularInline):
    """Inline view for the jobs."""

    model = Job
    extra = 2


class AvailabilityAdmin(admin.ModelAdmin):
    """Admin view for the availability of products."""

    list_display = ('date', 'scale', 'product')


class AvailabilityInline(admin.TabularInline):
    """Inline view for the availability of products."""

    model = Availability
    extra = 1


class SiloJobAdmin(admin.ModelAdmin):
    """Admin view for the silo jobs."""

    list_display = ('number', 'date', 'description')


class SiloJobInline(admin.TabularInline):
    """Admin view for the silo jobs."""

    model = SiloJob
    extra = 1


class SlotAdmin(admin.ModelAdmin):
    """Admin view for the slots."""

    list_display = ('date', 'block', 'times', 'line', 'company')
    inlines = [JobInline]


class BlockAdmin(admin.ModelAdmin):
    """Admin view for the blocks."""

    list_display = ('dock', 'start', 'end')


class BlockInline(admin.TabularInline):
    """Inline view for the blocks."""

    model = Block
    extra = 1


class DockAdmin(admin.ModelAdmin):
    """Admin view for the docks."""

    list_display = ('station', 'name', 'description')
    inlines = [BlockInline]


class DockInline(admin.TabularInline):
    """Inline view for the docks."""

    model = Dock
    extra = 1


class ScaleAdmin(admin.ModelAdmin):
    """Admin view for the scales."""

    list_display = ('name', 'description')
    inlines = [SiloJobInline, AvailabilityInline]


class ScaleInline(admin.TabularInline):
    """Inline view for the scales."""

    model = Scale
    extra = 1


class StationAdmin(admin.ModelAdmin):
    """Admin view for the stations."""

    list_display = ('name', 'shortdescription')
    fieldsets = [
        ('Basic information', {
            'fields': ['name', 'shortdescription', 'longdescription']
        }),
        ('Booking information', {
            'fields': ['multiple_charges', 'opened_on_weekend', 'has_status',
                       'has_klv', 'booking_deadline', 'rnvp']
        })
    ]
    inlines = [DockInline, ScaleInline]


class UserProfileInline(admin.StackedInline):
    """Inline view for the user profile."""

    model = UserProfile
    max_num = 1
    can_delete = False


class UserAdmin(AuthUserAdmin):
    """Admin view for the user profile."""

    def add_view(self, *args, **kwargs):
        """Return an overloaded add user view."""
        self.inlines = []
        return super(UserAdmin, self).add_view(*args, **kwargs)

    def change_view(self, *args, **kwargs):
        """Return an overloaded change user view."""
        self.inlines = [UserProfileInline]
        return super(UserAdmin, self).change_view(*args, **kwargs)


admin.site.register(Logging, LoggingAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(Dock, DockAdmin)
admin.site.register(Block, BlockAdmin)
admin.site.register(Slot, SlotAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(Scale, ScaleAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Availability, AvailabilityAdmin)
admin.site.register(SiloJob, SiloJobAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.unregister(Site)
