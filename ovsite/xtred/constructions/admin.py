from django.contrib import admin

from .models import (ConstructionsCompany,
                     Constructions,
                     ConstructionsWorks,
                     Location,
                     Entity,
                     BrandType)


class ConstructionsWorksInline(admin.TabularInline):
    model = ConstructionsWorks
    extra = 0


class EntityAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
    )


class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'country',
        'city',
    )


class ConstructionsAdmin(admin.ModelAdmin):
    inlines = (
        ConstructionsWorksInline,
    )
    list_display = (
        'pk',
        'brand',
        'location',
        'title',
        'date_start_graph',
        'date_finish_graph',
        'date_start',
        'date_finish',
        'date_acceptance',
        'description',
    )
    list_editable = (
        'description',
        'date_start_graph',
        'date_finish_graph',
        'date_start',
        'date_finish',
        'date_acceptance',

    )
    search_fields = (
        'title',
        'brand',

    )
    list_filter = (
        'title',
        'date_start',
        'date_finish',
        'date_acceptance',)
    list_display_links = ('title',)


class ConstructionsCompanyAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
    )
    list_display_links = ('title',)


class ConstructionsWorksAdmin(admin.ModelAdmin):

    list_display = (
        'pk',
        'work',
    )


class BrandTypeAdmin(admin.ModelAdmin):

    list_display = (
        'pk',
        'title',
        'brand_photo',
    )


admin.site.register(Constructions, ConstructionsAdmin)
admin.site.register(ConstructionsCompany, ConstructionsCompanyAdmin)
admin.site.register(ConstructionsWorks, ConstructionsWorksAdmin)
admin.site.register(BrandType, BrandTypeAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Entity, EntityAdmin)
