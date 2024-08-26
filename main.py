from typing import Optional
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from nicegui import Client, app, ui
import bcrypt  # Import bcrypt for hashing passwords
from app import *

# A dictionary to store usernames and hashed passwords
passwords = {'test1': bcrypt.hashpw('test1'.encode(), bcrypt.gensalt()).decode(),
             'test2': bcrypt.hashpw('test2'.encode(), bcrypt.gensalt()).decode()}

unrestricted_page_routes = {'/login', '/signup'}


class AuthMiddleware(BaseHTTPMiddleware):
    """This middleware restricts access to all NiceGUI pages.

    It redirects the user to the login page if they are not authenticated.
    """

    async def dispatch(self, request: Request, call_next):
        if not app.storage.user.get('authenticated', False):
            if request.url.path in Client.page_routes.values() and request.url.path not in unrestricted_page_routes:
                app.storage.user['referrer_path'] = request.url.path  # remember where the user wanted to go
                return RedirectResponse('/login')
        return await call_next(request)


app.add_middleware(AuthMiddleware)


@ui.page('/')
def main_page() -> None:
    with ui.column().classes('absolute-center items-center'):
        ui.label(f'Hello {app.storage.user["username"]}!').classes('text-2xl')
        ui.button(on_click=lambda: (app.storage.user.clear(), ui.navigate.to('/login')), icon='logout') \
            .props('outline round')
        ui.button('Go to app', on_click=lambda: ui.navigate.to('/app'))


@ui.page('/subpage')
def test_page() -> None:
    ui.label('This is a sub page.')


@ui.page('/login')
def login() -> Optional[RedirectResponse]:
    def try_login() -> None:
        stored_hash = passwords.get(username.value)
        if stored_hash and bcrypt.checkpw(password.value.encode(), stored_hash.encode()):
            app.storage.user.update({'username': username.value, 'authenticated': True})
            ui.navigate.to(app.storage.user.get('referrer_path', '/'))  # go back to where the user wanted to go
        else:
            ui.notify('Wrong! Try again or email contactblaze@proton.me for support', color='negative')

    if app.storage.user.get('authenticated', False):
        return RedirectResponse('/')
    with ui.card().classes('absolute-center'):
        username = ui.input('Username').on('keydown.enter', try_login)
        password = ui.input('Password', password=True, password_toggle_button=True).on('keydown.enter', try_login)
        ui.button('Log in', on_click=try_login)
        ui.button('Sign Up', on_click=lambda: ui.navigate.to('/signup'))
    return None


@ui.page('/signup')
def signup() -> Optional[RedirectResponse]:
    def create_account() -> None:
        if username.value in passwords:
            ui.notify('Username already exists!', color='negative')
        else:
            hashed_password = bcrypt.hashpw(password.value.encode(), bcrypt.gensalt()).decode()
            passwords[username.value] = hashed_password
            app.storage.user.update({'username': username.value, 'authenticated': True})
            ui.notify('Account created successfully!', color='positive')
            ui.navigate.to('/')  # Redirect to the main page after sign-up

    if app.storage.user.get('authenticated', False):
        return RedirectResponse('/')
    with ui.card().classes('absolute-center'):
        username = ui.input('Choose a Username').on('keydown.enter', create_account)
        password = ui.input('Choose a Password', password=True, password_toggle_button=True).on('keydown.enter', create_account)
        ui.button('Sign up', on_click=create_account)
    return None


ui.run(storage_secret='THIS_NEEDS_TO_BE_CHANGED')
