import functools

from django import shortcuts

from safe import exceptions
from safe import models


def _logged_in(request):
    return 'user_id' in request.session


def _setup_session(request, user):
    request.session['user_id'] = user.id
    request.session['username'] = user.username


def default_data(func):
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        data = dict()
        if _logged_in(request):
            data['user_id'] = request.session['user_id']
            data['username'] = request.session['username']
        return func(request, data, *args, **kwargs)
    return wrapper


def default_template(template_name, require_auth=True):
    def decorator(func):
        @functools.wraps(func)
        @default_data
        def wrapper(request, data, *args, **kwargs):
            if require_auth and not _logged_in(request):
                return shortcuts.redirect('safe:login')

            result = func(request, data, *args, **kwargs)

            if result is None:
                return shortcuts.render(request, template_name, data)
            else:
                return result
        return wrapper
    return decorator


def _handle_register(request, data):
    username = request.POST['username']
    raw_password = request.POST['password']
    raw_password_repeat = request.POST['password_repeat']
    if raw_password != raw_password_repeat:
        data['warn_message'] = "Passwords must match!"
        return

    try:
        user = models.User.create(username, raw_password)
        _setup_session(request, user)
        return shortcuts.redirect('safe:index')
    except exceptions.UserAlreadyExists:
        data['warn_message'] = 'User %s already exists.' % username


@default_template('register.html', require_auth=False)
def register(request, data):
    if _logged_in(request):
        return shortcuts.redirect('safe:index')
    if request.method == 'POST':
        return _handle_register(request, data)


def _handle_login(request, data):
    username = request.POST['username']
    raw_password = request.POST['password']
    user = models.User.authenticate(username, raw_password)
    if user:
        _setup_session(request, user)
        return shortcuts.redirect('safe:index')
    else:
        data['warn_message'] = 'Incorrect username or password.'


@default_template('login.html', require_auth=False)
def login(request, data):
    if request.method == 'POST':
        return _handle_login(request, data)


@default_template('index.html')
def index(request, data):
    user_id = request.session['user_id']
    password_names = models.Password.get_user_password_names(user_id)
    data['password_names'] = password_names


@default_template('login.html')
def logout(request, data):
    request.session.flush()
    del data['user_id']
    del data['username']
    data['message'] = 'You are now logged out.'


@default_template('index.html')
def create_password(request, data):
    if request.method == 'POST':
        user_id = request.session['user_id']
        name = request.POST['name']
        password = request.POST['password']
        key = request.POST['key']
        models.Password.create(user_id, name, password, key)
        return shortcuts.redirect('safe:index')


@default_template('show_password.html')
def show_password(request, data):
    if request.method == 'POST':
        user_id = request.session['user_id']
        name = request.POST['name']
        key = request.POST['key']
        password = models.Password.get_password(user_id, name, key)
        data['password'] = {'name': name, 'password': password}


@default_template('index.html')
def delete_password(request, data):
    if request.method == 'POST':
        user_id = request.session['user_id']
        name = request.POST['name']
        models.Password.delete_password(user_id, name)
        return shortcuts.redirect('safe:index')
