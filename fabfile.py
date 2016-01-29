from fabric.api import run, cd, env, lcd, sudo, put, local, task

local_docs_folder = 'docs/'


@task
def install_dependencies():
    local('npm install')
    local('pip install -r requirements.txt')


@task
def run_tests():
    local("py.test --cov=app --cov-report term-missing tests")

@task
def migrator():
    local("python scripts/migrator.py")


@task
def generate_docs():
    with(lcd(local_docs_folder)):
        local("make rst && make html")


@task
def locale(locale_task):
    """
    fab locale:locale_task
    :param locale_task: Name of the locale task to do: [extract|init|update|compile]
    :return:
    """
    if locale_task == "extract":
        local("pybabel extract -F babel.cfg -o locales/messages.pot app")
    if locale_task == "init":
        local("pybabel init -i locales/messages.pot -d app/translations -l es")
    if locale_task == "update":
        local("pybabel extract -F babel.cfg -o locales/messages.pot app")
        local("pybabel update -i locales/messages.pot -d app/translations")
    if locale_task == "compile":
        local("pybabel compile -d app/translations")

