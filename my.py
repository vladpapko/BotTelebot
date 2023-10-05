import telebot
import pandas as pd
import io
from telebot.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

bot = telebot.TeleBot("6554033082:AAFrznSh96XATTzvoWe7NSGZ1XfusZMLvVI")

class Form:
    def __init__(self):
        self.name = None
        self.file_id = None
        self.file_content = None

form_data = {}

@bot.message_handler(commands=['start'])
def handle_start(message):
    form_data[message.chat.id] = Form()
    bot.send_message(message.chat.id, "Привет! Как тебя зовут?", reply_markup=ReplyKeyboardRemove())
    bot.register_next_step_handler(message, process_name)

def process_name(message):
    form_data[message.chat.id].name = message.text
    bot.send_message(message.chat.id, f"Отлично, {message.text}! Теперь отправь мне файл с оценками (формат xlsx).")
    bot.register_next_step_handler(message, process_file_upload)

def process_file_upload(message):
    file_id = message.document.file_id
    form_data[message.chat.id].file_id = file_id
    bot.send_message(message.chat.id, "Файл успешно загружен! Теперь укажи наименование группы.")
    bot.register_next_step_handler(message, process_group_choice)

def process_group_choice(message):
    group = message.text
    data = form_data[message.chat.id]

    if not data.file_id:
        bot.send_message(message.chat.id, "Ошибка: Файл не был загружен.")
        return

    file_info = bot.get_file(data.file_id)

    # Загружаем содержимое файла
    file_content = bot.download_file(file_info.file_path)
    data.file_content = file_content

    # читает файл
    df = pd.read_excel(io.BytesIO(file_content))

    # Фильтруем данные по группе
    group_data = df[df['Группа'] == group]

    total_grades = len(group_data)
    student_ids = set(group_data['Личный номер студента'])
    control_types = set(group_data['Уровень контроля'])
    academic_years = set(group_data['Год'])

    report_text = (
        f"Анализ оценок для группы {group}:\n"
        f"Количество оценок в группе: {total_grades}\n"
        f"Личные номера студентов в группе: {', '.join(map(str, student_ids))}\n"
        f"Виды контроля: {', '.join(map(str, control_types))}\n"
        f"Данные представлены по следующим учебным годам: {', '.join(map(str, academic_years))}\n"
    )

    

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    back_button = KeyboardButton("Назад")
    markup.add(back_button)

    bot.send_message(message.chat.id, report_text, reply_markup=markup)

    bot.register_next_step_handler(message, handle_back_button)

def handle_back_button(message):
    if message.text.lower() == "назад":
        bot.send_message(message.chat.id, "Хорошо! Укажите группу для анализа.")
        bot.register_next_step_handler(message, process_group_choice)
    else:
        bot.send_message(message.chat.id, "Извините, не понял ваш запрос. Укажите новую группу.")

if __name__ == "__main__":
    bot.polling(none_stop=True)