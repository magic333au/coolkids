import logging
import re
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота
API_TOKEN = '8080145988:AAEC2ZnTEwfwJk_5NNaNb2vZ2tIQYkyFfmQ'

# chat_id
NOTIFY_CHAT_ID = -4769417229 

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Хранение записей пользователей
user_registrations = {}

# Состояния для FSM
class Form(StatesGroup):
    waiting_for_event = State()
    
    # Взрослые мероприятия
    waiting_for_mafia_option = State()
    waiting_for_mafia_questions = State()
    waiting_for_mafia_locations_keyboard = State()
    waiting_for_mafia_date = State()
    waiting_for_mafia_registration = State()

    waiting_for_breakfast_option = State()
    waiting_for_breakfast_question = State()
    waiting_for_breakfast_date = State()
    waiting_for_breakfast_registration = State()

    waiting_for_lecture_option = State()
    waiting_for_lecture_topic = State()
    waiting_for_lecture_registration = State()

    # Детские мероприятия
    waiting_for_birthday_option = State()

    waiting_for_masterclass_option = State()
    waiting_for_masterclass_type = State()
    waiting_for_masterclass_info = State()
    waiting_for_masterclass_schedule = State()
    waiting_for_masterclass_registration = State()

    waiting_for_camp_option = State()
    waiting_for_camp_details = State()
    waiting_for_camp_registration = State()

    waiting_for_chess_option = State()
    waiting_for_chess_data = State()
    waiting_for_drawing_option = State()
    waiting_for_drawing_registration = State()

    waiting_for_english_option = State()
    waiting_for_english_age = State()
    waiting_for_english_registration = State()

    waiting_for_school_prep_option = State()
    waiting_for_school_prep_registration = State()

    waiting_for_camp_back_to_description = State()
    waiting_for_user_data = State()

# Мероприятия
events = {
    "adult": {
        "Завтрак на английском": {
            "description": "Уютный завтрак с обсуждением фильма на английском языке! Это отличная возможность попрактиковать разговорный английский в непринуждённой атмосфере, а также провести время в компании единомышленников.",
            "price": "1000 руб",
            "film": "На этой неделе мы смотрим и обсуждаем фильм 'The Grand Budapest Hotel' (2014) режиссера Уэса Андерсона.",
            "locations": {
                "Чача": ["Среда 11:00", "Воскресенье 11:00"],
                "Лофт": ["Среда 11:00", "Воскресенье 11:00"]
            },
            "addresses": {
                "Чача": "Шлиссельбургский проспект д.3",
                "Лофт": "Рыбацкий проспект 23"
            }
        },
        "Мафия 18+": {
            "description": "Готовы примерить на себя роль мафиози или раскрыть преступление?\n\nУ нас собирается закрытая игра в «Мафию» для взрослых!\n\nВас ждёт захватывающая игра в компании интересных людей, где каждый может стать героем или хитрым злодеем.\n\nНастоящие эмоции, неожиданные повороты и море веселья — всё это «Мафия 18+»!\n\nГотовы испытать себя?",
            "price": "800 руб",
            "newbie_info": "Не переживайте! Даже если вы ни разу не играли — ведущий всё объяснит, поддержит и поможет влиться в игру.\n\nГлавное — желание веселиться и общаться!",
            "locations": {
                "Лофт": ["Пятница 19:00", "Суббота 19:00"]
            },
            "address": "Рыбацкий проспект 23/2"
        },
        "Лекции": {
            "description": "🌟 Хотите быть в курсе самых актуальных тем в образовании, воспитании и саморазвитии?\n\nТеперь не нужно ехать в центр города — у нас в Рыбацком проходят живые встречи с экспертами и единомышленниками!",
            "address": "Рыбацкий проспект 23/2",
            "lectures": {
                "Навыки XXI века и ИИ": {
                    "title": "Как подготовить ребёнка к будущему: навыки XXI века и роль искусственного интеллекта",
                    "description": "Что важно развивать в детях уже сегодня, чтобы они были успешными завтра? Как технологии и ИИ влияют на их жизнь?",
                    "date": "Каждый второй вторник месяца в 19:00"
                },
                "Финское образование": {
                    "title": "Современные методы обучения: почему у финских школьников нет домашних заданий, а результаты — лучшие в мире?",
                    "description": "Что мы можем взять на заметку для своих детей? Какие подходы действительно работают?",
                    "date": "Каждый второй четверг месяца в 19:00"
                },
                "Эмоциональный интеллект": {
                    "title": "Эмоциональный интеллект у взрослых: зачем он нужен и как развивать дома и на работе",
                    "description": "Как стать счастливее, успешнее и гармоничнее, понимая свои чувства и эмоции других?",
                    "date": "Каждую последнюю субботу месяца в 17:00"
                }
            },
            "price": "500 руб"
        }
    },
    "child": {
        "Детский день рождения": {
            "description": "Волшебный день рождения для вашего ребёнка!",
            "details": "Подарите своему ребёнку настоящий праздник — яркий, весёлый и незабываемый!\n\n"
                      "Мы организуем детские дни рождения «под ключ»: захватывающие шоу-программы, любимые герои, "
                      "интерактивные игры, творческие мастер-классы и море радости для каждого гостя.\n\n"
                      "Ваша задача — только наслаждаться счастливыми улыбками, обо всём остальном позаботимся мы.\n\n"
                      "Безопасность, индивидуальный подход, профессиональные аниматоры и атмосфера настоящей сказки — "
                      "ваш ребёнок и его друзья будут в восторге!\n\n"
                      "Давайте вместе сделаем этот день особенным и наполненным чудесами!",
            "additional_info": "Почему именно мы?\n"
                               "• Профессиональный подход: Наша команда состоит из опытных педагогов, которые знают, как взаимодействовать с детьми и создавать для них увлекательные и безопасные праздники.\n"
                               "• Индивидуальные программы: Мы разрабатываем каждую программу с учетом возраста, интересов и особенностей вашего ребенка. Каждый праздник — это уникальное приключение!\n"
                               "• Развитие через игру: Мы не просто развлекаем, но и обучаем! Наши мероприятия способствуют развитию социальных навыков, креативности и уверенности в себе."
        },
        "Мастер-класс в Чаче": {
            "description": "🍕🍔🍡 Привет! Хотите, чтобы ваш ребёнок попробовал себя в роли настоящего шеф-повара?",
            "details": "В ресторане «Чача» мы проводим весёлые и вкусные мастер-классы для детей!",
            "options": {
                "Пицца": "Дети учатся готовить настоящую пиццу с разными начинками!",
                "Гамбургеры": "Мастер-класс по приготовлению сочных бургеров",
                "Кей-попсы": "Яркие и вкусные кей-попсы - любимое лакомство детей",
                "Все варианты": "Мы предлагаем разнообразные мастер-классы для детей разного возраста!"
            },
            "schedule": {
                "Пицца": "Суббота 12:00",
                "Гамбургеры": "Воскресенье 12:00",
                "Кей-попсы": "Суббота 15:00"
            },
            "price": "1500 руб",
            "address": "Шлиссельбургский проспект д.3",
            "info": "Все мастер-классы проходят в уютной и безопасной атмосфере ресторана «Чача», подходят для детей от 5 лет.\n"
                    "В стоимость входит всё необходимое: продукты, фартук, диплом маленького повара и море позитива!"
        },
        "Шахматы": {
            "description": "♟️ Привет! Хотите, чтобы ваш ребёнок провёл лето интересно и с пользой?",
            "details": "В центре CoolKids каждую неделю проходят увлекательные шахматные игры для детей!",
            "schedule": "Мы играем в шахматы по понедельникам в 17:00 и 18:00",
            "price": "700 руб за занятие",
            "address": "Рыбацкий проспект 23/2"
        },
        "Рисование": {
            "description": "🎨 Рисование — это море вдохновения, развитие воображения и новые друзья!",
            "details": "На наших занятиях дети пробуют разные техники, создают уникальные картины и учатся выражать себя через творчество.",
            "schedule": "Занятия проходят по понедельникам в 17:00 и 18:00",
            "price": "700 руб за занятие",
            "address": "Рыбацкий проспект 23/2",
            "info": "Все материалы предоставляются, а работы можно забирать домой!"
        },
        "Городской лагерь": {
            "description": "🌞 Ищете, чем занять ребёнка летом, чтобы было интересно, полезно и безопасно?",
            "details": "У нас есть крутые городские лагеря с уникальными программами для детей!",
            "camps": {
                "Дети в бизнесе": {
                    "dates": "9-13 июня",
                    "description": "Погружаемся в захватывающий мир бизнеса! На этой смене дети попробуют себя в роли предпринимателей: научатся генерировать идеи, создавать свой мини-бизнес, работать в команде, вести переговоры и даже презентовать свой проект. В программе — креативные мастер-классы, игры на развитие финансовой грамотности, экскурсия в настоящий бизнес-центр и, конечно, море вдохновения!"
                },
                "Приключение с Гарри Поттером": {
                    "dates": "16-20 июня",
                    "description": "Волшебная неделя для настоящих фанатов Гарри Поттера! Ребята попадут в атмосферу Хогвартса: распределятся по факультетам, будут учиться магическим наукам, искать тайные послания, варить зелья и сразятся в квиддич. В программе — тематические квесты, мастер-классы, творческие задания и экскурсия в «волшебное» место города!"
                },
                "Мир эмоций": {
                    "dates": "7-11 июля",
                    "description": "Неделя, посвящённая эмоциональному интеллекту и дружбе! Дети узнают, как понимать и выражать свои чувства, учиться договариваться, поддерживать друг друга и находить новых друзей. В программе — тренинги на развитие эмпатии, творческие занятия, арт-терапия, активные игры и экскурсия в центр творчества!"
                },
                "Ярмарка профессий": {
                    "dates": "14-18 июля",
                    "description": "Погружение в мир разных профессий! Каждый день — новая специальность: от врача до архитектора, от журналиста до шеф-повара. Дети попробуют себя в разных ролях, пообщаются с настоящими профессионалами, поучаствуют в мастер-классах и экскурсиях. Это отличный шанс узнать больше о мире взрослых и найти своё призвание!"
                },
                "Подготовка к школе": {
                    "dates": "18-22 августа",
                    "description": "Идеальная смена для тех, кто хочет легко и весело войти в новый учебный год! Мы повторим школьную программу в игровой форме, потренируем память и внимание, разовьём навыки общения и самостоятельности. В программе — занятия с педагогами, полезные мастер-классы, прогулки, подвижные игры и экскурсия."
                },
                "Школа блогеров": {
                    "dates": "25-29 августа",
                    "description": "Неделя для будущих звёзд интернета! Дети узнают, как создавать интересные видео, вести свой блог, снимать сторис и монтировать ролики. В программе — основы работы с камерой и микрофоном, секреты успешных блогеров, творческие задания, командные проекты и экскурсия в медиа-студию!"
                }
            },
            "price": "13 500₽ за смену",
            "address": "Рыбацкий проспект 23/2",
            "info": "Каждая смена включает:\n• пребывание в центре с 10:00 до 17:00\n• комплексный обед и полезный перекус\n• прогулки на свежем воздухе\n• занятия английским\n• активные игры\n• экскурсию по теме смены"
        },
        "Курсы английского языка": {
            "description": "Хотите, чтобы ваш ребёнок учил английский с удовольствием и легко?",
            "details": "В Центре детского развития CoolKids открыта запись на пробные занятия по английскому языку для детей разных возрастов!",
            "schedule": {
                "4–5 лет": ["26 августа в 18:00"],
                "6–7 лет": ["26 августа в 19:00", "28 августа в 18:00"],
                "8–10 лет": ["28 августа в 19:00"],
                "Старше 10 лет": ["Индивидуальное интервью с преподавателем"]
            },
            "price": "Первое пробное занятие - бесплатно!",
            "address": "Рыбацкий проспект 23/2",
            "info": "Наши занятия проходят в игровой форме с использованием современных методик обучения. Мы делаем акцент на разговорной практике и преодолении языкового барьера."
        },
        "Подготовка к школе": {
            "description": "В нашем центре проводится летняя подготовка к школе.",
            "details": "Занятия включают:\n✔️ Математику\n✔️ Чтение\n✔️ Окружающий мир\n✔️ Письмо",
            "price": "Стоимость абонемента: 4800 руб",
            "schedule": {
                "Среда": "17:00",
                "Суббота": "18:00"
            },
            "address": "Рыбацкий проспект 23/2"
        },
        "Курсы китайского языка": {},
        "Медиа-студия": {},
        "Театральная студия": {}
    }
}

# Валидация данных
def validate_name(name: str) -> bool:
    """Проверяет, что имя состоит только из букв и имеет разумную длину"""
    return bool(re.fullmatch(r'^[а-яА-ЯёЁa-zA-Z\s\-]{2,50}$', name.strip()))

def validate_phone(phone: str) -> bool:
    """Проверяет корректность номера телефона"""
    phone = re.sub(r'[^\d]', '', phone)
    return len(phone) in (10, 11) and phone.isdigit()

def validate_age(age: str) -> bool:
    """Проверяет корректность возраста"""
    return age.isdigit() and 1 <= int(age) <= 120

def parse_user_data(text: str) -> dict:
    """Парсит введенные пользователем данные"""
    # Удаляем лишние пробелы и разделяем на части
    parts = [p.strip() for p in text.split() if p.strip()]
    
    data = {
        'name': None,
        'age': None,
        'phone': None,
        'other': []
    }
    
    # Ищем телефон в любом месте строки
    phone_match = re.search(r'(\+7|8|7)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}', text)
    if phone_match:
        data['phone'] = re.sub(r'[^\d]', '', phone_match.group())
        # Удаляем телефон из частей
        parts = [p for p in parts if not re.search(r'(\+7|8|7)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}', p)]
    
    # Ищем возраст (число с "лет" или без)
    age_match = None
    for i, part in enumerate(parts):
        if part.isdigit() and 1 <= int(part) <= 120:
            age_match = part
            data['age'] = age_match
            del parts[i]
            break
        elif re.fullmatch(r'\d+\s*лет', part.lower()):
            age_match = re.sub(r'\D', '', part)
            if age_match.isdigit() and 1 <= int(age_match) <= 120:
                data['age'] = age_match
                del parts[i]
                break
    
    # Оставшиеся части - имя и дополнительная информация
    if parts:
        data['name'] = ' '.join(parts[:2]) if len(parts) >= 2 else parts[0]
        data['other'] = parts[2:] if len(parts) > 2 else []
    
    return data

def format_registration(data: dict) -> str:
    """Форматирует данные для записи в унифицированном формате"""
    parts = []
    if data.get('name'):
        parts.append(data['name'])
    if data.get('age'):
        parts.append(f"{data['age']} лет")
    if data.get('phone'):
        phone = data['phone']
        # Форматируем телефон в формате 89123456789
        if len(phone) == 11 and phone.startswith('8'):
            phone = phone[1:]
        elif len(phone) == 11 and phone.startswith('7'):
            phone = '8' + phone[1:]
        parts.append(phone)
    if data.get('other'):
        parts.extend(data['other'])
    
    return ' '.join(parts)

# Клавиатуры
def get_start_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Начать",
        callback_data="start")
    )
    return builder.as_markup()

def get_event_type_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Взрослое",
        callback_data="adult")
    )
    builder.add(types.InlineKeyboardButton(
        text="Детское",
        callback_data="child")
    )
    builder.adjust(1)
    return builder.as_markup()

def get_adult_events_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Завтрак на английском",
        callback_data="breakfast")
    )
    builder.add(types.InlineKeyboardButton(
        text="Мафия 18+",
        callback_data="mafia")
    )
    builder.add(types.InlineKeyboardButton(
        text="Лекции",
        callback_data="lectures")
    )
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="back_to_start")
    )
    builder.adjust(1)
    return builder.as_markup()

def get_child_events_keyboard():
    builder = InlineKeyboardBuilder()
    for event in events["child"].keys():
        if event in ["Курсы китайского языка", "Медиа-студия", "Театральная студия"]:
            continue
        builder.add(types.InlineKeyboardButton(
            text=event,
            callback_data=f"child_{event.replace(' ', '_')}")
        )
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="back_to_event_type")
    )
    builder.adjust(1)
    return builder.as_markup()

def get_school_prep_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Да, интересно",
        callback_data="school_prep_yes")
    )
    builder.add(types.InlineKeyboardButton(
        text="Нет, спасибо",
        callback_data="child_back")
    )
    builder.adjust(1)
    return builder.as_markup()

def get_school_prep_details_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Записаться",
        callback_data="school_prep_register")
    )
    builder.add(types.InlineKeyboardButton(
        text="Нет, не интересно",
        callback_data="back_to_start")
    )
    builder.adjust(1)
    return builder.as_markup()

def get_school_prep_schedule_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Среда 17:00",
        callback_data="school_prep_wed")
    )
    builder.add(types.InlineKeyboardButton(
        text="Суббота 18:00",
        callback_data="school_prep_sat")
    )
    builder.adjust(1)
    return builder.as_markup()

def get_school_prep_success_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Вернуться в главное меню",
        callback_data="to_main_menu")
    )
    builder.adjust(1)
    return builder.as_markup()

def get_breakfast_options_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Когда и где?",
        callback_data="breakfast_when_where")
    )
    builder.add(types.InlineKeyboardButton(
        text="Зачем мне это?",
        callback_data="breakfast_why")
    )
    builder.add(types.InlineKeyboardButton(
        text="Хочу зарегистрироваться",
        callback_data="breakfast_register")
    )
    builder.add(types.InlineKeyboardButton(
        text="А какая цена?",
        callback_data="breakfast_price")
    )
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="back_to_adult_events")
    )
    builder.adjust(1)
    return builder.as_markup()

def get_breakfast_back_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="breakfast_back")
    )
    return builder.as_markup()

def get_breakfast_why_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="А какой фильм?",
        callback_data="breakfast_film")
    )
    builder.add(types.InlineKeyboardButton(
        text="Хочу зарегистрироваться",
        callback_data="breakfast_register")
    )
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="breakfast_back")
    )
    builder.adjust(1)
    return builder.as_markup()

def get_breakfast_locations_keyboard():
    builder = InlineKeyboardBuilder()
    for location in events["adult"]["Завтрак на английском"]["locations"].keys():
        builder.add(types.InlineKeyboardButton(
            text=location,
            callback_data=f"breakfast_loc_{location}")
        )
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="breakfast_back")
    )
    builder.adjust(1)
    return builder.as_markup()

def get_breakfast_dates_keyboard(location):
    builder = InlineKeyboardBuilder()
    for date in events["adult"]["Завтрак на английском"]["locations"][location]:
        builder.add(types.InlineKeyboardButton(
            text=date,
            callback_data=f"breakfast_date_{date}")
        )
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="breakfast_back_to_locations")
    )
    builder.adjust(1)
    return builder.as_markup()

def get_mafia_options_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="Когда и где?",
            callback_data="mafia_when_where"
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="А если я новичок?",
            callback_data="mafia_newbie"
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Записаться",
            callback_data="mafia_register"
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="back_to_adult_events"
        )
    )
    return builder.as_markup()

def get_mafia_newbie_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Отлично, хочу попробовать!",
        callback_data="mafia_when_where")
    )
    builder.add(types.InlineKeyboardButton(
        text="У меня остались вопросы",
        callback_data="mafia_questions")
    )
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="mafia_back")
    )
    builder.adjust(1)
    return builder.as_markup()

def get_mafia_locations_keyboard():
    builder = InlineKeyboardBuilder()
    for location in events["adult"]["Мафия 18+"]["locations"].keys():
        builder.add(types.InlineKeyboardButton(
            text=location,
            callback_data=f"mafia_loc_{location}"
        ))
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="mafia_back"
    ))
    builder.adjust(1)
    return builder.as_markup()

def get_mafia_dates_keyboard(location):
    builder = InlineKeyboardBuilder()
    for date in events["adult"]["Мафия 18+"]["locations"][location]:
        builder.row(
            types.InlineKeyboardButton(
                text=date,
                callback_data=f"mafia_date_{date}"
            )
        )
    builder.row(
        types.InlineKeyboardButton(
            text="⬅️ Назад к выбору места",
            callback_data="mafia_back_to_locations"
        )
    )
    return builder.as_markup()

def get_mafia_registration_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="mafia_back_to_dates")
    )
    return builder.as_markup()

def get_birthday_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Связаться с администратором",
        url="https://t.me/alinarolina")
    )
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Вернуться к выбору мероприятия",
        callback_data="child_back")
    )
    builder.adjust(1)
    return builder.as_markup()

def get_chess_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Да, расскажи!",
        callback_data="chess_more")
    )
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Вернуться к выбору мероприятия",
        callback_data="child_back")
    )
    builder.adjust(1)
    return builder.as_markup()

def get_chess_options_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Когда проходят занятия?",
        callback_data="chess_schedule")
    )
    builder.add(types.InlineKeyboardButton(
        text="Сколько стоит?",
        callback_data="chess_price")
    )
    builder.add(types.InlineKeyboardButton(
        text="Записаться!",
        callback_data="chess_register")
    )
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="chess_back_to_main")
    )
    builder.adjust(1)
    return builder.as_markup()

def get_chess_schedule_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Сколько стоит?",
        callback_data="chess_price")
    )
    builder.add(types.InlineKeyboardButton(
        text="Записаться!",
        callback_data="chess_register")
    )
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="chess_back_to_options")
    )
    builder.adjust(1)
    return builder.as_markup()

def get_chess_price_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Записаться!",
        callback_data="chess_register")
    )
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="chess_back_to_options")
    )
    builder.adjust(1)
    return builder.as_markup()

def get_chess_success_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Вернуться в главное меню",
        callback_data="to_main_menu")
    )
    builder.adjust(1)
    return builder.as_markup()

def get_masterclass_types_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Пицца",
        callback_data="masterclass_pizza")
    )
    builder.add(types.InlineKeyboardButton(
        text="Гамбургеры",
        callback_data="masterclass_burgers")
    )
    builder.add(types.InlineKeyboardButton(
        text="Кей-попсы",
        callback_data="masterclass_cakepops")
    )
    builder.add(types.InlineKeyboardButton(
        text="Все варианты",
        callback_data="masterclass_all")
    )
    builder.add(types.InlineKeyboardButton(
        text="А где это и нужно ли что-то с собой?",
        callback_data="masterclass_info")
    )
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="masterclass_back")
    )
    builder.adjust(1)
    return builder.as_markup()

def get_masterclass_info_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Узнать расписание",
        callback_data="masterclass_schedule")
    )
    builder.add(types.InlineKeyboardButton(
        text="Записаться!",
        callback_data="masterclass_register")
    )
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Вернуться к выбору мероприятия",
        callback_data="child_back")
    )
    builder.adjust(1)
    return builder.as_markup()

def get_masterclass_schedule_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Записать ребёнка",
        callback_data="masterclass_register")
    )
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Вернуться к выбору мероприятия",
        callback_data="child_back")
    )
    builder.adjust(1)
    return builder.as_markup()

def get_lectures_intro_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="Да, расскажи!",
            callback_data="lectures_more"
        ),
        types.InlineKeyboardButton(
            text="Нет, спасибо",
            callback_data="back_to_adult_events"
        )
    )
    return builder.as_markup()

def get_lectures_topics_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="Подробнее о темах",
            callback_data="lectures_topics"
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Когда и где проходят лекции?",
            callback_data="lectures_when_where"
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="lectures_back"
        )
    )
    return builder.as_markup()

def get_lectures_when_where_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="Выбрать лекцию",
            callback_data="lectures_topics"
        ),
        types.InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="lectures_back"
        )
    )
    return builder.as_markup()

def get_lectures_list_keyboard():
    builder = InlineKeyboardBuilder()
    for lecture_key, lecture_data in events["adult"]["Лекции"]["lectures"].items():
        builder.row(
            types.InlineKeyboardButton(
                text=lecture_data["title"],
                callback_data=f"lecture_{lecture_key}"
            )
        )
    builder.row(
        types.InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="lectures_more"
        )
    )
    return builder.as_markup()

def get_lecture_detail_keyboard(lecture_key):
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="📝 Записаться",
            callback_data=f"lecture_register_{lecture_key}"
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="⬅️ Назад к списку лекций",
            callback_data="lectures_topics"
        )
    )
    return builder.as_markup()

def get_camp_intro_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Да, расскажи!",
        callback_data="camp_more"
    ))
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Вернуться к выбору мероприятия",
        callback_data="child_back"
    ))
    builder.adjust(1)
    return builder.as_markup()

def get_camp_options_keyboard():
    builder = InlineKeyboardBuilder()
    for camp_name, camp_data in events["child"]["Городской лагерь"]["camps"].items():
        builder.add(types.InlineKeyboardButton(
            text=f"{camp_name} — {camp_data['dates']}",
            callback_data=f"camp_{camp_name.replace(' ', '_')}"
        ))
    builder.add(types.InlineKeyboardButton(
        text="ℹ️ Подробнее о сменах",
        callback_data="camp_details"
    ))
    builder.add(types.InlineKeyboardButton(
        text="📝 Записаться",
        callback_data="camp_register"
    ))
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Назад к описанию",
        callback_data="camp_back_to_description"
    ))
    builder.adjust(1)
    return builder.as_markup()

def get_camp_details_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Остались вопросы, хочу связаться с администратором",
        url="https://t.me/alinarolina"
    ))
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Вернуться к выбору смен",
        callback_data="camp_more"
    ))
    builder.adjust(1)
    return builder.as_markup()

def get_camp_success_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Вернуться в главное меню",
        callback_data="to_main_menu"
    ))
    builder.adjust(1)
    return builder.as_markup()

def get_drawing_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Да, расскажи!",
        callback_data="drawing_more")
    )
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Вернуться к выбору мероприятия",
        callback_data="child_back")
    )
    builder.adjust(1)
    return builder.as_markup()

def get_drawing_options_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Когда проходят занятия?",
        callback_data="drawing_schedule")
    )
    builder.add(types.InlineKeyboardButton(
        text="Сколько стоит?",
        callback_data="drawing_price")
    )
    builder.add(types.InlineKeyboardButton(
        text="Записаться!",
        callback_data="drawing_register")
    )
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="drawing_back_to_main")
    )
    builder.adjust(1)
    return builder.as_markup()

def get_drawing_schedule_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Сколько стоит?",
        callback_data="drawing_price")
    )
    builder.add(types.InlineKeyboardButton(
        text="Записаться!",
        callback_data="drawing_register")
    )
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="drawing_back_to_options")
    )
    builder.adjust(1)
    return builder.as_markup()

def get_drawing_price_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Записаться!",
        callback_data="drawing_register")
    )
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="drawing_back_to_options")
    )
    builder.adjust(1)
    return builder.as_markup()

def get_english_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Да, расскажи!",
        callback_data="english_more")
    )
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Вернуться к выбору мероприятия",
        callback_data="child_back")
    )
    builder.adjust(1)
    return builder.as_markup()

def get_english_age_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="4-5 лет",
        callback_data="english_age_4_5")
    )
    builder.add(types.InlineKeyboardButton(
        text="6-7 лет",
        callback_data="english_age_6_7")
    )
    builder.add(types.InlineKeyboardButton(
        text="8-10 лет",
        callback_data="english_age_8_10")
    )
    builder.add(types.InlineKeyboardButton(
        text="Старше 10 лет",
        callback_data="english_age_10+")
    )
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="english_back")
    )
    builder.adjust(1)
    return builder.as_markup()

def get_english_schedule_keyboard(age_group):
    builder = InlineKeyboardBuilder()
    
    if age_group == "4–5 лет":
        builder.add(types.InlineKeyboardButton(
            text="Записаться",
            callback_data=f"english_register_{events['child']['Курсы английского языка']['schedule'][age_group][0]}")
        )
    elif age_group == "6–7 лет":
        for date in events["child"]["Курсы английского языка"]["schedule"][age_group]:
            builder.add(types.InlineKeyboardButton(
                text=f"Записаться на {date}",
                callback_data=f"english_register_{date}")
            )
    elif age_group == "8–10 лет":
        builder.add(types.InlineKeyboardButton(
            text="Записаться",
            callback_data=f"english_register_{events['child']['Курсы английского языка']['schedule'][age_group][0]}")
        )
    else:  # Старше 10 лет
        builder.add(types.InlineKeyboardButton(
            text="Оставить заявку",
            callback_data="english_register_individual")
        )
    
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="english_back_to_age")
    )
    builder.adjust(1)
    return builder.as_markup()

def get_english_success_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Вернуться в главное меню",
        callback_data="to_main_menu")
    )
    builder.adjust(1)
    return builder.as_markup()

def get_camp_selection_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Записаться на эту смену",
        callback_data="camp_register"
    ))
    builder.add(types.InlineKeyboardButton(
        text="⬅️ Вернуться к списку смен",
        callback_data="camp_more"
    ))
    builder.adjust(1)
    return builder.as_markup()

async def safe_edit_message(text: str, callback: types.CallbackQuery, reply_markup=None, state: FSMContext = None):
    try:
        await callback.message.edit_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        await callback.answer()
        return True
    except Exception as e:
        logger.error(f"Ошибка при редактировании сообщения: {e}")
        try:
            await callback.message.answer(
                text=text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
            await callback.answer()
            return True
        except Exception as e:
            logger.error(f"Ошибка при отправке нового сообщения: {e}")
            try:
                await callback.answer(
                    "Произошла ошибка, пожалуйста, попробуйте ещё раз",
                    show_alert=True
                )
            except:
                pass
            return False

async def save_user_registration(user_id: int, registration_data: dict):
    if user_id not in user_registrations:
        user_registrations[user_id] = []
    user_registrations[user_id].append(registration_data)

async def request_user_data(message: types.Message, state: FSMContext, event_type: str, instructions: str, example: str):
    """Универсальная функция для запроса данных пользователя с проверкой"""
    await state.update_data(event_type=event_type)
    await message.answer(
        f"✏️ <b>Запись на {event_type}</b>\n\n"
        f"{instructions}\n\n"
        f"<b>Пример:</b> <i>{example}</i>\n\n"
        "Если вы ошиблись при вводе, просто отправьте данные заново.",
        parse_mode=ParseMode.HTML
    )

async def validate_and_process_registration(message: types.Message, state: FSMContext, required_fields: list):
    """Универсальная функция для проверки и обработки данных регистрации"""
    try:
        user_data = await state.get_data()
        user_input = message.text.strip()
        
        # Парсим введенные данные
        parsed_data = parse_user_data(user_input)
        
        # Проверяем обязательные поля
        errors = []
        if 'name' in required_fields and not parsed_data.get('name'):
            errors.append("❌ Пожалуйста, укажите ваше имя")
            
        if 'phone' in required_fields and not parsed_data.get('phone'):
            errors.append("❌ Пожалуйста, укажите корректный номер телефона (например, 89123456789)")
            
        if 'age' in required_fields and not parsed_data.get('age'):
            errors.append("❌ Пожалуйста, укажите возраст")
            
        if errors:
            # Формируем сообщение с ошибками и примером
            example = "Неизвестный формат"  # Дефолтное значение
            
            # Приводим event_type к нижнему регистру и проверяем вхождение
            event_type = user_data.get('event_type', '').lower()
            
            if 'breakfast' in event_type:
                example = "Иванов Иван 89123456789"
            elif 'mafia' in event_type:
                example = "Иван 79123456789 2"
            elif 'lecture' in event_type:
                example = "Александр 79123456789 1"
            
            error_msg = "\n".join(errors) + f"\n\n<b>Пример правильного формата:</b>\n<code>{example}</code>"
            await message.answer(error_msg, parse_mode=ParseMode.HTML)
            return None
        
        # Форматируем данные для записи
        registration_details = format_registration(parsed_data)
        
        return registration_details
        
    except Exception as e:
        logger.error(f"Error validating registration: {e}")
        await message.answer(
            "❌ Ошибка при обработке ваших данных. Пожалуйста, попробуйте еще раз."
        )
        return None

@dp.message(Form.waiting_for_mafia_registration)
async def process_mafia_registration(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    text = message.text.strip()
    
    # Парсим введенные данные
    parts = text.split()
    if len(parts) < 3:
        await message.answer(
            "❌ Недостаточно данных. Пожалуйста, введите:\n"
            "Имя, телефон и количество человек\n\n"
            "<b>Пример:</b> <i>Иван 79123456789 2</i>",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Извлекаем количество людей (последний элемент)
    count_str = parts[-1]
    if not count_str.isdigit():
        await message.answer(
            "❌ Количество человек должно быть числом. Пожалуйста, введите:\n"
            "Имя, телефон и количество человек\n\n"
            "<b>Пример:</b> <i>Иван 79123456789 2</i>",
            parse_mode=ParseMode.HTML
        )
        return
    
    count = int(count_str)
    name = ' '.join(parts[:-2])
    phone = parts[-2]
    
    # Проверяем телефон
    phone_clean = re.sub(r'[^\d]', '', phone)
    if len(phone_clean) not in (10, 11) or not phone_clean.isdigit():
        await message.answer(
            "❌ Некорректный номер телефона. Пожалуйста, введите:\n"
            "Имя, телефон и количество человек\n\n"
            "<b>Пример:</b> <i>Иван 79123456789 2</i>",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Форматируем данные для записи
    registration_details = f"{name} {phone} {count}"
    
    # Сохраняем запись
    registration_data = {
        "event": "Мафия 18+",
        "details": registration_details,
        "date": user_data.get("date", ""),
        "location": user_data.get("location", ""),
        "timestamp": str(datetime.now())
    }
    await save_user_registration(message.from_user.id, registration_data)
    
    await bot.send_message(
        chat_id=NOTIFY_CHAT_ID,
        text=f"🎭 Новая запись на Мафию 18+:\n"
             f"📅 Дата: {user_data.get('date', 'не указана')}\n"
             f"📍 Место: {user_data.get('location', 'не указано')}\n"
             f"👤 Данные: {registration_details}\n"
             f"От: @{message.from_user.username or 'нет'}",
        parse_mode=ParseMode.HTML
    )

    await message.answer(
        f"✅ <b>Вы успешно записаны на Мафию 18+!</b>\n\n"
        f"📅 Дата: {user_data.get('date', 'не указана')}\n"
        f"📍 Место: {user_data.get('location', 'не указано')}\n"
        f"🏠 Адрес: {events['adult']['Мафия 18+']['address']}\n"
        f"💵 Стоимость: {events['adult']['Мафия 18+']['price']}\n\n"
        f"По всем вопросам: @alinarolina",
        parse_mode=ParseMode.HTML,
        reply_markup=get_chess_success_keyboard()
    )
    
    await state.clear()

@dp.message(Form.waiting_for_breakfast_registration)
async def process_breakfast_registration(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    
    # Проверяем и обрабатываем данные
    registration_details = await validate_and_process_registration(
        message, state, 
        required_fields=['name', 'phone']
    )
    
    if not registration_details:
        # Остаемся в том же состоянии, чтобы пользователь мог ввести данные снова
        return
    
    # Сохраняем запись
    registration_data = {
        "event": "Завтрак на английском",
        "details": registration_details,
        "date": user_data.get("date", ""),
        "location": user_data.get("location", ""),
        "timestamp": str(datetime.now())
    }
    await save_user_registration(message.from_user.id, registration_data)
    
    address = events["adult"]["Завтрак на английском"]["addresses"][user_data["location"]]
    
    await bot.send_message(
        chat_id=NOTIFY_CHAT_ID,
        text=f"☕ Новая запись на Завтрак на английском:\n"
             f"📅 Дата: {user_data.get('date', 'не указана')}\n"
             f"📍 Место: {user_data.get('location', 'не указано')}\n"
             f"👤 Данные: {registration_details}\n"
             f"От: @{message.from_user.username or 'нет'}",
        parse_mode=ParseMode.HTML
    )

    await message.answer(
        f"✅ <b>Вы успешно записаны на Завтрак на английском!</b>\n\n"
        f"📅 Дата: {user_data.get('date', 'не указана')}\n"
        f"📍 Место: {user_data.get('location', 'не указано')}\n"
        f"🏠 Адрес: {address}\n"
        f"💵 Стоимость: {events['adult']['Завтрак на английском']['price']}\n\n"
        f"Фильм для обсуждения: {events['adult']['Завтрак на английском']['film']}\n\n"
        f"По всем вопросам: @alinarolina",
        parse_mode=ParseMode.HTML,
        reply_markup=get_chess_success_keyboard()
    )
    
    await state.clear()

# Обработчики команд
@dp.message(Command("start"))
async def send_welcome(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Привет, это твой гид по культурным и развлекательным мероприятиям Рыбацкого!",
        reply_markup=get_start_keyboard()
    )

# Основные обработчики callback-запросов
@dp.callback_query(lambda c: c.data == "start")
async def process_start(callback: types.CallbackQuery, state: FSMContext):
    await safe_edit_message(
        "Что тебя интересует?",
        callback,
        reply_markup=get_event_type_keyboard(),
        state=state
    )
    await state.set_state(Form.waiting_for_event)


# Обработчики для взрослых/детских мероприятий
@dp.callback_query(lambda c: c.data in ["adult", "child"], Form.waiting_for_event)
async def process_event_type(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "adult":
        await safe_edit_message(
            "Какое мероприятие вас интересует?",
            callback,
            reply_markup=get_adult_events_keyboard(),
            state=state
        )
        await state.set_state(Form.waiting_for_event)
    else:
        await safe_edit_message(
            "Какое детское мероприятие вас интересует?",
            callback,
            reply_markup=get_child_events_keyboard(),
            state=state
        )
        await state.set_state(Form.waiting_for_event)

# Обработчики для завтрака на английском
@dp.callback_query(lambda c: c.data == "breakfast", Form.waiting_for_event)
async def process_breakfast(callback: types.CallbackQuery, state: FSMContext):
    description = events["adult"]["Завтрак на английском"]["description"]
    await safe_edit_message(
        description,
        callback,
        reply_markup=get_breakfast_options_keyboard(),
        state=state
    )
    await state.set_state(Form.waiting_for_breakfast_option)

@dp.callback_query(lambda c: c.data.startswith("breakfast_"), Form.waiting_for_breakfast_option)
async def process_breakfast_option(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data
    
    if data == "breakfast_when_where":
        await safe_edit_message(
            "Выберите, какое место вам было бы удобно:",
            callback,
            reply_markup=get_breakfast_locations_keyboard(),
            state=state
        )
        await state.set_state(Form.waiting_for_breakfast_date)
    
    elif data == "breakfast_why":
        await safe_edit_message(
            "Это уютная встреча за вкусным завтраком, где мы обсуждаем интересный фильм на английском языке. "
            "Отличная возможность попрактиковать язык и познакомиться с новыми людьми!",
            callback,
            reply_markup=get_breakfast_why_keyboard(),
            state=state
        )
        await state.set_state(Form.waiting_for_breakfast_question)
    
    elif data == "breakfast_register":
        await safe_edit_message(
            "Выберите, какое место вам было бы удобно:",
            callback,
            reply_markup=get_breakfast_locations_keyboard(),
            state=state
        )
        await state.set_state(Form.waiting_for_breakfast_date)
    
    elif data == "breakfast_price":
        price = events["adult"]["Завтрак на английском"]["price"]
        await safe_edit_message(
            f"Стоимость участия: {price}",
            callback,
            reply_markup=get_breakfast_back_keyboard(),
            state=state
        )
    
    elif data == "breakfast_back":
        description = events["adult"]["Завтрак на английском"]["description"]
        await safe_edit_message(
            description,
            callback,
            reply_markup=get_breakfast_options_keyboard(),
            state=state
        )
        await state.set_state(Form.waiting_for_breakfast_option)

# Обработчики для вопросов по завтраку
@dp.callback_query(lambda c: c.data.startswith("breakfast_"), Form.waiting_for_breakfast_question)
async def process_breakfast_question(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data
    
    if data == "breakfast_film":
        film = events["adult"]["Завтрак на английском"]["film"]
        await safe_edit_message(
            film,
            callback,
            reply_markup=get_breakfast_why_keyboard(),
            state=state
        )
    
    elif data == "breakfast_register":
        await safe_edit_message(
            "Выберите, какой день недели и время вам были бы удобны:",
            callback,
            reply_markup=get_breakfast_locations_keyboard(),
            state=state
        )
        await state.set_state(Form.waiting_for_breakfast_date)
    
    elif data == "breakfast_back":
        description = events["adult"]["Завтрак на английском"]["description"]
        await safe_edit_message(
            description,
            callback,
            reply_markup=get_breakfast_options_keyboard(),
            state=state
        )
        await state.set_state(Form.waiting_for_breakfast_option)

# Обработчики для выбора локации и даты завтрака
@dp.callback_query(lambda c: c.data.startswith("breakfast_loc_"), Form.waiting_for_breakfast_date)
async def process_breakfast_location(callback: types.CallbackQuery, state: FSMContext):
    location = callback.data.split("_")[2]
    await state.update_data(location=location)
    await safe_edit_message(
        "Выберите удобный день недели и время:",
        callback,
        reply_markup=get_breakfast_dates_keyboard(location),
        state=state
    )

@dp.callback_query(lambda c: c.data == "breakfast_back_to_locations", Form.waiting_for_breakfast_date)
async def breakfast_back_to_locations(callback: types.CallbackQuery, state: FSMContext):
    await safe_edit_message(
        "Выберите, какое место для вас было бы удобнее:",
        callback,
        reply_markup=get_breakfast_locations_keyboard(),
        state=state
    )

@dp.callback_query(lambda c: c.data == "breakfast_back", Form.waiting_for_breakfast_date)
async def breakfast_back_from_locations(callback: types.CallbackQuery, state: FSMContext):
    description = events["adult"]["Завтрак на английском"]["description"]
    await safe_edit_message(
        description,
        callback,
        reply_markup=get_breakfast_options_keyboard(),
        state=state
    )
    await state.set_state(Form.waiting_for_breakfast_option)

@dp.callback_query(lambda c: c.data.startswith("breakfast_date_"), Form.waiting_for_breakfast_date)
async def process_breakfast_date(callback: types.CallbackQuery, state: FSMContext):
    date = callback.data.split("_")[2]
    user_data = await state.get_data()
    location = user_data["location"]
    address = events["adult"]["Завтрак на английском"]["addresses"][location]
    
    await state.update_data(date=date, event="Завтрак на английском")
    await state.set_state(Form.waiting_for_breakfast_registration)
    
    await callback.message.answer(
        f"Вы выбрали:\n"
        f"📅 Дата: {date}\n"
        f"📍 Место: {location}\n"
        f"🏠 Адрес: {address}\n\n"
        "Для завершения регистрации отправьте одним сообщением:\n"
        "Фамилию, Имя и номер телефона\n\n"
        "<b>Пример:</b> <i>Иванов Иван 89123456789</i>",
        parse_mode=ParseMode.HTML,
        reply_markup=get_mafia_registration_keyboard()
    )
    await callback.answer()

@dp.message(Form.waiting_for_breakfast_registration)
async def process_breakfast_registration(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    
    # Проверяем и обрабатываем данные
    registration_details = await validate_and_process_registration(
        message, state, 
        required_fields=['name', 'phone']
    )
    
    if not registration_details:
        return  # Ошибка уже обработана
    
    # Сохраняем запись
    registration_data = {
        "event": "Завтрак на английском",
        "details": registration_details,
        "date": user_data.get("date", ""),
        "location": user_data.get("location", ""),
        "timestamp": str(datetime.now())
    }
    await save_user_registration(message.from_user.id, registration_data)
    
    address = events["adult"]["Завтрак на английском"]["addresses"][user_data["location"]]
    
    await bot.send_message(
        chat_id=NOTIFY_CHAT_ID,
        text=f"☕ Новая запись на Завтрак на английском:\n"
             f"📅 Дата: {user_data.get('date', 'не указана')}\n"
             f"📍 Место: {user_data.get('location', 'не указано')}\n"
             f"👤 Данные: {registration_details}\n"
             f"От: @{message.from_user.username or 'нет'}",
        parse_mode=ParseMode.HTML
    )

    await message.answer(
        f"✅ <b>Вы успешно записаны на Завтрак на английском!</b>\n\n"
        f"📅 Дата: {user_data.get('date', 'не указана')}\n"
        f"📍 Место: {user_data.get('location', 'не указано')}\n"
        f"🏠 Адрес: {address}\n"
        f"💵 Стоимость: {events['adult']['Завтрак на английском']['price']}\n\n"
        f"Фильм для обсуждения: {events['adult']['Завтрак на английском']['film']}\n\n"
        f"По всем вопросам: @alinarolina",
        parse_mode=ParseMode.HTML,
        reply_markup=get_chess_success_keyboard()
    )
    
    await state.clear()


# Обработчики для мафии
@dp.callback_query(lambda c: c.data == "mafia", Form.waiting_for_event)
async def process_mafia(callback: types.CallbackQuery, state: FSMContext):
    description = events["adult"]["Мафия 18+"]["description"]
    await safe_edit_message(
        description,
        callback,
        reply_markup=get_mafia_options_keyboard(),
        state=state
    )
    await state.set_state(Form.waiting_for_mafia_option)

@dp.callback_query(lambda c: c.data.startswith("mafia_"), Form.waiting_for_mafia_option)
async def process_mafia_option(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data
    
    if data == "mafia_when_where":
        await safe_edit_message(
            "Выберите место проведения:",
            callback,
            reply_markup=get_mafia_locations_keyboard(),
            state=state
        )
        await state.set_state(Form.waiting_for_mafia_locations_keyboard)
    
    elif data == "mafia_newbie":
        newbie_info = events["adult"]["Мафия 18+"]["newbie_info"]
        await safe_edit_message(
            newbie_info,
            callback,
            reply_markup=get_mafia_newbie_keyboard(),
            state=state
        )
        await state.set_state(Form.waiting_for_mafia_questions)
    
    elif data == "mafia_register":
        await safe_edit_message(
            "Выберите место проведения:",
            callback,
            reply_markup=get_mafia_locations_keyboard(),
            state=state
        )
        await state.set_state(Form.waiting_for_mafia_locations_keyboard)
    
    elif data == "mafia_back":
        description = events["adult"]["Мафия 18+"]["description"]
        await safe_edit_message(
            description,
            callback,
            reply_markup=get_mafia_options_keyboard(),
            state=state
        )
        await state.set_state(Form.waiting_for_mafia_option)

# Обработчики для вопросов по мафии
@dp.callback_query(lambda c: c.data.startswith("mafia_"), Form.waiting_for_mafia_questions)
async def process_mafia_questions(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data
    
    if data == "mafia_when_where":
        await safe_edit_message(
            "Выберите место проведения:",
            callback,
            reply_markup=get_mafia_locations_keyboard(),
            state=state
        )
        await state.set_state(Form.waiting_for_mafia_locations_keyboard)
    
    elif data == "mafia_questions":
        await callback.message.answer(
            "Вы можете задать любые вопросы администратору @alinarolina\n\n"
            "Также вы можете вернуться к выбору даты для игры:",
            reply_markup=get_mafia_locations_keyboard()
        )
        await state.set_state(Form.waiting_for_mafia_locations_keyboard)
        await callback.answer()

    elif data == "mafia_back":
        description = events["adult"]["Мафия 18+"]["description"]
        await safe_edit_message(
            description,
            callback,
            reply_markup=get_mafia_options_keyboard(),
            state=state
        )
        await state.set_state(Form.waiting_for_mafia_option)

# Обработчики для выбора локации и даты мафии
@dp.callback_query(lambda c: c.data.startswith("mafia_loc_"), Form.waiting_for_mafia_locations_keyboard)
async def process_mafia_location(callback: types.CallbackQuery, state: FSMContext):
    location = callback.data.split("_")[2]
    await state.update_data(location=location)
    await safe_edit_message(
        "Выберите удобную дату:",
        callback,
        reply_markup=get_mafia_dates_keyboard(location),
        state=state
    )
    await state.set_state(Form.waiting_for_mafia_date)

@dp.callback_query(lambda c: c.data == "mafia_back_to_locations", Form.waiting_for_mafia_date)
async def mafia_back_to_locations_handler(callback: types.CallbackQuery, state: FSMContext):
    await safe_edit_message(
        "Выберите место проведения:",
        callback,
        reply_markup=get_mafia_locations_keyboard(),
        state=state
    )
    await state.set_state(Form.waiting_for_mafia_locations_keyboard)

@dp.callback_query(lambda c: c.data == "mafia_back", Form.waiting_for_mafia_locations_keyboard)
async def mafia_back_to_main_options(callback: types.CallbackQuery, state: FSMContext):
    description = events["adult"]["Мафия 18+"]["description"]
    await safe_edit_message(
        description,
        callback,
        reply_markup=get_mafia_options_keyboard(),
        state=state
    )
    await state.set_state(Form.waiting_for_mafia_option)
    

@dp.callback_query(lambda c: c.data.startswith("mafia_date_"), Form.waiting_for_mafia_date)
async def process_mafia_date(callback: types.CallbackQuery, state: FSMContext):
    try:
        date = callback.data.split("_")[2]
        user_data = await state.get_data()
        location = user_data.get("location", "Лофт")  # По умолчанию Лофт
        address = events["adult"]["Мафия 18+"]["address"]
        price = events["adult"]["Мафия 18+"]["price"]
        
        await state.update_data(
            date=date,
            event="Мафия 18+",
            location=location
        )
        await state.set_state(Form.waiting_for_mafia_registration)
        
        # Создаем клавиатуру с кнопкой "Назад"
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="mafia_back_to_dates")
        )
        
        await callback.message.answer(
            "🎭 <b>Запись на Мафию 18+</b>\n\n"
            "Для завершения регистрации отправьте:\n"
            "Ваше имя, контактный телефон, количество человек\n\n"
            "<b>Пример:</b>\n<i>Иван 79123456789 2</i>",
            parse_mode=ParseMode.HTML,
            reply_markup=builder.as_markup()
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in process_mafia_date: {e}")
        await callback.answer("Произошла ошибка, попробуйте позже")

@dp.callback_query(lambda c: c.data == "mafia_back_to_dates", Form.waiting_for_mafia_registration)
async def mafia_back_to_dates_handler(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    location = user_data.get("location", "Лофт")
    await safe_edit_message(
        "Выберите удобную дату:",
        callback,
        reply_markup=get_mafia_dates_keyboard(location),
        state=state
    )
    await state.set_state(Form.waiting_for_mafia_date)

@dp.message(Form.waiting_for_mafia_registration)
async def process_mafia_registration(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    text = message.text.strip()
    
    # Парсим введенные данные
    parts = text.split()
    if len(parts) < 3:
        await message.answer(
            "❌ Недостаточно данных. Пожалуйста, введите:\n"
            "Имя, телефон и количество человек\n\n"
            "<b>Пример:</b> <i>Иван 79123456789 2</i>",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Извлекаем количество людей (последний элемент)
    count_str = parts[-1]
    if not count_str.isdigit():
        await message.answer(
            "❌ Количество человек должно быть числом. Пожалуйста, введите:\n"
            "Имя, телефон и количество человек\n\n"
            "<b>Пример:</b> <i>Иван 79123456789 2</i>",
            parse_mode=ParseMode.HTML
        )
        return
    
    count = int(count_str)
    name = ' '.join(parts[:-2])
    phone = parts[-2]
    
    # Проверяем телефон
    phone_clean = re.sub(r'[^\d]', '', phone)
    if len(phone_clean) not in (10, 11) or not phone_clean.isdigit():
        await message.answer(
            "❌ Некорректный номер телефона. Пожалуйста, введите:\n"
            "Имя, телефон и количество человек\n\n"
            "<b>Пример:</b> <i>Иван 79123456789 2</i>",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Форматируем данные для записи
    registration_details = f"{name} {phone} {count}"
    
    # Сохраняем запись
    registration_data = {
        "event": "Мафия 18+",
        "details": registration_details,
        "date": user_data.get("date", ""),
        "location": user_data.get("location", ""),
        "timestamp": str(datetime.now())
    }
    await save_user_registration(message.from_user.id, registration_data)
    
    await bot.send_message(
        chat_id=NOTIFY_CHAT_ID,
        text=f"🎭 Новая запись на Мафию 18+:\n"
             f"📅 Дата: {user_data.get('date', 'не указана')}\n"
             f"📍 Место: {user_data.get('location', 'не указано')}\n"
             f"👤 Данные: {registration_details}\n"
             f"От: @{message.from_user.username or 'нет'}",
        parse_mode=ParseMode.HTML
    )

    await message.answer(
        f"✅ <b>Вы успешно записаны на Мафию 18+!</b>\n\n"
        f"📅 Дата: {user_data.get('date', 'не указана')}\n"
        f"📍 Место: {user_data.get('location', 'не указано')}\n"
        f"🏠 Адрес: {events['adult']['Мафия 18+']['address']}\n"
        f"💵 Стоимость: {events['adult']['Мафия 18+']['price']}\n\n"
        f"По всем вопросам: @alinarolina",
        parse_mode=ParseMode.HTML,
        reply_markup=get_chess_success_keyboard()
    )
    
    await state.clear()

        # Обработчики для лекций
@dp.callback_query(lambda c: c.data == "lectures", Form.waiting_for_event)
async def process_lectures(callback: types.CallbackQuery, state: FSMContext):
    description = events["adult"]["Лекции"]["description"]
    address = events["adult"]["Лекции"]["address"]
    await safe_edit_message(
        f"{description}\n\n"
        f"Всё проходит в уютном Лофте по адресу {address}.\n"
        "Готовы узнать подробности?",
        callback,
        reply_markup=get_lectures_intro_keyboard(),
        state=state
    )
    await state.set_state(Form.waiting_for_lecture_option)

@dp.callback_query(lambda c: c.data == "lectures_more", Form.waiting_for_lecture_option)
async def process_lectures_more(callback: types.CallbackQuery, state: FSMContext):
    lectures = events["adult"]["Лекции"]["lectures"]
    lectures_text = "В этом месяце вас ждут три вдохновляющие лекции:\n\n"
    
    for i, (key, lecture) in enumerate(lectures.items(), 1):
        lectures_text += f"{i}️⃣ {lecture['title']}\n{lecture['description']}\n\n"
    
    await safe_edit_message(
        lectures_text,
        callback,
        reply_markup=get_lectures_topics_keyboard(),
        state=state
    )

@dp.callback_query(lambda c: c.data == "lectures_when_where", Form.waiting_for_lecture_option)
async def process_lectures_when_where(callback: types.CallbackQuery, state: FSMContext):
    address = events["adult"]["Лекции"]["address"]
    await safe_edit_message(
        f"Все лекции проходят в уютном Лофте по адресу {address} — теперь не нужно тратить время на дорогу в центр!\n\n"
        "Вы сможете пообщаться с единомышленниками из своего района, задать вопросы экспертам и получить новые знания в комфортной атмосфере.",
        callback,
        reply_markup=get_lectures_when_where_keyboard(),
        state=state
    )

@dp.callback_query(lambda c: c.data == "lectures_topics", Form.waiting_for_lecture_option)
async def process_lectures_topics(callback: types.CallbackQuery, state: FSMContext):
    await safe_edit_message(
        "Выберите интересующую вас лекцию, и я пришлю подробное описание или помогу сразу записаться!",
        callback,
        reply_markup=get_lectures_list_keyboard(),
        state=state
    )

@dp.callback_query(lambda c: c.data.startswith("lecture_"), Form.waiting_for_lecture_option)
async def process_lecture_detail(callback: types.CallbackQuery, state: FSMContext):
    try:
        parts = callback.data.split('_')
        
        if len(parts) < 2:
            await callback.answer("Неверный формат данных")
            return

        lecture_key = parts[-1]
        
        if lecture_key not in events["adult"]["Лекции"]["lectures"]:
            await callback.answer("Лекция не найдена")
            return

        lecture = events["adult"]["Лекции"]["lectures"][lecture_key]

        if "register" in callback.data:
            await state.update_data(
                event=f"Лекция: {lecture['title']}",
                lecture_key=lecture_key
            )
            await state.set_state(Form.waiting_for_lecture_registration)
            
            await callback.message.answer(
                "✏️ <b>Запись на лекцию</b>\n\n"
                "Чтобы забронировать место, отправьте:\n"
                "Ваше имя и фамилию, контактный телефон, количество человек\n"
                "*сумма указана за одного человека\n\n"
                "<b>Например:</b>\n<i>Александр 79123456789 1</i>",
                parse_mode=ParseMode.HTML
                    )


            await callback.answer()
        else:
            await safe_edit_message(
                f"📚 <b>{lecture['title']}</b>\n\n"
                f"{lecture['description']}\n\n"
                f"📅 <b>Дата:</b> {lecture['date']}\n"
                f"⏰ <b>Время:</b> {lecture.get('time', 'уточняется')}\n"
                f"🏠 <b>Адрес:</b> {events['adult']['Лекции']['address']}\n"
                f"💵 <b>Стоимость:</b> {events['adult']['Лекции']['price']}",
                callback,
                reply_markup=get_lecture_detail_keyboard(lecture_key),
                state=state
            )
    except Exception as e:
        logger.error(f"Error in process_lecture_detail: {e}")
        await callback.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

@dp.message(Form.waiting_for_lecture_registration)
async def process_lecture_registration(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    
    # Проверяем и обрабатываем данные
    registration_details = await validate_and_process_registration(
        message, state,
        required_fields=['name', 'phone']
    )
    
    if not registration_details:
        return

    lecture_key = user_data.get("lecture_key")
    if not lecture_key:
        await message.answer("❌ Ошибка: лекция не найдена")
        await state.clear()
        return

    lecture = events["adult"]["Лекции"]["lectures"][lecture_key]

    # Сохраняем запись
    registration_data = {
        "event": f"Лекция: {lecture['title']}",
        "details": registration_details,
        "date": lecture['date'],
        "timestamp": str(datetime.now())
    }
    await save_user_registration(message.from_user.id, registration_data)

    await bot.send_message(
        chat_id=NOTIFY_CHAT_ID,
        text=f"📚 Новая запись на лекцию:\n"
             f"Тема: {lecture['title']}\n"
             f"Дата: {lecture['date']}\n"
             f"Данные: {registration_details}\n"
             f"Пользователь: @{message.from_user.username or 'не указан'}",
        parse_mode=ParseMode.HTML
    )

    await message.answer(
        f"✅ <b>Вы успешно записаны на лекцию!</b>\n\n"
        f"📚 <b>Тема:</b> {lecture['title']}\n"
        f"📅 <b>Дата:</b> {lecture['date']}\n"
        f"🏠 <b>Адрес:</b> {events['adult']['Лекции']['address']}\n"
        f"💵 <b>Стоимость:</b> {events['adult']['Лекции']['price']}\n\n"
        f"По всем вопросам: @alinarolina",
        parse_mode=ParseMode.HTML,
        reply_markup=get_chess_success_keyboard()
    )
    
    await state.clear()

# Обработчик для подготовки к школе
@dp.callback_query(lambda c: c.data == "child_Подготовка_к_школе")
async def process_school_prep(callback: types.CallbackQuery, state: FSMContext):
    await safe_edit_message(
        "В нашем центре проводится летняя подготовка к школе. Готов узнать подробности?",
        callback,
        reply_markup=get_school_prep_keyboard(),
        state=state
    )
    await state.set_state(Form.waiting_for_school_prep_option)

@dp.callback_query(lambda c: c.data == "school_prep_yes", Form.waiting_for_school_prep_option)
async def process_school_prep_yes(callback: types.CallbackQuery, state: FSMContext):
    prep_data = events["child"]["Подготовка к школе"]
    await safe_edit_message(
        f"{prep_data['details']}\n"
        f"{prep_data['price']}",
        callback,
        reply_markup=get_school_prep_details_keyboard(),
        state=state
    )

@dp.callback_query(lambda c: c.data == "school_prep_register", Form.waiting_for_school_prep_option)
async def process_school_prep_register(callback: types.CallbackQuery, state: FSMContext):
    await safe_edit_message(
        "Выберите удобное время:",
        callback,
        reply_markup=get_school_prep_schedule_keyboard(),
        state=state
    )

@dp.callback_query(lambda c: c.data in ["school_prep_wed", "school_prep_sat"], Form.waiting_for_school_prep_option)
async def process_school_prep_time(callback: types.CallbackQuery, state: FSMContext):
    time = "Среда 17:00" if callback.data == "school_prep_wed" else "Суббота 18:00"
    await state.update_data(event="Подготовка к школе", time=time)
    await callback.message.answer(
        "Для записи на подготовку к школе отправьте:\n"
        "1. Имя и возраст ребенка\n"
        "2. Ваш номер телефона\n\n"
        "<b>Пример:</b> <i>Алексей 6 лет 89123456789</i>",
        parse_mode=ParseMode.HTML
    )
    await state.set_state(Form.waiting_for_school_prep_registration)

@dp.message(Form.waiting_for_school_prep_registration)
async def process_school_prep_data(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    
    # Проверяем и обрабатываем данные
    registration_details = await validate_and_process_registration(
        message, state,
        required_fields=['name', 'phone', 'age']
    )
    
    if not registration_details:
        return

    # Сохраняем запись
    registration_data = {
        "event": "Подготовка к школе",
        "details": registration_details,
        "time": user_data.get("time", ""),
        "timestamp": str(datetime.now())
    }
    await save_user_registration(message.from_user.id, registration_data)

    await bot.send_message(
        chat_id=NOTIFY_CHAT_ID,
        text=f"📚 Новая запись на подготовку к школе:\n"
             f"⏰ Время: {user_data.get('time', 'не указано')}\n"
             f"👶 Данные: {registration_details}\n"
             f"👤 От: @{message.from_user.username or 'нет'}",
        parse_mode=ParseMode.HTML
    )

    prep_data = events["child"]["Подготовка к школе"]
    await message.answer(
        f"✅ <b>Вы успешно записаны на подготовку к школе!</b>\n\n"
        f"⏰ Время: {user_data.get('time', 'не указано')}\n"
        f"🏠 Адрес: {prep_data['address']}\n"
        f"💵 Стоимость: {prep_data['price']}\n\n"
        f"По всем вопросам: @alinarolina",
        parse_mode=ParseMode.HTML,
        reply_markup=get_school_prep_success_keyboard()
    )
    
    await state.clear()
# Обработчики для детских мероприятий
@dp.callback_query(lambda c: c.data.startswith("child_"))
async def process_child_event(callback: types.CallbackQuery, state: FSMContext):
    event_name = callback.data.replace("child_", "").replace("_", " ")
    
    if event_name == "Детский день рождения":
        await state.set_state(Form.waiting_for_birthday_option)
        await safe_edit_message(
            f"{events['child']['Детский день рождения']['details']}\n\n"
            f"{events['child']['Детский день рождения']['additional_info']}",
            callback,
            reply_markup=get_birthday_keyboard(),
            state=state
        )
    elif event_name == "Мастер-класс в Чаче":
        await state.set_state(Form.waiting_for_masterclass_option)
        await safe_edit_message(
            f"{events['child']['Мастер-класс в Чаче']['description']}\n"
            f"{events['child']['Мастер-класс в Чаче']['details']}\n"
            "Готовы узнать подробности?",
            callback,
            reply_markup=get_chess_keyboard(),
            state=state
        )
    elif event_name == "Шахматы":
        await state.set_state(Form.waiting_for_chess_option)
        await safe_edit_message(
            f"{events['child']['Шахматы']['description']}\n"
            f"{events['child']['Шахматы']['details']}\n"
            "Готовы узнать подробности?",
            callback,
            reply_markup=get_chess_keyboard(),
            state=state
        )
    elif event_name == "Рисование":
        await state.set_state(Form.waiting_for_drawing_option)
        await safe_edit_message(
            f"{events['child']['Рисование']['description']}\n"
            f"{events['child']['Рисование']['details']}\n"
            f"Встречаемся в уютном центре CoolKids по адресу {events['child']['Рисование']['address']} — всё лето!\n"
            "Готовы узнать подробности?",
            callback,
            reply_markup=get_drawing_keyboard(),
            state=state
        )
    elif event_name == "Городской лагерь":
        await state.set_state(Form.waiting_for_camp_option)
        await safe_edit_message(
            f"{events['child']['Городской лагерь']['description']}\n"
            f"{events['child']['Городской лагерь']['details']}\n"
            "Хотите узнать подробности?",
            callback,
            reply_markup=get_camp_intro_keyboard(),
            state=state
        )
    elif event_name == "Курсы английского языка":
        await state.set_state(Form.waiting_for_english_option)
        description = events["child"]["Курсы английского языка"]["description"]
        details = events["child"]["Курсы английского языка"]["details"]
        await safe_edit_message(
            f"{description}\n{details}\nГотовы узнать расписание и выбрать подходящую группу?",
            callback,
            reply_markup=get_english_keyboard(),
            state=state
        )
    else:
        await safe_edit_message(
            "Какое детское мероприятие вас интересует?",
            callback,
            reply_markup=get_child_events_keyboard(),
            state=state
        )

# Обработчики для мастер-классов
@dp.callback_query(lambda c: c.data == "chess_more", Form.waiting_for_masterclass_option)
async def process_masterclass_more(callback: types.CallbackQuery, state: FSMContext):
    await safe_edit_message(
        "На наших мастер-классах дети сами готовят пиццу, сочные гамбургеры или яркие кей-попсы под руководством опытного шефа!\n"
        "Это не только вкусно, но и очень весело: игры, конкурсы, фото и, конечно, дегустация собственных шедевров!\n\n"
        "Интересно, какой мастер-класс понравится вашему ребёнку больше всего?",
        callback,
        reply_markup=get_masterclass_types_keyboard(),
        state=state
    )
    await state.set_state(Form.waiting_for_masterclass_type)

@dp.callback_query(lambda c: c.data.startswith("masterclass_"), Form.waiting_for_masterclass_type)
async def process_masterclass_type(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data
    
    if data == "masterclass_pizza":
        await safe_edit_message(
            events["child"]["Мастер-класс в Чаче"]["options"]["Пицца"],
            callback,
            reply_markup=get_masterclass_types_keyboard(),
            state=state
        )
    
    elif data == "masterclass_burgers":
        await safe_edit_message(
            events["child"]["Мастер-класс в Чаче"]["options"]["Гамбургеры"],
            callback,
            reply_markup=get_masterclass_types_keyboard(),
            state=state
        )
    
    elif data == "masterclass_cakepops":
        await safe_edit_message(
            events["child"]["Мастер-класс в Чаче"]["options"]["Кей-попсы"],
            callback,
            reply_markup=get_masterclass_types_keyboard(),
            state=state
        )
    
    elif data == "masterclass_all":
        await safe_edit_message(
            "Мы предлагаем разнообразные мастер-классы для детей разного возраста!\n\n"
            "• Пицца - дети учатся готовить настоящую пиццу с разными начинками\n"
            "• Гамбургеры - мастер-класс по приготовлению сочных бургеров\n"
            "• Кей-попсы - яркие и вкусные кей-попсы - любимое лакомство детей\n\n"
            "Все мастер-классы проходят в уютной атмосфере ресторана «Чача»!",
            callback,
            reply_markup=get_masterclass_types_keyboard(),
            state=state
        )
    
    elif data == "masterclass_info":
        await safe_edit_message(
            events["child"]["Мастер-класс в Чаче"]["info"],
            callback,
            reply_markup=get_masterclass_info_keyboard(),
            state=state
        )
        await state.set_state(Form.waiting_for_masterclass_info)
    
    elif data == "masterclass_back":
        await safe_edit_message(
            "Какое детское мероприятие вас интересует?",
            callback,
            reply_markup=get_child_events_keyboard(),
            state=state
        )
        await state.set_state(Form.waiting_for_event)

@dp.callback_query(lambda c: c.data.startswith("masterclass_"), Form.waiting_for_masterclass_info)
async def process_masterclass_info(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data
    
    if data == "masterclass_schedule":
        schedule = events["child"]["Мастер-класс в Чаче"]["schedule"]
        price = events["child"]["Мастер-класс в Чаче"]["price"]
        address = events["child"]["Мастер-класс в Чаче"]["address"]
        
        schedule_text = "Ближайшие мастер-классы:\n"
        for mc_type, date in schedule.items():
            schedule_text += f"• {mc_type} — {date}\n"
        
        await safe_edit_message(
            f"{schedule_text}\n"
            f"Место: ресторан «Чача» ({address})\n"
            f"Стоимость: {price} за ребёнка.\n\n"
            "Количество мест ограничено!",
            callback,
            reply_markup=get_masterclass_schedule_keyboard(),
            state=state
        )
        await state.set_state(Form.waiting_for_masterclass_schedule)
    
    elif data == "masterclass_register":
        await state.set_state(Form.waiting_for_masterclass_registration)
        await callback.message.answer(
            "Для бронирования места, пожалуйста, напишите:\n"
            "• Имя и возраст ребёнка\n"
            "• Ваш номер телефона\n"
            "• Предпочтительный мастер-класс (пицца, гамбургеры или кей-попсы)\n\n"
            "<b>Пример:</b> <i>Алексей 10 лет 89123456789 пицца</i>",
            parse_mode=ParseMode.HTML
        )
        await callback.answer()
    
    elif data == "child_back":
        await safe_edit_message(
            "Какое детское мероприятие вас интересует?",
            callback,
            reply_markup=get_child_events_keyboard(),
            state=state
        )
        await state.set_state(Form.waiting_for_event)

@dp.callback_query(lambda c: c.data.startswith("masterclass_"), Form.waiting_for_masterclass_schedule)
async def process_masterclass_schedule(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data
    
    if data == "masterclass_register":
        await state.set_state(Form.waiting_for_masterclass_registration)
        await callback.message.answer(
            "Для бронирования места, пожалуйста, напишите:\n"
            "• Имя и возраст ребёнка\n"
            "• Ваш номер телефона\n"
            "• Предпочтительный мастер-класс (пицца, гамбургеры или кей-попсы)\n\n"
            "<b>Пример:</b> <i>Алексей 10 лет 89123456789 пицца</i>",
            parse_mode=ParseMode.HTML
        )
        await callback.answer()
    
    elif data == "child_back":
        await safe_edit_message(
            "Какое детское мероприятие вас интересует?",
            callback,
            reply_markup=get_child_events_keyboard(),
            state=state
        )
        await state.set_state(Form.waiting_for_event)

@dp.message(Form.waiting_for_masterclass_registration)
async def process_masterclass_registration(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    
    # Проверяем и обрабатываем данные
    registration_details = await validate_and_process_registration(
        message, state,
        required_fields=['name', 'phone', 'age']
    )
    
    if not registration_details:
        return
    
    # Определяем тип мастер-класса
    mc_types = ["пицца", "гамбургеры", "кей-попсы"]
    mc_type = None
    for t in mc_types:
        if t in message.text.lower():
            mc_type = t
            break
    
    if not mc_type:
        await message.answer("❌ Не указан тип мастер-класса. Пожалуйста, укажите: пицца, гамбургеры или кей-попсы")
        return
    
    registration_details += f" {mc_type}"

    # Сохраняем запись
    registration_data = {
        "event": f"Мастер-класс: {mc_type.capitalize()}",
        "details": registration_details,
        "timestamp": str(datetime.now())
    }
    await save_user_registration(message.from_user.id, registration_data)

    await bot.send_message(
        chat_id=NOTIFY_CHAT_ID,
        text=f"👨‍🍳 Новая запись на мастер-класс ({mc_type.capitalize()}):\n"
             f"👶 Ребенок: {registration_details}\n"
             f"👤 От: @{message.from_user.username or 'нет'}",
        parse_mode=ParseMode.HTML
    )

    mc_data = events["child"]["Мастер-класс в Чаче"]
    await message.answer(
        f"✅ <b>Запись оформлена!</b>\n\n"
        f"👨‍🍳 Мастер-класс: {mc_type.capitalize()}\n"
        f"🏠 Адрес: {mc_data['address']}\n"
        f"💵 Стоимость: {mc_data['price']}\n\n"
        f"По всем вопросам: @alinarolina",
        parse_mode=ParseMode.HTML,
        reply_markup=get_chess_success_keyboard()
    )
    
    await state.clear()


# Обработчики для шахмат
@dp.callback_query(lambda c: c.data == "chess_more", Form.waiting_for_chess_option)
async def process_chess_more(callback: types.CallbackQuery, state: FSMContext):
    await safe_edit_message(
        "Шахматы — это не только весело, но и полезно!\n"
        "Ребята учатся стратегически мыслить, принимать решения и находить новых друзей.\n"
        "Наши встречи проходят в уютном центре CoolKids по адресу Рыбацкий пр-т 23/2.\n"
        "Присоединяйтесь к нам этим летом!",
        callback,
        reply_markup=get_chess_options_keyboard(),
        state=state
    )

@dp.callback_query(lambda c: c.data == "chess_back_to_main", Form.waiting_for_chess_option)
async def chess_back_to_main(callback: types.CallbackQuery, state: FSMContext):
    description = events["child"]["Шахматы"]["description"]
    details = events["child"]["Шахматы"]["details"]
    await safe_edit_message(
        f"{description}\n{details}\nГотовы узнать подробности?",
        callback,
        reply_markup=get_chess_keyboard(),
        state=state
    )
    await state.set_state(Form.waiting_for_chess_option)

@dp.callback_query(lambda c: c.data == "chess_back_to_options", Form.waiting_for_chess_option)
async def chess_back_to_options(callback: types.CallbackQuery, state: FSMContext):
    await process_chess_more(callback, state)

@dp.callback_query(lambda c: c.data == "chess_schedule", Form.waiting_for_chess_option)
async def process_chess_schedule(callback: types.CallbackQuery, state: FSMContext):
    schedule = events["child"]["Шахматы"]["schedule"]
    await safe_edit_message(
        f"Расписание занятий:\n{schedule}",
        callback,
        reply_markup=get_chess_schedule_keyboard(),
        state=state
    )

@dp.callback_query(lambda c: c.data == "chess_price", Form.waiting_for_chess_option)
async def process_chess_price(callback: types.CallbackQuery, state: FSMContext):
    price = events["child"]["Шахматы"]["price"]
    await safe_edit_message(
        f"Стоимость участия — {price}.\n"
        "Всё включено: доски, фигуры, дружелюбная атмосфера и поддержка тренера!",
        callback,
        reply_markup=get_chess_price_keyboard(),
        state=state
    )

@dp.callback_query(lambda c: c.data == "chess_register", Form.waiting_for_chess_option)
async def chess_register_handler(callback: types.CallbackQuery, state: FSMContext):
    try:
        await state.set_state(Form.waiting_for_chess_data)
        await callback.message.answer(
            "♟️ Для записи на шахматы отправьте одним сообщением и в одну строчку: \n"
            "• Имя и возраст ребенка, ваш номер телефона, удобное время (17:00 или 18:00)\n"
            "<b>Пример:</b> <i>Алексей 10 лет 89123456789 17:00</i>",
            parse_mode=ParseMode.HTML
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in chess_register_handler: {e}")
        await callback.answer("Ошибка, попробуйте позже", show_alert=True)

@dp.message(Form.waiting_for_chess_data)
async def process_chess_data(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    
    # Проверяем и обрабатываем данные
    registration_details = await validate_and_process_registration(
        message, state,
        required_fields=['name', 'phone', 'age']
    )
    
    if not registration_details:
        # Остаемся в том же состоянии
        return
    
    # Дополнительная проверка времени
    time_match = re.search(r'(17|18)(?::00)?', message.text)
    if not time_match:
        await message.answer("❌ Не указано время. Пожалуйста, укажите 17:00 или 18:00")
        return
    
    time = time_match.group().replace(':00', '')
    registration_details += f" {time}:00"

    # Сохраняем запись
    registration_data = {
        "event": "Шахматы",
        "details": registration_details,
        "timestamp": str(datetime.now())
    }
    await save_user_registration(message.from_user.id, registration_data)

    await bot.send_message(
        chat_id=NOTIFY_CHAT_ID,
        text=f"♟️ Новая запись на Шахматы:\n"
             f"👶 Ребенок: {registration_details}\n"
             f"👤 От: @{message.from_user.username or 'нет'}",
        parse_mode=ParseMode.HTML
    )

    chess_data = events["child"]["Шахматы"]
    await message.answer(
        f"✅ <b>Запись оформлена!</b>\n\n"
        f"♟️ Шахматы в {time}:00\n"
        f"🏠 Адрес: {chess_data['address']}\n"
        f"💵 Стоимость: {chess_data['price']}\n\n"
        f"По всем вопросам: @alinarolina",
        parse_mode=ParseMode.HTML,
        reply_markup=get_chess_success_keyboard()
    )
    
    await state.clear()

@dp.callback_query(lambda c: c.data == "child_Городской_лагерь")
async def process_camp(callback: types.CallbackQuery, state: FSMContext):
    description = events["child"]["Городской лагерь"]["description"]
    details = events["child"]["Городской лагерь"]["details"]
    await safe_edit_message(
        f"{description}\n{details}\nХотите узнать подробности?",
        callback,
        reply_markup=get_camp_intro_keyboard(),
        state=state
    )
    await state.set_state(Form.waiting_for_camp_option)

@dp.callback_query(lambda c: c.data == "camp_more", Form.waiting_for_camp_option)
async def process_camp_more(callback: types.CallbackQuery, state: FSMContext):
    camps = events["child"]["Городской лагерь"]["camps"]
    camps_text = "В этом году мы подготовили 6 тематических смен — каждый ребёнок найдёт себе занятие по душе!\n\n"
    
    for camp_name, camp_data in camps.items():
        camps_text += f"• {camp_name} — {camp_data['dates']}\n"
    
    await safe_edit_message(
        camps_text,
        callback,
        reply_markup=get_camp_options_keyboard(),
        state=state
    )

@dp.callback_query(lambda c: c.data.startswith("camp_") and not c.data in ["camp_more", "camp_details", "camp_register", "camp_back_to_description"], Form.waiting_for_camp_option)
async def process_camp_selection(callback: types.CallbackQuery, state: FSMContext):
    camp_name = callback.data.replace("camp_", "").replace("_", " ")
    camp_data = events["child"]["Городской лагерь"]["camps"].get(camp_name)
    
    if camp_data:
        await state.update_data(camp_name=camp_name)
        await safe_edit_message(
            f"🏕️ <b>{camp_name} ({camp_data['dates']})</b>\n\n"
            f"{camp_data['description']}\n\n"
            f"💵 Стоимость смены: {events['child']['Городской лагерь']['price']}\n"
            f"🏠 Адрес: {events['child']['Городской лагерь']['address']}",
            callback,
            reply_markup=get_camp_selection_keyboard(),
            state=state
        )

@dp.callback_query(lambda c: c.data == "camp_details", Form.waiting_for_camp_option)
async def process_camp_details(callback: types.CallbackQuery, state: FSMContext):
    info = events["child"]["Городской лагерь"]["info"]
    await safe_edit_message(
        f"<b>Подробнее о сменах:</b>\n\n"
        f"Каждая смена включает:\n"
        f"• Пребывание в центре с 10:00 до 17:00\n"
        f"• Комплексный обед и полезный перекус\n"
        f"• Прогулки на свежем воздухе\n"
        f"• Занятия английским\n"
        f"• Активные игры\n"
        f"• Экскурсию по теме смены\n\n"
        f"{info}",
        callback,
        reply_markup=get_camp_options_keyboard(),
        state=state
    )

@dp.callback_query(lambda c: c.data == "camp_register", Form.waiting_for_camp_option)
async def camp_register_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.waiting_for_camp_registration)
    await callback.message.answer(
        "🏕️ <b>Запись в городской лагерь</b>\n\n"
        "Для бронирования места, пожалуйста, напишите:\n"
        "• Имя и возраст ребёнка\n"
        "• Ваш номер телефона\n"
        "• Выбранную смену\n\n"
        "<b>Пример:</b> <i>Алексей 10 лет 89123456789 Дети в бизнесе</i>",
        parse_mode=ParseMode.HTML
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "camp_back_to_description", Form.waiting_for_camp_option)
async def camp_back_to_description(callback: types.CallbackQuery, state: FSMContext):
    description = events["child"]["Городской лагерь"]["description"]
    details = events["child"]["Городской лагерь"]["details"]
    await safe_edit_message(
        f"{description}\n{details}\nХотите узнать подробности?",
        callback,
        reply_markup=get_camp_intro_keyboard(),
        state=state
    )
    await state.set_state(Form.waiting_for_camp_option)

@dp.message(Form.waiting_for_camp_registration)
async def process_camp_registration(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    
    # Проверяем и обрабатываем данные
    registration_details = await validate_and_process_registration(
        message, state,
        required_fields=['name', 'phone', 'age']
    )
    
    if not registration_details:
        return
    
    # Определяем смену
    camp_names = events["child"]["Городской лагерь"]["camps"].keys()
    camp_name = None
    for name in camp_names:
        if name.lower() in message.text.lower():
            camp_name = name
            break
    
    if not camp_name:
        await message.answer("❌ Не указана смена. Пожалуйста, укажите название смены")
        return
    
    registration_details += f" {camp_name}"

    # Сохраняем запись
    registration_data = {
        "event": f"Городской лагерь: {camp_name}",
        "details": registration_details,
        "timestamp": str(datetime.now())
    }
    await save_user_registration(message.from_user.id, registration_data)

    await bot.send_message(
        chat_id=NOTIFY_CHAT_ID,
        text=f"🏕️ Новая запись в городской лагерь ({camp_name}):\n"
             f"👶 Ребенок: {registration_details}\n"
             f"👤 От: @{message.from_user.username or 'нет'}",
        parse_mode=ParseMode.HTML
    )

    camp_data = events["child"]["Городской лагерь"]
    await message.answer(
        f"✅ <b>Запись оформлена!</b>\n\n"
        f"🏕️ Смена: {camp_name}\n"
        f"🏠 Адрес: {camp_data['address']}\n"
        f"💵 Стоимость: {camp_data['price']}\n\n"
        f"По всем вопросам: @alinarolina",
        parse_mode=ParseMode.HTML,
        reply_markup=get_camp_success_keyboard()
    )
    
    await state.clear()

@dp.callback_query(lambda c: c.data == "camp_back_to_description", Form.waiting_for_camp_option)
async def camp_back_to_description(callback: types.CallbackQuery, state: FSMContext):
    description = events["child"]["Городской лагерь"]["description"]
    details = events["child"]["Городской лагерь"]["details"]
    await safe_edit_message(
        f"{description}\n{details}\nХотите узнать подробности?",
        callback,
        reply_markup=get_camp_intro_keyboard(),
        state=state
    )
    await state.set_state(Form.waiting_for_camp_option)


# Обработчики для рисования
@dp.callback_query(lambda c: c.data == "drawing_more", Form.waiting_for_drawing_option)
async def process_drawing_more(callback: types.CallbackQuery, state: FSMContext):
    await safe_edit_message(
        "Рисование — это не только весело, но и полезно!\n"
        "Дети развивают воображение, мелкую моторику и творческое мышление.\n"
        "Наши занятия проходят в уютном центре CoolKids по адресу Рыбацкий пр-т 23/2.",
        callback,
        reply_markup=get_drawing_options_keyboard(),
        state=state
    )

@dp.callback_query(lambda c: c.data == "drawing_back_to_main", Form.waiting_for_drawing_option)
async def drawing_back_to_main(callback: types.CallbackQuery, state: FSMContext):
    description = events["child"]["Рисование"]["description"]
    details = events["child"]["Рисование"]["details"]
    await safe_edit_message(
        f"{description}\n{details}\nГотовы узнать подробности?",
        callback,
        reply_markup=get_drawing_keyboard(),
        state=state
    )
    await state.set_state(Form.waiting_for_drawing_option)

@dp.callback_query(lambda c: c.data == "drawing_back_to_options", Form.waiting_for_drawing_option)
async def drawing_back_to_options(callback: types.CallbackQuery, state: FSMContext):
    await process_drawing_more(callback, state)

@dp.callback_query(lambda c: c.data == "drawing_schedule", Form.waiting_for_drawing_option)
async def process_drawing_schedule(callback: types.CallbackQuery, state: FSMContext):
    schedule = events["child"]["Рисование"]["schedule"]
    await safe_edit_message(
        f"Расписание занятий:\n{schedule}",
        callback,
        reply_markup=get_drawing_schedule_keyboard(),
        state=state
    )

@dp.callback_query(lambda c: c.data == "drawing_price", Form.waiting_for_drawing_option)
async def process_drawing_price(callback: types.CallbackQuery, state: FSMContext):
    price = events["child"]["Рисование"]["price"]
    info = events["child"]["Рисование"]["info"]
    await safe_edit_message(
        f"Стоимость участия — {price}.\n"
        f"{info}",
        callback,
        reply_markup=get_drawing_price_keyboard(),
        state=state
    )

@dp.callback_query(lambda c: c.data == "drawing_register", Form.waiting_for_drawing_option)
async def drawing_register_handler(callback: types.CallbackQuery, state: FSMContext):
    try:
        await state.set_state(Form.waiting_for_user_data)
        await state.update_data(event="Рисование")
        await callback.message.answer(
            "🎨 <b>Запись на рисование</b>\n\n"
            "Для завершения регистрации отправьте:\n"
            "1. Имя и возраст ребенка\n"
            "2. Ваш номер телефона\n"
            "3. Удобное время (17:00 или 18:00)\n\n"
            "<b>Пример:</b> <i>Алексей 10 лет 89123456789 17:00</i>",
            parse_mode=ParseMode.HTML
        )
        logger.warning(await state.get_state())
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in drawing_register_handler: {e}")
        await callback.answer("Ошибка, попробуйте позже", show_alert=True)

@dp.message(Form.waiting_for_drawing_registration)
async def process_drawing_registration(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    
    # Проверяем и обрабатываем данные
    registration_details = await validate_and_process_registration(
        message, state,
        required_fields=['name', 'phone', 'age']
    )
    
    if not registration_details:
        return
    
    # Проверяем время
    time_match = re.search(r'(17|18)(?::00)?', message.text)
    if not time_match:
        await message.answer("❌ Не указано время. Пожалуйста, укажите 17:00 или 18:00")
        return
    
    time = time_match.group().replace(':00', '')
    registration_details += f" {time}:00"

    # Сохраняем запись
    registration_data = {
        "event": "Рисование",
        "details": registration_details,
        "timestamp": str(datetime.now())
    }
    await save_user_registration(message.from_user.id, registration_data)

    await bot.send_message(
        chat_id=NOTIFY_CHAT_ID,
        text=f"🎨 Новая запись на рисование:\n"
             f"👤 Данные: {registration_details}\n"
             f"От: @{message.from_user.username or 'нет'}",
        parse_mode=ParseMode.HTML
    )

    drawing_data = events["child"]["Рисование"]
    await message.answer(
        f"✅ <b>Вы успешно записаны на рисование!</b>\n\n"
        f"🏠 Адрес: {drawing_data['address']}\n"
        f"💵 Стоимость: {drawing_data['price']}\n\n"
        f"По всем вопросам: @alinarolina",
        parse_mode=ParseMode.HTML,
        reply_markup=get_chess_success_keyboard()
    )
    
    await state.clear()

# Обработчики для курсов английского языка
@dp.callback_query(lambda c: c.data == "child_Курсы_английского_языка")
async def process_english(callback: types.CallbackQuery, state: FSMContext):
    description = events["child"]["Курсы английского языка"]["description"]
    details = events["child"]["Курсы английского языка"]["details"]
    await safe_edit_message(
        f"{description}\n{details}\nГотовы узнать расписание и выбрать подходящую группу?",
        callback,
        reply_markup=get_english_keyboard(),
        state=state
    )
    await state.set_state(Form.waiting_for_english_option)

@dp.callback_query(lambda c: c.data == "english_more", Form.waiting_for_english_option)
async def process_english_more(callback: types.CallbackQuery, state: FSMContext):
    await safe_edit_message(
        "Пожалуйста, выберите возраст вашего ребёнка, чтобы я подобрал подходящую группу:",
        callback,
        reply_markup=get_english_age_keyboard(),
        state=state
    )
    await state.set_state(Form.waiting_for_english_age)

@dp.callback_query(lambda c: c.data.startswith("english_age_"), Form.waiting_for_english_age)
async def process_english_age(callback: types.CallbackQuery, state: FSMContext):
    age_group = callback.data.replace("english_age_", "").replace("_", " ")
    
    if age_group == "4 5":
        age_group = "4–5 лет"
        schedule = events["child"]["Курсы английского языка"]["schedule"][age_group][0]
        await safe_edit_message(
            f"Для малышей {age_group} пробное занятие пройдёт {schedule}.\n"
            f"Хотите записаться?",
            callback,
            reply_markup=get_english_schedule_keyboard(age_group),
            state=state
        )
    elif age_group == "6 7":
        age_group = "6–7 лет"
        await safe_edit_message(
            f"Для детей {age_group} доступны два пробных занятия:\n"
            f"• {events['child']['Курсы английского языка']['schedule'][age_group][0]}\n"
            f"• {events['child']['Курсы английского языка']['schedule'][age_group][1]}\n"
            f"Выберите удобное время:",
            callback,
            reply_markup=get_english_schedule_keyboard(age_group),
            state=state
        )
    elif age_group == "8 10":
        age_group = "8–10 лет"
        schedule = events["child"]["Курсы английского языка"]["schedule"][age_group][0]
        await safe_edit_message(
            f"Для ребят {age_group} пробное занятие состоится {schedule}.\n"
            f"Записать вашего ребёнка?",
            callback,
            reply_markup=get_english_schedule_keyboard(age_group),
            state=state
        )
    elif age_group == "10+":
        age_group = "Старше 10 лет"
        await safe_edit_message(
            f"Для детей {age_group} мы проводим индивидуальное интервью с преподавателем, чтобы подобрать оптимальную программу обучения.\n"
            f"Пожалуйста, оставьте свои данные, и мы свяжемся с вами для согласования времени:\n"
            f"• Имя и возраст ребёнка\n"
            f"• Ваше имя\n"
            f"• Контактный телефон",
            callback,
            reply_markup=get_english_schedule_keyboard(age_group),
            state=state
        )
    
    await state.update_data(age_group=age_group)

@dp.callback_query(lambda c: c.data.startswith("english_register_"), Form.waiting_for_english_age)
async def process_english_register(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    age_group = user_data.get("age_group", "")
    
    if "individual" in callback.data:
        await state.set_state(Form.waiting_for_english_registration)
        await callback.message.answer(
            "Пожалуйста, отправьте одним сообщением и в одну строчку:\n"
            "1. Имя и возраст ребёнка\n"
            "2. Ваше имя и фамилию\n"
            "3. Контактный телефон\n\n"
            "<b>Пример:</b> <i>Алексей 11 лет Мария 89123456789</i>",
            parse_mode=ParseMode.HTML
        )
    else:
        date = callback.data.replace("english_register_", "")
        await state.update_data(date=date, event="Курсы английского языка")
        await state.set_state(Form.waiting_for_english_registration)
        await callback.message.answer(
            "Пожалуйста, отправьте одним сообщением и в одну строчку:\n"
            "1. Имя и возраст ребёнка\n"
            "2. Ваше имя и фамилию\n"
            "3. Контактный телефон\n\n"
            "<b>Пример:</b> <i>Алексей 11 лет Мария 89123456789</i>",
            parse_mode=ParseMode.HTML
        )
    await callback.answer()

@dp.message(Form.waiting_for_english_registration)
async def process_english_registration(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    
    # Проверяем и обрабатываем данные
    registration_details = await validate_and_process_registration(
        message, state,
        required_fields=['name', 'phone']
    )
    
    if not registration_details:
        return
    
    age_group = user_data.get("age_group", "")
    date = user_data.get("date", "индивидуальное интервью")
    registration_details += f" {date}"

    # Сохраняем запись
    registration_data = {
        "event": f"Английский язык ({age_group})",
        "details": registration_details,
        "timestamp": str(datetime.now())
    }
    await save_user_registration(message.from_user.id, registration_data)

    await bot.send_message(
        chat_id=NOTIFY_CHAT_ID,
        text=f"🇬🇧 Новая запись на курсы английского:\n"
             f"👶 Возрастная группа: {age_group}\n"
             f"📅 Дата: {date}\n"
             f"📝 Данные: {registration_details}\n"
             f"👤 От: @{message.from_user.username or 'нет'}",
        parse_mode=ParseMode.HTML
    )

    await message.answer(
        f"✅ <b>Спасибо за запись!</b>\n\n"
        f"Мы ждём вас в Центре CoolKids по адресу {events['child']['Курсы английского языка']['address']}.\n\n"
        f"По всем вопросам: @alinarolina",
        parse_mode=ParseMode.HTML,
        reply_markup=get_english_success_keyboard()
    )
    
    await state.clear()

# Обработчики кнопок "Назад"
@dp.callback_query(lambda c: c.data == "english_back", Form.waiting_for_english_age)
async def english_back_handler(callback: types.CallbackQuery, state: FSMContext):
    description = events["child"]["Курсы английского языка"]["description"]
    details = events["child"]["Курсы английского языка"]["details"]
    await safe_edit_message(
        f"{description}\n{details}\nГотовы узнать расписание и выбрать подходящую группу?",
        callback,
        reply_markup=get_english_keyboard(),
        state=state
    )
    await state.set_state(Form.waiting_for_english_option)

@dp.callback_query(lambda c: c.data == "english_back_to_age", Form.waiting_for_english_age)
async def english_back_to_age_handler(callback: types.CallbackQuery, state: FSMContext):
    await safe_edit_message(
        "Пожалуйста, выберите возраст вашего ребёнка, чтобы я подобрал подходящую группу:",
        callback,
        reply_markup=get_english_age_keyboard(),
        state=state
    )

@dp.callback_query(lambda c: c.data == "child_back")
async def child_back_handler(callback: types.CallbackQuery, state: FSMContext):
    try:
        # Пытаемся редактировать сообщение
        await callback.message.edit_text(
            "Какое детское мероприятие вас интересует?",
            reply_markup=get_child_events_keyboard()
        )
        await state.set_state(Form.waiting_for_event)
        await callback.answer()
    except Exception as e:
        # Если не получилось редактировать (например, сообщение слишком старое)
        await callback.message.answer(
            "Какое детское мероприятие вас интересует?",
            reply_markup=get_child_events_keyboard()
        )
        await state.set_state(Form.waiting_for_event)
        await callback.answer()

@dp.callback_query(lambda c: c.data == "back_to_event_type")
async def back_to_event_type_handler(callback: types.CallbackQuery, state: FSMContext):
    await safe_edit_message(
        "Что тебя интересует?",
        callback,
        reply_markup=get_event_type_keyboard(),
        state=state
    )
    await state.set_state(Form.waiting_for_event)

@dp.callback_query(lambda c: c.data == "back_to_adult_events")
async def back_to_adult_events_handler(callback: types.CallbackQuery, state: FSMContext):
    await safe_edit_message(
        "Какое мероприятие вас интересует?",
        callback,
        reply_markup=get_adult_events_keyboard(),
        state=state
    )
    await state.set_state(Form.waiting_for_event)

@dp.callback_query(lambda c: c.data == "lectures_back")
async def lectures_back_handler(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state in [Form.waiting_for_lecture_option.state, Form.waiting_for_lecture_topic.state]:
        description = events["adult"]["Лекции"]["description"]
        await safe_edit_message(
            f"{description}\n\n"
            f"Всё проходит в уютном Лофте по адресу {events['adult']['Лекции']['address']}.\n"
            "Готовы узнать подробности?",
            callback,
            reply_markup=get_lectures_intro_keyboard(),
            state=state
        )
        await state.set_state(Form.waiting_for_lecture_option)
    else:
        await callback.answer("Нельзя вернуться назад из этого состояния")  

@dp.callback_query(lambda c: c.data == "back_to_lectures")
async def back_to_lectures_handler(callback: types.CallbackQuery, state: FSMContext):
    lectures = events["adult"]["Лекции"]["lectures"]
    lectures_text = "В этом месяце вас ждут три вдохновляющие лекции:\n\n"
    
    for i, (key, lecture) in enumerate(lectures.items(), 1):
        lectures_text += f"{i}️⃣ {lecture['title']}\n{lecture['description']}\n\n"
    
    await safe_edit_message(
        lectures_text,
        callback,
        reply_markup=get_lectures_topics_keyboard(),
        state=state
    )
    await state.set_state(Form.waiting_for_lecture_option)

@dp.callback_query(lambda c: c.data == "back_to_start")
async def back_to_start_handler(callback: types.CallbackQuery, state: FSMContext):
    await safe_edit_message(
        "Что тебя интересует?",
        callback,
        reply_markup=get_event_type_keyboard(),
        state=state
    )
    await state.set_state(Form.waiting_for_event)

@dp.callback_query(lambda c: c.data == "camp_back_to_main", Form.waiting_for_camp_option)
async def camp_back_to_main(callback: types.CallbackQuery, state: FSMContext):
    description = events["child"]["Городской лагерь"]["description"]
    details = events["child"]["Городской лагерь"]["details"]
    await safe_edit_message(
        f"{description}\n{details}\nХотите узнать подробности?",
        callback,
        reply_markup=get_camp_intro_keyboard(),
        state=state
    )
    await state.set_state(Form.waiting_for_camp_option)

@dp.callback_query(lambda c: c.data == "camp_back_to_options", Form.waiting_for_camp_details)
async def camp_back_to_options_handler(callback: types.CallbackQuery, state: FSMContext):
    camps = events["child"]["Городской лагерь"]["camps"]
    camps_text = "В этом году мы подготовили 6 тематических смен — каждый ребёнок найдёт себе занятие по душе!\n\n"
    
    for camp_name, camp_data in camps.items():
        camps_text += f"• {camp_name} — {camp_data['dates']}\n"
    
    await safe_edit_message(
        camps_text,
        callback,
        reply_markup=get_camp_options_keyboard(),
        state=state
    )
    await state.set_state(Form.waiting_for_camp_option)

@dp.callback_query(lambda c: c.data == "drawing_back_to_main")
async def drawing_back_to_main_handler(callback: types.CallbackQuery, state: FSMContext):
    description = events["child"]["Рисование"]["description"]
    details = events["child"]["Рисование"]["details"]
    await safe_edit_message(
        f"{description}\n{details}\nГотовы узнать подробности?",
        callback,
        reply_markup=get_drawing_keyboard(),
        state=state
    )
    await state.set_state(Form.waiting_for_drawing_option)

@dp.callback_query(lambda c: c.data == "to_main_menu")
async def return_to_main_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await callback.message.delete()
    except:
        pass
    await callback.message.answer(
        "Что тебя интересует?",
        reply_markup=get_event_type_keyboard()
    )
    await callback.answer()
    await state.set_state(Form.waiting_for_event)
    # Обработчик для всех необработанных callback-запросов
@dp.callback_query()
async def handle_unprocessed_callbacks(callback: types.CallbackQuery):
    try:
        await callback.answer()
    except:
        pass

# Запуск бота
async def main():
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == '__main__':
    asyncio.run(main())