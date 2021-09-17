from django.contrib import admin


from .models import *


from import_export.admin import ImportExportModelAdmin

#admin.site.register(pumpInstData)

# Register your models here.



@admin.register(SiteDetails)
@admin.register(SiteData)
@admin.register(BHSiteDetails)
@admin.register(BHData)
@admin.register(BHInstData)
@admin.register(DBData)
@admin.register(homeid)






class SiteDetailsAdmin(ImportExportModelAdmin):
	pass

class SiteDataAdmin(ImportExportModelAdmin):
	pass

class BHSiteDetailsAdmin(ImportExportModelAdmin):
	pass

class BHDataAdmin(ImportExportModelAdmin):
	pass

class BHInstDataAdmin(ImportExportModelAdmin):
	pass

class DBDataAdmin(ImportExportModelAdmin):
	pass

class homeidAdmin(ImportExportModelAdmin):
	pass

