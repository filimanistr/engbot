from aionuts.dispatcher.handler import CancelHandler
from aionuts.dispatcher.middlewares import BaseMiddleware
from config import ERROR_EMPTY_MESSAGE

class ContentMiddleware(BaseMiddleware):
    """Checks if message is empty"""
    async def on_process_message(self, message, _):
        # Exception 
        if message.get_command() in ('/h', '/help'):
            return

        text = message.text
        if message.is_command():
            text = message.get_args()

        if text == '':
            await message.answer(ERROR_EMPTY_MESSAGE)
            raise CancelHandler()
