# from django.contrib import admin
# from django import forms
# from django.contrib.admin import AdminSite
# from django.utils.safestring import mark_safe
# from django.utils.translation import gettext_lazy
#
# from todoapp.models import Tasks
#
#
# # Register your models here.
#
# class TasksAdminForm(forms.ModelForm):
#     class Meta:
#         model = Tasks
#         fields = '__all__'
#
#
# class TasksAdmin(admin.ModelAdmin):
#     form = TasksAdminForm
#     list_display = ('title', 'description', 'due_date', 'is_completed')
#     readonly_fields = ['created', 'last_updated', ]
#     list_per_page = 1000
#     search_fields = ('title', 'description', 'due_date', 'is_completed',)
#
#
# admin.site.register(Tasks, TasksAdmin)
#
#
# class MyAdminSite(AdminSite):
#     # Text to put at the end of each page's <title>.
#     site_title = gettext_lazy('My site admin')
#
#     # Text to put in each page's <h1> (and above login form).
#     site_header = gettext_lazy('My administration')
#
#     # Text to put at the top of the admin index page.
#     index_title = gettext_lazy('Site administration')
#
#
# admin_site = MyAdminSite()
