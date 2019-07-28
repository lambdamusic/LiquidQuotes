
from django.contrib import admin
from django.conf import settings
from koncepts.models import *


admin.site.register(Document, Document.Admin)
admin.site.register(Koncept, Koncept.Admin)
admin.site.register(Fragment, Fragment.Admin)
admin.site.register(Project, Project.Admin)

admin.site.register(IntFrag, IntFrag.Admin)
admin.site.register(IntKon, IntKon.Admin)

admin.site.register(Languages, Languages.Admin)
# admin.site.register(Tag, Tag.Admin)
admin.site.register(RelationKon, RelationKon.Admin)
admin.site.register(FAQitem, FAQitem.Admin)


admin.site.register(Subject, Subject.Admin)
