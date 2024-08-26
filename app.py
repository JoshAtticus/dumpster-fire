from datetime import datetime
from typing import List, Tuple
from uuid import uuid4
from nicegui import ui
from main import *

messages: List[Tuple[str, str, str]] = []

@ui.refreshable
def chat_messages(own_id: str) -> None:
    for user_id, text, stamp in messages:
        ui.chat_message(text=text, stamp=stamp, sent=own_id == user_id)
    ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')


@ui.page('/app')
async def main():
    def send() -> None:
        ui.notify('Sent!')
        stamp = datetime.utcnow().strftime('%X')
        messages.append((user_id, text.value, stamp))
        text.value = ''
        chat_messages.refresh()

    user_id = str(uuid4())   

    ui.html('<style>.bottom-fixed { position: 50; bottom: 0; left: 25; width: 97% }</style>')

    with ui.footer().classes('bg-white'):
        text = ui.input(placeholder='Message') \
            .props('rounded outlined').classes('flex-grow q-input') \
            .on('keydown.enter', send)
        ui.button('Send', on_click=send).classes('q-btn, bg-black')
        

    await ui.context.client.connected()  # chat_messages(...) uses run_javascript which is only possible after connecting
    with ui.column().classes('w-full max-w-2xl mx-auto items-stretch'):
        chat_messages(user_id)

ui.run()
