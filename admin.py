from timeslots.models import Ladestelle, Rampe, Slot, Pause
from django.contrib import admin

class PausenAdmin(admin.ModelAdmin):
    pass

class SlotInline(admin.TabularInline):
    model = Slot
    extra = 1
    
class RampenAdmin(admin.ModelAdmin):
    inlines = [SlotInline]

class RampeInline(admin.TabularInline):
    model = Rampe
    extra = 1
    show_edit_link = True
    
class LadestellenAdmin(admin.ModelAdmin):
    inlines = [RampeInline]

admin.site.register(Ladestelle, LadestellenAdmin)
admin.site.register(Rampe, RampenAdmin)
admin.site.register(Pause, PausenAdmin)
