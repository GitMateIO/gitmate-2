from django.contrib import admin

from gitmate_logger.models import Error


class ErrorAdmin(admin.ModelAdmin):
    """
    Class that controls display of errors in admin panel.
    """
    list_display = ('path', 'kind', 'info', 'when')
    list_display_links = ('path', )
    ordering = ('-id', )
    search_fields = ('path', 'kind', 'info', 'data')
    readonly_fields = ('path', 'kind', 'info', 'data', 'when')
    fieldsets = ((None, {'fields': ('kind', 'path', 'info', 'when')}),)

    def has_delete_permission(self, request, obj=None):
        """
        Enabling the delete permissions.
        """
        return True

    def has_add_permission(self, request):
        """
        Disabling the create permissions.
        """
        return False

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        The detail view of the error record.
        """
        extra_context = extra_context or {}
        obj = self.get_object(request, admin.utils.unquote(object_id))

        extra_context.update({
            'instance': obj,
            'error_body': obj.data,
        })

        return super(ErrorAdmin, self).change_view(
            request, object_id, form_url, extra_context=extra_context)


admin.site.register(Error, ErrorAdmin)
