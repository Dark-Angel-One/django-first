# Google Keep Clone - Academy Project

A professional, "Pixel-perfect" clone of Google Keep, built with Django 6 and Tailwind CSS. This project demonstrates modern "Hybrid" web architecture, combining server-side rendering with a dynamic API-driven frontend.

## 🚀 Features

### Core Functionality
- **Checklists & Todo Mode**: Create dynamic checklists with checkboxes, progress tracking, and strikethrough completion.
- **Smart Reminders (Audio + Auto-Archive)**: Set reminders that play a sound when due and automatically move the note to the Archive.
- **Organization**: Pin important notes, Archive old ones, and Move to Trash (Soft Delete).
- **Color Coding**: Organize notes visually with a palette of 12 colors (Dark Mode compatible).
- **Live Search**: Real-time filtering of notes by title and content.

### UI/UX (2025 Standards)
- **Glassmorphism & Bento Layout**: Modern, grid-based layout using Tailwind CSS.
- **Optimistic UI**: Instant feedback for actions like Pinning and Checkbox toggling, ensuring the interface feels snappy even on slow networks.
- **Dark/Light Mode**: Fully supported with persistent preference (localStorage).
- **Responsive Design**: Collapsible sidebar and mobile-friendly interface.
- **Micro-interactions**: Hover effects, smooth transitions, and dynamic modals.

### Technical Excellence
- **Hybrid Architecture**: Django Templates for SEO/Initial Load + JS/DRF for interactivity.
- **Security**: User isolation (access only your own notes), CSRF protection, and Environment variables.
- **Clean Code**: Follows Django best practices and separation of concerns.

## 🛠 Tech Stack

- **Backend**: Python 3.12, Django 6.0, Django REST Framework (DRF).
- **Frontend**: HTML5, Tailwind CSS (via CDN), Vanilla JavaScript (ES6+).
- **Database**: SQLite (Development), Extensible to PostgreSQL.
- **Utilities**: `python-dotenv`, `django-filter`.

## 📦 Installation Guide

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/django-keep-clone.git
   cd django-keep-clone
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**
   Create a `.env` file in the root directory (copy from `.env.example`):
   ```env
   SECRET_KEY=your-secret-key
   DEBUG=True
   ```

5. **Apply Migrations**
   ```bash
   python manage.py migrate
   ```

6. **Run Server**
   ```bash
   python manage.py runserver
   ```
   Access the app at `http://127.0.0.1:8000`.

## 🔌 API Endpoints

All API endpoints are prefixed with `/api/v1/`. Authentication is required.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/notes/` | List all active notes (searchable) |
| POST | `/notes/` | Create a new note |
| GET | `/notes/{id}/` | Retrieve note details |
| PATCH | `/notes/{id}/` | Partial update (title, content, color) |
| DELETE | `/notes/{id}/` | Delete note (Hard delete) |
| POST | `/notes/{id}/archive/` | Toggle Archive status |
| POST | `/notes/{id}/trash/` | Toggle Trash status |
| POST | `/notes/{id}/pin/` | Toggle Pin status |
| POST | `/notes/empty_trash/` | Permanently delete all trashed notes |

## 🗄 Database Schema

- **User** (Django Auth): Owns Notes and Labels.
- **Note**:
  - `user` (FK): Owner.
  - `title`, `content`: Text data.
  - `color`: Visual style.
  - `is_pinned`, `is_archived`, `is_trashed`: Status flags.
  - `is_checklist`: Toggle for display mode.
- **ChecklistItem**:
  - `note` (FK): Parent note.
  - `text`, `is_checked`: Item data.
  - `order`: Sorting order.
- **Label**:
  - `user` (FK): Owner.
  - `name`: Label text.
  - `notes` (ManyToMany): Relation to notes.
