#!/bin/bash

export DEVELOPMENT=True

if [ "$1" = "test" ]; then
    shift  # so that `test` is not passed to `manage.py test`
    coverage run --source='.' manage.py test $@
    coverage report --fail-under=98
    coverage html
    pylint $(git ls-files '*.py')
else
    python manage.py $@
fi
