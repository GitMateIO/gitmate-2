from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import QuerySet

from .models import Organization
from .models import Repository
from .models import SettingsBase


def divert_access_to_repos(repos: QuerySet(Repository), user: User):
    """
    Hands over the operating user access from one administrator to the next one
    for a repository.

    :param repos:   The list of repositories.
    :param user:    The user whose access is to be diverted.
    """
    for repo in repos.filter(user=user):
        if repo.admins.count() > 1:
            repo.admins.remove(user)
            repo.user = repo.admins.first()
            repo.save()


def divert_access_to_orgs(orgs: QuerySet(Organization), user: User):
    """
    Hands over the operating user access from one administrator to the next one
    for an organization.

    :param orgs:   The list of organizations.
    :param user:    The user whose access is to be diverted.
    """
    for org in orgs.filter(primary_user=user):
        if org.admins.count() > 1:
            org.admins.remove(user)
            org.primary_user = org.admins.first()
            org.save()


class _SettingsBaseModelFormTemplate(forms.ModelForm):
    # template methods / search fields go in here
    pass


class _SettingsBaseModelAdminTemplate(admin.ModelAdmin):
    # any relevant behavioural specifics
    search_fields = ('repo__full_name', )

    def __init__(self, model, site):
        self.list_display = [field.name for field in model._meta.fields
                             if field.name != 'id']
        super(_SettingsBaseModelAdminTemplate, self).__init__(model, site)


class _SettingsBaseGenericModelFormMeta(type):
    """
    A meta class to control admin form generation.

    Reference: http://stackoverflow.com/a/6581949
    """
    def __new__(cls, clsname, bases, attrs):
        # making sure we are using the correct class
        if len(bases) < 1:  # pragma: no cover
            raise ValueError('SettingsBaseAdminForm requires a base class')
        assert issubclass(bases[0], SettingsBase)

        meta = type('SettingsBaseAdminModelFormMeta',
                    (object, ),
                    {'model': bases[0], 'fields': '__all__'})
        class_dict = {'Meta': meta}

        # add user overrides, if specified
        class_dict.update(attrs)
        model_form = type(
            bases[0].__name__ + 'ModelForm',
            (_SettingsBaseModelFormTemplate, ),
            class_dict)
        return model_form


class SettingsBaseGenericModelAdminMeta(type):
    """
    ``type()`` magic for the ModelAdmin class.
    """
    def __new__(cls, clsname, bases, attrs):
        # making sure we are using the correct class
        if len(bases) < 1:  # pragma: no cover
            raise ValueError('SettingsBaseAdminForm requires a base class')

        # django ModelAdmin classes are required to have a Meta member class
        # with a 'model' attribute that points to the model type
        meta = type('SettingsBaseAdminModelAdminMeta',
                    (object, ),
                    {'model': bases[0]})
        class_dict = {'Meta': meta}

        # we want all our generic form behaviours to be inherited as well, so
        # add these to the attribute dict.
        class_dict['form'] = _SettingsBaseGenericModelFormMeta(
            clsname, bases, attrs)
        class_dict.update(attrs)
        model_admin = type(
            bases[0].__name__ + 'ModelAdmin',
            (_SettingsBaseModelAdminTemplate, ),
            class_dict)
        return model_admin


def register_all_setting_models(mixins=None, **attr_dict):
    if mixins is None:
        mixins = ()

    mixins = tuple(mixins)
    models = SettingsBase.__subclasses__()
    model_admins = [
        SettingsBaseGenericModelAdminMeta(x.__name__, (x,) + mixins, attr_dict)
        for x in models
    ]

    for model, model_admin in zip(models, model_admins):
        admin.site.register(model, model_admin)
