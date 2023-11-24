from django.contrib import admin

from dashview.models import Feedback,Vote,Comment

admin.site.register( Feedback)
admin.site.register( Vote)
admin.site.register( Comment)