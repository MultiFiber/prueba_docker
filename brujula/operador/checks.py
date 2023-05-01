import django, ast
from django.core import checks
from django.core.checks import Warning, Error, Info
import inspect


def check_model(model):
    if True:
        yield Warning(
            'Field has no verbose name',
            hint='Set verbose name on field {}.'.format('5'),
            obj=52,
            id='EM_001',
        )


@checks.register(checks.Tags.models)
def check_models(app_configs, **kwargs):
    errors = []
    for app in django.apps.apps.get_app_configs():

        # Skip third party apps.
        if app.path.find('site-packages') > -1:
            continue

        for model in app.get_models():
            for check_message in check_model(model):
                errors.append(check_message)


    # errors.append(Info(
    #         'Field has no verbose name',
    #         hint='Set verbose name on field {}.'.format('5'),
    #         obj=52,
    #         id='H002',
    #     ))

    return errors       