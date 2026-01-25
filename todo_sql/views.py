from django.shortcuts import render, redirect  # Не забудь redirect!
from .models import Task
from .forms import TaskForm  # <--- 1. Импортируем нашу новую форму
from django.urls import reverse_lazy # Понадобится для переадресации
from django.views.generic import UpdateView, DeleteView , CreateView, ListView# Импортируем готовый класс-редактор
from django.views import View  # <--- Не забудь добавить этот импорт!
from django.shortcuts import get_object_or_404, redirect
# (get_object_or_404 - это более безопасный способ сделать .get)



class TaskCreateView(CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'add.html'       # Нам понадобится простой шаблон
    success_url = reverse_lazy('index') # Куда вернуться после успеха


# 2. КЛАСС ПРОСМОТРА (Вместо функции index)
class TaskListView(ListView):
    model = Task
    template_name = 'index.html'
    context_object_name = 'tasks'  # Важно! Чтобы в HTML мы по-прежнему использовали имя 'tasks'

    # Настройка сортировки (аналог order_by)
    # Если в models.py есть ordering, эту строку можно не писать, но для надежности оставим:
    ordering = ['-created_at']


# def index(request):
#     # --- БЛОК 1: ОБРАБОТКА ДАННЫХ (Если нажали кнопку) ---
#     if request.method == 'POST':
#         # Мы "скармливаем" данные из запроса в нашу Форму
#         form = TaskForm(request.POST)
#
#         # Django сам проверяет: заполнили ли обязательные поля? Не слишком ли длинный текст?
#         if form.is_valid():
#             form.save()  # МАГИЯ! Сам создает запись в БД SQL
#             return redirect('index')
#     else:
#         form = TaskForm()
#
#     # --- БЛОК 2: ПОКАЗ СТРАНИЦЫ (Обычный заход) ---
#
#     # Получаем задачи из базы
#     tasks = Task.objects.all()  # order_by сортирует: новые сверху (-)
#
#
#     context = {
#         'tasks': tasks,
#         'form': form,  # <--- Передаем форму в HTML
#     }
#     return render(request, 'index.html', context)


class TaskToggleView(View):
    def get(self, request, pk):
        # 1. Ищем задачу по PK (Primary Key = ID)
        task = Task.objects.get(id=pk)

        # 2. Меняем статус
        task.is_completed = not task.is_completed
        task.save()

        # 3. Уходим на главную
        return redirect('index')

def toggle_task(request, task_id):
    # 1. Ищем задачу по ID
    # Task.objects.get() — это команда "Дай мне конкретную запись"
    task = Task.objects.get(id=task_id)

    # 2. Переворачиваем статус
    # Оператор 'not' делает из True -> False, а из False -> True
    task.is_completed = not task.is_completed

    # 3. Сохраняем изменения в базу SQL
    task.save()

    # 4. Возвращаемся на главную
    return redirect('index')

class TaskDeleteView(DeleteView):
    model = Task
    success_url = reverse_lazy('index') # Куда вернуть после удаления
    template_name = 'delete.html'       # Шаблон с вопросом "Вы уверены?"

# def delete_task(request, task_id):
#     # 1. Ищем задачу по ID
#     # Если такого ID нет, Django выдаст ошибку, но пока считаем, что всё ок
#     task = Task.objects.get(id=task_id)
#
#     # 2. Удаляем её из базы данных
#     # Это одна команда, которая заменяет нам кучу кода с открытием/записью файла!
#     task.delete()
#
#     # 3. Возвращаемся на главную
#     return redirect('index')

# Класс для редактирования
class TaskUpdateView(UpdateView):
    model = Task                    # 1. С какой моделью работаем?
    form_class = TaskForm           # 2. Какую форму используем?
    template_name = 'edit.html'     # 3. Какой HTML-шаблон показать?
    success_url = reverse_lazy('index') # 4. Куда перейти после успеха?

# # Функция редактирования
# def edit_task(request, task_id):
#     # 1. Ищем "пациента" в базе данных
#     task = Task.objects.get(id=task_id)
#
#     # 2. Если нажали "Сохранить" (POST)
#     if request.method == 'POST':
#         # ВАЖНО: передаем instance=task, чтобы Django знал, кого обновлять
#         form = TaskForm(request.POST, instance=task)
#         if form.is_valid(): # проверка на дурака
#             form.save()
#             return redirect('index') # Возвращаемся на главную
#     # 3. Если просто открыли страницу (GET)
#     else:
#         # Мы создаем форму, но уже ЗАПОЛНЕННУЮ старыми данными (instance=task)
#         form = TaskForm(instance=task)
#     # 4. Отправляем на отдельную страницу редактирования
#     context = {
#         'form': form,
#         'task': task
#     }
#     return render(request, 'edit.html', context)