from urllib.parse import quote_plus

from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html

from gitmate_logger.models import Error


class ErrorAdmin(admin.ModelAdmin):
    """
    Class that controls display of errors in admin panel.
    """
    list_display = ('path', 'kind', 'info', 'when', 'error_actions')
    list_display_links = ('path', )
    ordering = ('-id', )
    search_fields = ('path', 'kind', 'info', 'data')
    readonly_fields = ('path', 'kind', 'info', 'data', 'when', 'error_actions')
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
        self.user_name = request.user.username
        obj = self.get_object(request, admin.utils.unquote(object_id))

        extra_context.update({
            'instance': obj,
            'error_body': obj.data,
            'issue_link': self.error_actions(obj)
        })

        return super(ErrorAdmin, self).change_view(
            request, object_id, form_url, extra_context=extra_context)

    def changelist_view(self, request, extra_context=None):
        self.user_name = request.user.username
        return super(ErrorAdmin, self).changelist_view(
            request, extra_context=extra_context)

    def error_actions(self, error):
        title = quote_plus('{} on {}'.format(error.kind, error.path))
        desc = quote_plus('Traceback: ```{}```\n\n'
                          'Kind: `{}`\n\nInfo: `{}`\n\nWhen: {}\n\n'
                          'Submitted by {} via GitMate Error console'.format(
                              error.data,
                              error.kind,
                              error.info,
                              error.when,
                              self.user_name))
        return format_html(
            '<a class="button" href="{}" target="_blank">File Issue</a>',
            settings.ISSUE_REPORT_URL.format(title=title, description=desc))

    # Don't move above the methods, as it is not defined yet.
    error_actions.short_description = 'Actions'
    error_actions.allow_tags = True


admin.site.register(Error, ErrorAdmin)
