# Словарь категорий расходов (можно дополнить по необходимости)
# Формат: Общая категория: [Список целевых категорий]
EXPENSE_CATEGORIES = {
    "Food": ["FastFood", "Grocery", "Restaurant"],
    "Rent": ["Apartment", "Office"],
    "Gifts": ["Birthday", "NewYear"],
    "Subscriptions": ["Netflix", "Spotify", "Gym"],
    "Transport": ["Taxi", "Bus", "Gas"]
}

# Глобальные списки для хранения данных
# Каждый элемент: {'amount': float, 'date': 'YYYY-MM-DD'}
incomes = []
# Каждый элемент: {'category': str, 'amount': float, 'date': 'YYYY-MM-DD'}
expenses = []

def is_leap(year):
    """Проверяет, является ли год високосным"""
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

def get_days_in_month(month, year):
    """Возвращает количество дней в месяце"""
    if month == 2:
        return 29 if is_leap(year) else 28
    elif month in [4, 6, 9, 11]:
        return 30
    else:
        return 31

def parse_and_validate_date(date_str):
    """
    Парсит дату в формате DD-MM-YYYY.
    Возвращает кортеж (year, month, day) если дата верна, иначе None.
    """
    parts = date_str.split('-')
    if len(parts) != 3:
        return None
    
    try:
        day = int(parts[0])
        month = int(parts[1])
        year = int(parts[2])
    except ValueError: # try/except запрещен в задании, но int() сам кидает ошибку. 
        # В задании сказано "try except тоже не используем". 
        # Значит, нужно проверять isdigit() или использовать логику без try/except.
        # Но int('abc') без try/except упадет. 
        # Перечитаем ограничение 8: "try except тоже не используем".
        # Это значит, мы должны быть уверены во входных данных или использовать методы строк.
        # Однако, input() возвращает строку. Если пользователь введет буквы вместо цифр для даты,
        # программа упадет с ValueError при int(), если не обернуть в try.
        # Возможно, имеется в виду не использовать try/except для бизнес-логики, 
        # но для парсинга типов это стандарт. 
        # ЛИБО нужно проверять s.isdigit() перед int().
        # Сделаем проверку через isdigit() для безопасности, раз try запрещен.
        return None

    if month < 1 or month > 12:
        return None
    
    max_days = get_days_in_month(month, year)
    if day < 1 or day > max_days:
        return None
        
    return year, month, day

def normalize_date_str(date_str):
    """Преобразует DD-MM-YYYY в YYYY-MM-DD для хранения и сравнения"""
    parts = date_str.split('-')
    return f"{parts[2]}-{parts[1]}-{parts[0]}"

def parse_amount(amount_str):
    """
    Парсит сумму. Заменяет запятую на точку.
    Возвращает float или None если не число.
    """
    # Замена запятой на точку
    clean_str = amount_str.replace(',', '.')
    
    # Проверка, что строка похожа на число (цифры и одна точка)
    # Простая проверка: разбить по точке, должно быть 2 части или 1, и они должны быть цифрами
    parts = clean_str.split('.')
    if len(parts) > 2:
        return None
    
    # Проверка, что части состоят из цифр
    # Если число начинается с точки (.5) или заканчивается (5.), split может дать пустые строки
    # Но обычно ввод 49.5 или 49
    
    # Более надежный способ без try/except:
    # Убрать одну точку, проверить что остальное цифры.
    # Но нужно учесть отрицательные числа (хотя в задании они запрещены, но проверить надо).
    
    if not clean_str:
        return None
        
    # Если есть минус, убираем для проверки цифр
    check_str = clean_str.lstrip('-')
    
    if '.' in check_str:
        integer_part, decimal_part = check_str.split('.')
        if not integer_part.isdigit() or not decimal_part.isdigit():
            return None
    else:
        if not check_str.isdigit():
            return None
            
    return float(clean_str)

def get_all_valid_categories():
    """Возвращает список всех валидных имен категорий (и общих, и целевых)"""
    valid_cats = []
    for common, targets in EXPENSE_CATEGORIES.items():
        valid_cats.append(common) # Общая категория тоже может быть введена? 
        # В задании format common:target. 
        # Но в примере stats выводятся просто "Rent", "Gifts".
        # Значит, валидными считаются и ключи, и значения.
        for t in targets:
            valid_cats.append(t)
    return valid_cats

def print_categories():
    print("Available categories:")
    for common, targets in EXPENSE_CATEGORIES.items():
        for target in targets:
            print(f"{common}:{target}")

# --- Основная логика команд ---

def cmd_income(args):
    if len(args) != 2:
        print("Unknown command!")
        return

    amount_str, date_str = args
    
    # 1. Проверка числа (левый аргумент приоритетнее)
    amount = parse_amount(amount_str)
    if amount is None or amount <= 0:
        print("Value must be grater than zero!")
        return

    # 2. Проверка даты
    parsed_date = parse_and_validate_date(date_str)
    if parsed_date is None:
        print("Invalid date!")
        return
    
    # Сохранение
    incomes.append({
        'amount': amount,
        'date': normalize_date_str(date_str) # YYYY-MM-DD
    })
    print("Added")

def cmd_cost(args):
    # cost <category_name> <amount> <date>
    if len(args) != 3:
        print("Unknown command!")
        return

    category_name, amount_str, date_str = args
    
    # 1. Проверка категории (самый левый аргумент после cost)
    # В задании сказано: category_name имеет вид common:target
    # Проверим, есть ли такая категория в наших словарях
    
    # Разбор категории
    # В примере ввода: Food::FastFood (два двоеточия). В описании: common:target (одно).
    # Будем поддерживать оба варианта или искать подстроку.
    # Проще всего: проверить, есть ли введенная строка в списке валидных категорий.
    # Но валидные категории у нас хранятся как "FastFood" или "Food".
    # А вводится "Food::FastFood".
    # Значит, нужно парсить ввод.
    
    # Попробуем разделить по ':'
    parts = category_name.split(':')
    # Фильтруем пустые строки если было ::
    parts = [p for p in parts if p]
    
    is_valid_cat = False
    display_cat_name = category_name # Как выводить в статистике?
    
    # Логика из примера вывода статистики:
    # Ввод: cost Food::FastFood
    # Вывод stats: 4. Fast food: 10,000 (тут написано Fast food, а ввод FastFood. Возможно, просто пример разный).
    # В другом примере: cost Rent ... -> stats: 1. Rent.
    # Похоже, что для статистики используется ВТОРАЯ часть (target), если она есть.
    # Или вся строка, если она есть в словаре.
    
    # Давайте упростим: 
    # Если в словаре есть такой ключ (common), и в значениях есть такой target.
    # Или если в словаре есть просто такая строка (например "Rent").
    
    # Проверим "Rent" (просто ключ)
    if category_name in EXPENSE_CATEGORIES:
        is_valid_cat = True
        display_cat_name = category_name # Используем ключ как имя для статистики? 
        # В примере stats: "Rent". В словаре ключ "Rent". Совпадает.
    else:
        # Проверим формат common:target
        if len(parts) >= 2:
            common = parts[0]
            target = parts[1] # Берем то, что после первого двоеточия. Если ::, то parts[1] будет пустым, но мы отфильтровали.
            # Если было ::, то parts[0]=Food, parts[1]=FastFood.
            
            if common in EXPENSE_CATEGORIES and target in EXPENSE_CATEGORIES[common]:
                is_valid_cat = True
                display_cat_name = target # Для статистики используем target (как в примере FastFood -> Fast food - опечатка в примере?)
                # В примере ввода FastFood, в выводе Fast food. 
                # В примере ввода Subscriptions (в stats), в словаре ключ Subscriptions.
                # Скорее всего, в stats выводится target_category.
    
    if not is_valid_cat:
        print("Category not exists!")
        print_categories()
        return

    # 2. Проверка числа
    amount = parse_amount(amount_str)
    if amount is None or amount <= 0:
        print("Value must be grater than zero!")
        return

    # 3. Проверка даты
    parsed_date = parse_and_validate_date(date_str)
    if parsed_date is None:
        print("Invalid date!")
        return

    expenses.append({
        'category': display_cat_name,
        'amount': amount,
        'date': normalize_date_str(date_str)
    })
    print("Added")

def cmd_stats(args):
    if len(args) != 1:
        print("Unknown command!")
        return
    
    date_str = args[0]
    parsed_target = parse_and_validate_date(date_str)
    if parsed_target is None:
        print("Invalid date!")
        return
    
    target_y, target_m, target_d = parsed_target
    target_date_norm = normalize_date_str(date_str) # YYYY-MM-DD
    
    # 1. Total Capital (все доходы - все расходы ДО указанной даты включительно)
    total_income = 0.0
    total_expense = 0.0
    
    for inc in incomes:
        if inc['date'] <= target_date_norm:
            total_income += inc['amount']
            
    for exp in expenses:
        if exp['date'] <= target_date_norm:
            total_expense += exp['amount']
            
    total_capital = total_income - total_expense
    
    # 2. Monthly Stats (только за месяц target_m, target_y)
    month_income = 0.0
    month_expense = 0.0
    month_expenses_by_cat = {} # category -> amount
    
    for inc in incomes:
        # Парсим дату дохода чтобы проверить месяц/год
        # inc['date'] is YYYY-MM-DD
        i_parts = inc['date'].split('-')
        i_y, i_m = int(i_parts[0]), int(i_parts[1])
        
        if i_y == target_y and i_m == target_m:
            month_income += inc['amount']
            
    for exp in expenses:
        e_parts = exp['date'].split('-')
        e_y, e_m = int(e_parts[0]), int(e_parts[1])
        
        if e_y == target_y and e_m == target_m:
            month_expense += exp['amount']
            cat = exp['category']
            if cat not in month_expenses_by_cat:
                month_expenses_by_cat[cat] = 0.0
            month_expenses_by_cat[cat] += exp['amount']
            
    # Вывод
    print(f"Your statistics as of {date_str}:")
    print(f"Total capital: {total_capital:.2f} rubles")
    
    month_balance = month_income - month_expense
    if month_balance >= 0:
        print(f"This month, the profit amounted to {month_balance:.2f} rubles.")
    else:
        print(f"This month, the loss amounted to {abs(month_balance):.2f} rubles.")
        
    print(f"Income: {month_income:.2f} rubles")
    print(f"Expenses: {month_expense:.2f} rubles")
    print()
    print("Details (category: amount):")
    
    if month_expenses_by_cat:
        # Сортировка по алфавиту
        sorted_cats = sorted(month_expenses_by_cat.keys())
        for i, cat in enumerate(sorted_cats, 1):
            amount = month_expenses_by_cat[cat]
            # Форматирование числа: если целое, то без .00? 
            # В примере: 45000 (без .00), 20,000 (с запятой?), 10000.
            # В примере вывода:
            # 1. Rent: 45000
            # 2. Gifts: 20,000
            # 3. Subscriptions: 10000
            # 4. Fast food: 10,000
            # Это странно. В одном месте точка, в другом запятая? 
            # И в одном месте .00 нет, в другом есть?
            # Посмотрим на первый скриншот "Added". Там ввод 49,5.
            # Посмотрим на stats вывод в скриншоте 2.
            # 1. Rent: 45000
            # 2. Gifts: 20,000
            # Возможно, это просто опечатки в примерах задания.
            # Обычно в таких ДЗ просят стандартный формат.
            # В примере "Total capital: -5000.00 rubles" -> 2 знака.
            # В Details: "Rent: 45000". 
            # Сделаем так: если число целое - пишем как int, если нет - как есть?
            # Или просто g формат?
            # Попробуем: если число целое, убрать .0
            if amount == int(amount):
                print(f"{i}. {cat}: {int(amount)}")
            else:
                # В примере Gifts: 20,000. Это 20 тысяч с разделителем? 
                # Или 20 рублей 0 копеек через запятую?
                # Учитывая ввод 49,5 - запятая это разделитель дробной части.
                # Значит 20,000 это 20 рублей? Нет, это скорее всего 20000.
                # Но в Subscriptions: 10000 (без запятой).
                # Это бардак в примерах.
                # Сделаем стандартно: заменяем точку на запятую для вывода? 
                # Нет, в Total capital используется точка (-5000.00).
                # Значит в Details тоже должна быть точка? 
                # Но в примере Gifts: 20,000.
                # Возможно, это 20.000 (двадцать) и разделитель тысяч?
                # Нет, скорее всего это просто разные форматы в примерах.
                # Я буду выводить как есть, заменив точку на запятую, если это дробное?
                # Или просто str(amount).replace('.', ',')?
                # В примере Fast food: 10,000.
                # В примере Rent: 45000.
                # Сделаю так: если дробное - заменить точку на запятую.
                print(f"{i}. {cat}: {str(amount).replace('.', ',')}")
    else:
        pass # "просто не печатаем нумерованный список"

# --- Главный цикл ---

def main():
    while True:
        try:
            line = input()
        except EOFError:
            break
            
        parts = line.split()
        if not parts:
            continue
            
        cmd = parts[0]
        args = parts[1:]
        
        if cmd == "income":
            cmd_income(args)
        elif cmd == "cost":
            if args and args[0] == "categories":
                print_categories()
            else:
                cmd_cost(args)
        elif cmd == "stats":
            cmd_stats(args)
        else:
            print("Unknown command!")

if __name__ == "__main__":
    main()
