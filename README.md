# Django Google Notes Clone

An improved Django application inspired by Google Keep.
Улучшенное Django-приложение, вдохновленное Google Keep.

## Features / Возможности

- **Create Notes**: Add notes quickly without page reload.
  **Создание заметок**: Быстрое добавление заметок без перезагрузки страницы.
- **Color Coding**: Organize notes with pastel colors.
  **Цветовая кодировка**: Организация заметок с помощью пастельных цветов.
- **Pinning**: Pin important notes to the top.
  **Закрепление**: Закрепляйте важные заметки сверху.
- **Search**: Filter notes by title or content.
  **Поиск**: Фильтрация заметок по заголовку или содержимому.
- **Responsive Grid**: Masonry-like grid layout.
  **Адаптивная сетка**: Сетка в стиле Masonry.

## Screenshots / Скриншоты

![Main Interface / Главный интерфейс](placeholder_main.png)
![Edit Note / Редактирование заметки](placeholder_edit.png)

## Installation / Установка

1. **Clone the repository / Клонируйте репозиторий:**
   ```bash
   git clone <repository_url>
   cd django-google-notes
   ```

2. **Create a virtual environment / Создайте виртуальное окружение:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install requirements / Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```
   *Note: Ensure `django` is installed. If not, run `pip install django`.*

4. **Apply migrations / Примените миграции:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Run the server / Запустите сервер:**
   ```bash
   python manage.py runserver
   ```

6. **Open in browser / Откройте в браузере:**
   http://127.0.0.1:8000/

## Project Structure / Структура проекта

- `config/`: Project settings.
- `todo_sql/`: Main application (renamed internally to Notes logic).
  - `models.py`: `Note` model definition.
  - `views.py`: Logic for creating, listing, updating notes.
  - `templates/`: HTML templates.
  - `static/`: CSS and JS files.

## Tech Stack / Стек технологий

- Python 3
- Django 5+
- HTML5 / CSS3 (CSS Grid)
- JavaScript (Fetch API)
