import re

DAY_VARIANTS = {
    'понедельник': 'Monday',
    'пн': 'Monday',
    'вторник': 'Tuesday',
    'вт': 'Tuesday',
    'среда': 'Wednesday',
    'ср': 'Wednesday',
    'четверг': 'Thursday',
    'чт': 'Thursday',
    'пятница': 'Friday',
    'пт': 'Friday',
    'суббота': 'Saturday',
    'сб': 'Saturday',
    'воскресенье': 'Sunday',
    'вс': 'Sunday'
}


def days_or_months(text):
    days_result = []
    numbers_result = []
    words = re.split(r'[,. ]+', text.replace(',', ''))
    for word in words:
        if word.lower() in DAY_VARIANTS:
            if DAY_VARIANTS[word.lower()] not in days_result:
                days_result.append(DAY_VARIANTS[word.lower()])
        else:
            try:
                num = int(word)
                if 1 <= num <= 31:
                    if str(num) not in numbers_result:
                        numbers_result.append(str(num))
            except ValueError:
                pass
    return days_result, numbers_result


def extract_time_intervals(time_string: str) -> str:
    time_intervals = []
    intervals = re.findall(r'\b\d{1,2}[-:]\d{2}\b', time_string)
    for interval in intervals:
        hours, minutes = map(
            int,
            interval.split('-' if '-' in interval else ':')
        )
        if 0 <= hours <= 23 and 0 <= minutes <= 59:
            time_intervals.append(interval.replace('-', ':'))
    return ', '.join(time_intervals)
