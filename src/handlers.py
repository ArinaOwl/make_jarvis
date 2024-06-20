from aiogram import F, Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram import flags
from aiogram.fsm.context import FSMContext

from states import BotStates
import kb
import texts
from models import LlamaChat, STT, TTS

router = Router()
tts = TTS()
stt = STT()
chat = LlamaChat()


@router.message(Command("start"))
async def start_handler(msg: Message, state: FSMContext):
    """Обработчик команды \\start"""
    await state.set_state(BotStates.menu)
    await msg.answer(texts.start, reply_markup=kb.menu)


@router.callback_query(F.data == "help")
async def menu_help_handler(clbck: CallbackQuery):
    """Обработчик команды 'Помощь' (кнопка интерактивной клавиатуры)"""
    await clbck.message.edit_text(texts.help, reply_markup=kb.menu)


@router.message(Command("help"))
@router.message(BotStates.menu, F.voice)
async def help_handler(msg: Message):
    """Обработчик команды \\help или голосового сообщения вне тренировки"""
    await msg.answer(texts.help, reply_markup=kb.menu)


@router.callback_query(F.data == "practice")
async def menu_help_handler(clbck: CallbackQuery, state: FSMContext):
    """Обработчик команды 'Практика' (кнопка интерактивной клавиатуры)"""
    chat.reset_msg()
    await state.set_state(BotStates.practice)
    await clbck.message.edit_text(texts.practice)


@router.message(BotStates.practice, F.text)
@flags.chat_action("typing")
async def practice(msg: Message):
    """Чат с llama"""
    chat.add_msg(msg.text)
    answer = chat.get_llama_answer()
    chat.add_msg(answer)

    await msg.answer(answer)


@router.message(BotStates.practice, F.voice)
@flags.chat_action("typing")
async def practice_voice(msg: Message, bot: Bot):
    """Голосовой чат с llama"""

    file_id = msg.voice.file_id
    file = await bot.get_file(file_id)
    await bot.download_file(file.file_path, destination='src/audio/message.ogg')

    text = stt.run("src/audio/message.ogg")

    chat.add_msg(text)
    answer = chat.get_llama_answer()
    chat.add_msg(answer)

    tts.run(answer, 'src/audio/answer.ogg')

    if len(answer) > 0:
        await msg.answer(answer)
    await bot.send_voice(msg.from_user.id, FSInputFile("src/audio/answer.ogg"))

