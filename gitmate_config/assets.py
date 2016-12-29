from django_assets import Bundle
from django_assets import register
from webassets.filter import register_filter
from webassets_elm import Elm

register_filter(Elm)

elm_js = Bundle('client/GitMate.elm',
                filters=('elm',),
                output='client/gitmate.js',
                depends='client/**/*.elm')
register('elm_js', elm_js)
