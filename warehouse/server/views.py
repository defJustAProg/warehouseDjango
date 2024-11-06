from django.shortcuts import render
import os
from server.models import Roll
from django.forms.models import model_to_dict
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from server.tgBotService import send_record_to_bot
from datetime import datetime
from django.db.models import Avg, Max, Min, Sum
from asgiref.sync import sync_to_async
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render
from .forms import LoginForm, UserRegistrationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return HttpResponseRedirect('http://localhost:8000/api/')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)  # Проверка учетных данных
            if user is not None:
                login(request, user)  # Вход в систему
                return HttpResponseRedirect('http://localhost:8000/api/')
            else:
                form.add_error(None, 'Неверное имя пользователя или пароль.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('http://localhost:8000/api/accounts/login/')


# Главная страница
def get_start_page(request):
    return render(request, "index.html")

# Добавление нового ролла
@login_required
async def add_roll(request):
    if request.method == "PUT":
        try:
            body = json.loads(request.body)
            record = await sync_to_async(Roll.objects.create)(**body)

            # Если контейнер с ботом был запущен
            if os.environ.get('BOT_ENABLED') == 'true':
                await send_record_to_bot(os.environ['BOT_URL'], record)

            return JsonResponse(model_to_dict(record), status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            # print("error: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)

# Получение данных с сортировкой
def get_rolls(request):
    roll_sort_model = request.GET.get('rollSortModel')
    if roll_sort_model:
        try:
            # Преобразуем строку в словарь
            filter_params = json.loads(roll_sort_model)
            # Получаем отфильтрованные записи
            data = Roll.objects.filter(**filter_params)

            # Преобразуем QuerySet в список словарей
            data_list = list(data.values())  # Используем values() для получения словарей

            return JsonResponse(data_list, safe=False)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Missing rollSortModel parameter"}, status=400)

# Удаление ролла
@login_required
def delete_roll(request):
    if request.method == "DELETE":
        roll_id = request.GET.get('id')
        if roll_id:
            try:
                # Получаем объект по id, если он не найден, будет возвращен 404
                roll = get_object_or_404(Roll, id=roll_id)
                roll.status = False  # Устанавливаем статус как "удаленный"
                roll.save()
                roll_dict = model_to_dict(roll)  # Преобразуем объект в словарь
                return JsonResponse(roll_dict, status=200)  # Возвращаем удаленный объект

            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)  # Обработка других исключений

        return JsonResponse({"error": "Missing id parameter"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=400)

# Получение статистики
def get_statistics(request):
    put_date = request.GET.get('put_date')
    delete_date = request.GET.get('delete_date')

    if put_date and delete_date:
        try:
            # Преобразуем строки в объекты даты
            request_put_date = datetime.strptime(put_date, '%Y-%m-%d').date()
            request_delete_date = datetime.strptime(delete_date, '%Y-%m-%d').date()

            # Фильтруем записи по датам
            rolls = Roll.objects.filter(put_date__gte=request_put_date, delete_date__lte=request_delete_date)

            if rolls.exists():
                count_of_rolls = rolls.count()
                count_of_delete_rolls = rolls.filter(status=False).count()
                avg_length = rolls.aggregate(Avg('length'))['length__avg'] or 0
                avg_weight = rolls.aggregate(Avg('weight'))['weight__avg'] or 0
                max_length = rolls.aggregate(Max('length'))['length__max'] or 0
                min_length = rolls.aggregate(Min('length'))['length__min'] or 0
                max_weight = rolls.aggregate(Max('weight'))['weight__max'] or 0
                min_weight = rolls.aggregate(Min('weight'))['weight__min'] or 0
                sum_weight = rolls.aggregate(Sum('weight'))['weight__sum'] or 0

                return JsonResponse({
                    "count_of_rolls": count_of_rolls,
                    "count_of_delete_rolls": count_of_delete_rolls,
                    "avg_length": avg_length,
                    "avg_weight": avg_weight,
                    "max_length": max_length,
                    "min_length": min_length,
                    "max_weight": max_weight,
                    "min_weight": min_weight,
                    "sum_weight": sum_weight
                })

            else:
                return JsonResponse({"message": "No records for the period"}, status=404)

        except ValueError:
            return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

    return JsonResponse({"error": "Missing date parameters"}, status=400)