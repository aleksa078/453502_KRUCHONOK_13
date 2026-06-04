"""Function-Based Views: страницы, доступы, CRUD, покупка, API и статистика."""
import logging
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.db.models import Exists, OuterRef, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods

from core.charts import chart_sales_by_category, chart_sales_timeline
from core.decorators import employee_or_superuser
from core.external_api import fetch_age_by_name, fetch_cat_fact, fetch_weather
from core.forms import ProfileSettingsForm, PropertyForm, PurchaseConfirmForm, RegisterForm, ReviewForm, SaleForm
from core.models import (
    Buyer,
    Category,
    CompanyInfo,
    ContactPerson,
    Employee,
    FAQEntry,
    NewsArticle,
    PromoCode,
    Property,
    PropertyImage,
    Review,
    Sale,
    UserProfile,
    Vacancy,
)
from core.parallel_utils import fetch_home_widgets_parallel
from core.statistics import client_age_stats, popular_category_by_count, profitable_category, sale_amount_stats
from core.timezone_utils import format_dd_mm_yyyy

logger = logging.getLogger('core')


def _user_profile(user):
    """Безопасно возвращает профиль пользователя или None."""
    if not getattr(user, 'is_authenticated', False):
        return None
    return getattr(user, 'profile', None)


def _is_employee(user):
    """Проверяет роль сотрудника."""
    profile = _user_profile(user)
    return bool(profile and profile.role == UserProfile.ROLE_EMPLOYEE and hasattr(user, 'employee'))


def _is_client(user):
    """Проверяет роль клиента."""
    profile = _user_profile(user)
    return bool(profile and profile.role == UserProfile.ROLE_CLIENT)


def _can_manage_property(user, prop):
    """Superuser управляет всеми объектами, сотрудник — только закреплёнными за ним."""
    if user.is_authenticated and user.is_superuser:
        return True
    if _is_employee(user):
        return prop.agents.filter(pk=user.employee.pk).exists()
    return False


def _sales_queryset_for_user(user):
    """Ограничивает сделки по роли: admin — все, employee — свои, client — свои покупки."""
    qs = Sale.objects.select_related('property', 'buyer', 'employee')
    if user.is_superuser:
        return qs
    if _is_employee(user):
        return qs.filter(employee=user.employee)
    buyer = getattr(user, 'buyer', None)
    if buyer:
        return qs.filter(buyer=buyer)
    return qs.none()


def _apply_search_sort(request, queryset, search_fields, default_sort='title', extra_allowed=None):
    """Применяет GET-поиск q и безопасную сортировку sort."""
    q = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', default_sort).strip() or default_sort
    if q:
        cond = Q()
        for field in search_fields:
            cond |= Q(**{f'{field}__icontains': q})
        queryset = queryset.filter(cond)

    allowed = {default_sort, f'-{default_sort}', 'title', '-title', 'price', '-price', 'published_at', '-published_at'}
    if extra_allowed:
        allowed.update(extra_allowed)
    if sort in allowed:
        queryset = queryset.order_by(sort)
    else:
        queryset = queryset.order_by(default_sort)
    return queryset


def _parse_decimal_param(request, name):
    """Безопасно читает decimal GET-параметр фильтра цены."""
    raw = request.GET.get(name, '').strip()
    if not raw:
        return None
    try:
        value = Decimal(raw)
        if value < 0:
            raise InvalidOperation
        return value
    except (InvalidOperation, ValueError):
        messages.error(request, f'Параметр {name} должен быть положительным числом.')
        return None


def home(request):
    """Главная: последняя опубликованная новость + внешние API."""
    if request.method == 'HEAD':
        return HttpResponse(status=200)
    latest = NewsArticle.objects.filter(is_published=True).order_by('-published_at').first()
    city = request.GET.get('city') or settings.DEFAULT_CITY_WEATHER
    widgets = fetch_home_widgets_parallel(
        city=city,
        user_name=request.user.username if request.user.is_authenticated else 'guest',
    )
    return render(request, 'core/home.html', {'latest_news': latest, 'widgets': widgets, 'weather_city': city})


def about(request):
    """О компании: CompanyInfo + привязанная CompanyHistory."""
    company = CompanyInfo.objects.first()
    history = company.history.all() if company else []
    return render(request, 'core/about.html', {'company': company, 'history': history})


def news_list(request):
    """Новости с картинками, поиском и сортировкой."""
    qs = NewsArticle.objects.filter(is_published=True).select_related('company')
    qs = _apply_search_sort(request, qs, ['title', 'summary'], '-published_at')
    return render(request, 'core/news_list.html', {'articles': qs})


def news_detail(request, pk):
    """Страница полной новости."""
    article = get_object_or_404(NewsArticle.objects.select_related('company'), pk=pk, is_published=True)
    return render(request, 'core/news_detail.html', {'article': article})


def faq_list(request):
    """Словарь терминов с поиском и сортировкой."""
    entries = _apply_search_sort(request, FAQEntry.objects.all(), ['question', 'answer'], 'question')
    return render(request, 'core/faq.html', {'entries': entries})


def contacts(request):
    """Контакты сотрудников с фото, поиском и сортировкой."""
    people = _apply_search_sort(
        request,
        ContactPerson.objects.all(),
        ['full_name', 'position', 'duties', 'email'],
        'full_name',
        extra_allowed={'position', '-position'},
    )
    return render(request, 'core/contacts.html', {'people': people})


def privacy(request):
    """Политика конфиденциальности."""
    return render(request, 'core/privacy.html')


def vacancies(request):
    """Вакансии с поиском и сортировкой."""
    items = _apply_search_sort(
        request,
        Vacancy.objects.filter(is_active=True),
        ['title', 'description'],
        'title',
        extra_allowed={'salary_from', '-salary_from'},
    )
    return render(request, 'core/vacancies.html', {'vacancies': items})


def reviews_list(request):
    """Отзывы: видны только одобренные; есть поиск/сортировка."""
    reviews = _apply_search_sort(
        request,
        Review.objects.filter(is_approved=True),
        ['author_name', 'text'],
        '-created_at_utc',
        extra_allowed={'rating', '-rating', 'author_name', '-author_name'},
    )
    return render(request, 'core/reviews.html', {'reviews': reviews})


@login_required
def review_create(request):
    """
    Добавляет отзыв авторизованного пользователя на модерацию.

    author_name не показывается в форме, потому что берётся из текущего пользователя.
    Важно: author_name и user устанавливаются ДО form.is_valid(), иначе ModelForm
    вызывает model.clean(), а поле author_name отсутствует в форме и возникает ошибка.
    """
    author_name = request.user.get_full_name() or request.user.username

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        form.instance.author_name = author_name
        form.instance.user = request.user
        form.instance.is_approved = False

        if form.is_valid():
            form.save()
            messages.success(request, 'Отзыв отправлен на модерацию.')
            return redirect('reviews')
    else:
        form = ReviewForm()

    return render(request, 'core/review_form.html', {'form': form})


def promos(request):
    """Промокоды и купоны с поиском/сортировкой."""
    qs = _apply_search_sort(
        request,
        PromoCode.objects.all(),
        ['code', 'description'],
        'code',
        extra_allowed={'discount_percent', '-discount_percent', 'valid_until', '-valid_until'},
    )
    active = qs.filter(is_archived=False)
    archived = qs.filter(is_archived=True)
    return render(request, 'core/promos.html', {'active': active, 'archived': archived})


def catalog(request):
    """Каталог для гостей/клиентов: фильтр по цене, категории, поиск и сортировка."""
    qs = Property.objects.filter(is_active=True).select_related('category').prefetch_related('gallery_images')
    cat = request.GET.get('category', '').strip()
    price_min = _parse_decimal_param(request, 'price_min')
    price_max = _parse_decimal_param(request, 'price_max')

    if cat:
        try:
            qs = qs.filter(category_id=int(cat))
        except ValueError:
            messages.error(request, 'Категория должна быть выбрана из списка.')
    if price_min is not None:
        qs = qs.filter(price__gte=price_min)
    if price_max is not None:
        qs = qs.filter(price__lte=price_max)

    qs = _apply_search_sort(request, qs, ['title', 'description', 'characteristics'], 'title')
    categories = Category.objects.all()
    return render(request, 'core/catalog.html', {'properties': qs, 'categories': categories})


def register_view(request):
    """Публичная регистрация создаёт только клиента; employee назначает админ."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Сигнал core.signals создаёт пустой профиль для любого нового User.
            # Здесь мы не создаём второй UserProfile, а заполняем уже созданный профиль.
            profile, _ = UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    'birth_date': form.cleaned_data['birth_date'],
                    'phone': form.cleaned_data['phone'],
                    'role': UserProfile.ROLE_CLIENT,
                    'timezone': form.cleaned_data['timezone'],
                },
            )
            request.session['user_timezone'] = profile.timezone
            Buyer.objects.create(
                user=user,
                full_name=user.username,
                email=user.email,
                phone=form.cleaned_data['phone'],
                birth_date=form.cleaned_data['birth_date'],
            )
            login(request, user)
            messages.success(request, 'Регистрация успешна. Вы зарегистрированы как клиент.')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'core/register.html', {'form': form})


@login_required
def dashboard(request):
    """Личный кабинет: admin видит всё, employee — свои сделки, client — покупки и промокоды."""
    ctx = {'user_timezone': getattr(request, 'user_timezone', 'UTC')}
    if request.user.is_superuser:
        ctx['sales'] = _sales_queryset_for_user(request.user)[:20]
        ctx['role_label'] = 'Администратор'
    elif _is_employee(request.user):
        ctx['sales'] = _sales_queryset_for_user(request.user)
        ctx['properties'] = request.user.employee.properties.filter(is_active=True)
        ctx['role_label'] = 'Сотрудник'
    else:
        buyer = getattr(request.user, 'buyer', None)
        ctx['purchases'] = Sale.objects.filter(buyer=buyer).select_related('property') if buyer else Sale.objects.none()
        ctx['promos'] = PromoCode.objects.filter(is_archived=False)[:5]
        ctx['role_label'] = 'Клиент'
    return render(request, 'core/dashboard.html', ctx)


@login_required
def profile_settings(request):
    """Смена таймзоны; создаёт профиль, если superuser создан через createsuperuser."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileSettingsForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            request.session['user_timezone'] = form.cleaned_data['timezone']
            messages.success(request, 'Профиль обновлён.')
            return redirect('dashboard')
    else:
        form = ProfileSettingsForm(instance=profile)
    return render(request, 'core/profile_settings.html', {'form': form})


def property_list(request):
    """
    Список объектов недвижимости.

    Важно для защиты:
    - гости и клиенты видят все объекты, включая проданные;
    - проданные объекты помечаются как «продан»;
    - купить можно только активный объект без Sale;
    - сотрудник может редактировать только свои объекты;
    - superuser может редактировать все объекты.
    """
    qs = (
        Property.objects
        .select_related('category')
        .prefetch_related('owners', 'agents', 'gallery_images')
        .annotate(has_sale=Exists(Sale.objects.filter(property=OuterRef('pk'))))
    )

    editable_ids = []
    if request.user.is_authenticated and request.user.is_superuser:
        editable_ids = list(qs.values_list('id', flat=True))
    elif _is_employee(request.user):
        editable_ids = list(qs.filter(agents=request.user.employee).values_list('id', flat=True))

    qs = _apply_search_sort(request, qs, ['title', 'description', 'characteristics'], 'title')

    return render(request, 'core/property_list.html', {
        'properties': qs,
        'can_create': request.user.is_authenticated and (
            request.user.is_superuser or _is_employee(request.user)
        ),
        'editable_property_ids': editable_ids,
    })


def property_detail(request, pk):
    """
    Детальная страница объекта.

    Проданный объект можно открыть и посмотреть, но купить его нельзя.
    Кнопка «Купить» показывается только клиенту, если объект активен и по нему нет Sale.
    """
    prop = get_object_or_404(
        Property.objects
        .select_related('category')
        .prefetch_related('agents', 'gallery_images'),
        pk=pk,
    )

    has_sale = Sale.objects.filter(property=prop).exists()

    stamps = {
        'utc': format_dd_mm_yyyy(prop.created_at_utc),
        'local': prop.created_at_local_text or format_dd_mm_yyyy(prop.created_at_local),
        'tz': prop.created_at_timezone,
    }

    return render(request, 'core/property_detail.html', {
        'property': prop,
        'stamps': stamps,
        'has_sale': has_sale,
        'can_edit': _can_manage_property(request.user, prop),
        'can_buy': (
            request.user.is_authenticated
            and _is_client(request.user)
            and prop.is_active
            and not has_sale
        ),
    })

def _save_property_gallery(request, prop):
    """
    Сохраняет 1–3 дополнительные картинки объекта недвижимости.

    Файлы приходят из frontend-формы через поле gallery_images.
    JavaScript не используется: браузер отправляет несколько файлов через input multiple.
    """
    images = request.FILES.getlist('gallery_images')
    if not images:
        return

    prop.gallery_images.all().delete()

    for index, image in enumerate(images[:3], start=1):
        PropertyImage.objects.create(
            property=prop,
            image=image,
            sort_order=index,
            caption=f'{prop.title}: фото {index}',
            is_main=index == 1,
        )


@employee_or_superuser
def property_create(request):
    """CREATE объекта недвижимости через форму на сайте."""
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            obj = form.save()
            if _is_employee(request.user):
                obj.agents.add(request.user.employee)
            _save_property_gallery(request, obj)
            messages.success(request, 'Объект создан.')
            return redirect('property_list')
    else:
        form = PropertyForm(user=request.user)
    return render(request, 'core/property_form.html', {'form': form, 'action': 'Создать'})


@employee_or_superuser
def property_update(request, pk):
    """UPDATE объекта; сотрудник может менять только закреплённый за ним объект."""
    prop = get_object_or_404(Property, pk=pk)
    if not _can_manage_property(request.user, prop):
        raise PermissionDenied
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=prop, user=request.user)
        if form.is_valid():
            obj = form.save()
            _save_property_gallery(request, obj)
            messages.success(request, 'Объект обновлён.')
            return redirect('property_detail', pk=pk)
    else:
        form = PropertyForm(instance=prop, user=request.user)
    return render(request, 'core/property_form.html', {'form': form, 'action': 'Сохранить'})


@employee_or_superuser
def property_delete(request, pk):
    """Soft delete: объект становится неактивным, чтобы не ломать Sale с PROTECT."""
    prop = get_object_or_404(Property, pk=pk)
    if not _can_manage_property(request.user, prop):
        raise PermissionDenied
    if request.method == 'POST':
        prop.is_active = False
        prop.save()
        messages.success(request, 'Объект скрыт из публичного каталога.')
        return redirect('property_list')
    return render(request, 'core/property_confirm_delete.html', {'property': prop})


@login_required
@require_http_methods(['GET', 'POST'])
def purchase_property(request, pk):
    """Клиентская покупка объекта: создаёт Sale и привязывает Buyer автоматически."""
    if not _is_client(request.user):
        raise PermissionDenied('Покупать недвижимость может только пользователь с ролью client.')
    prop = get_object_or_404(Property.objects.prefetch_related('agents'), pk=pk, is_active=True)
    if Sale.objects.filter(property=prop).exists():
        messages.error(request, 'Этот объект уже куплен.')
        return redirect('property_detail', pk=pk)

    if request.method == 'POST':
        form = PurchaseConfirmForm(request.POST)
        if form.is_valid():
            profile = request.user.profile
            buyer, _ = Buyer.objects.get_or_create(
                user=request.user,
                defaults={
                    'full_name': request.user.get_full_name() or request.user.username,
                    'email': request.user.email or f'{request.user.username}@example.com',
                    'phone': profile.phone,
                    'birth_date': profile.birth_date,
                },
            )
            employee = prop.agents.first() or Employee.objects.first()
            if employee is None:
                messages.error(request, 'Покупка невозможна: в системе нет сотрудника для сделки.')
                return redirect('property_detail', pk=pk)
            today = timezone.localdate()
            Sale.objects.create(
                property=prop,
                buyer=buyer,
                employee=employee,
                sale_date=today,
                contract_date=today,
                amount=prop.price,
            )
            prop.is_active = False
            prop.save()
            messages.success(request, 'Покупка оформлена. Сделка добавлена в ваш личный кабинет.')
            return redirect('dashboard')
    else:
        form = PurchaseConfirmForm()
    return render(request, 'core/purchase_confirm.html', {'form': form, 'property': prop})


@employee_or_superuser
def sale_list(request):
    """Список сделок с фронта: admin — все, employee — свои."""
    sales = _sales_queryset_for_user(request.user)
    sales = _apply_search_sort(
        request,
        sales,
        ['property__title', 'buyer__full_name', 'employee__full_name'],
        '-sale_date',
        extra_allowed={'amount', '-amount', 'sale_date', '-sale_date'},
    )
    return render(request, 'core/sale_list.html', {'sales': sales})


@employee_or_superuser
def sale_create(request):
    """CREATE сделки через frontend-форму для сотрудника/superuser."""
    if request.method == 'POST':
        form = SaleForm(request.POST, user=request.user)
        if form.is_valid():
            sale = form.save()
            sale.property.is_active = False
            sale.property.save()
            messages.success(request, 'Сделка создана.')
            return redirect('sale_list')
    else:
        form = SaleForm(user=request.user)
    return render(request, 'core/sale_form.html', {'form': form, 'action': 'Создать'})


@employee_or_superuser
def sale_update(request, pk):
    """UPDATE сделки; employee может менять только свою сделку."""
    sale = get_object_or_404(_sales_queryset_for_user(request.user), pk=pk)
    if request.method == 'POST':
        form = SaleForm(request.POST, instance=sale, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Сделка обновлена.')
            return redirect('sale_list')
    else:
        form = SaleForm(instance=sale, user=request.user)
    return render(request, 'core/sale_form.html', {'form': form, 'action': 'Сохранить'})


@employee_or_superuser
def sale_delete(request, pk):
    """DELETE сделки через frontend; после удаления объект можно снова активировать вручную."""
    sale = get_object_or_404(_sales_queryset_for_user(request.user), pk=pk)
    if request.method == 'POST':
        sale.delete()
        messages.success(request, 'Сделка удалена.')
        return redirect('sale_list')
    return render(request, 'core/sale_confirm_delete.html', {'sale': sale})


@employee_or_superuser
def statistics_view(request):
    """Статистика и графики; employee видит только свои сделки."""
    sales = _sales_queryset_for_user(request.user)
    if request.user.is_superuser:
        buyers = list(Buyer.objects.all())
        properties = Property.objects.all()
        suffix = 'admin'
    else:
        buyers = list(Buyer.objects.filter(purchases__employee=request.user.employee).distinct())
        properties = Property.objects.filter(agents=request.user.employee).distinct()
        suffix = f'user_{request.user.pk}'
    stats = sale_amount_stats(sales)
    ages = client_age_stats(buyers)
    popular = popular_category_by_count(properties)
    profit = profitable_category(sales)
    clients_alpha = sorted(buyers, key=lambda b: b.full_name)
    chart1 = chart_sales_by_category(sales, suffix=suffix)
    chart2 = chart_sales_timeline(sales, suffix=suffix)
    return render(request, 'core/statistics.html', {
        'stats': stats,
        'ages': ages,
        'popular': popular,
        'profit': profit,
        'clients_alpha': clients_alpha,
        'chart_category': chart1,
        'chart_timeline': chart2,
    })


@require_GET
def api_sales_json(request):
    """JSON API сделок: 401 для анонима, данные ограничены ролью пользователя."""
    if settings.API_REQUIRE_AUTH and not request.user.is_authenticated:
        return JsonResponse({'error': 'auth required'}, status=401)
    sales = _sales_queryset_for_user(request.user)
    if not request.user.is_superuser and not (_is_employee(request.user) or hasattr(request.user, 'buyer')):
        return JsonResponse({'error': 'forbidden'}, status=403)
    data = list(sales.values('id', 'amount', 'sale_date', 'property__title', 'buyer__full_name')[:50])
    for row in data:
        row['sale_date'] = row['sale_date'].isoformat() if row.get('sale_date') else None
        row['amount'] = float(row['amount']) if row.get('amount') is not None else None
    return JsonResponse({'sales': data})


def api_demo(request):
    """Отдельная страница демонстрации внешних API и их кэша."""
    city = request.GET.get('city', settings.DEFAULT_CITY_WEATHER).strip() or settings.DEFAULT_CITY_WEATHER
    name = request.GET.get('name', 'alex').strip() or 'alex'
    context = {
        'city': city,
        'name': name,
        'weather': fetch_weather(city),
        'agify': fetch_age_by_name(name),
        'cat_fact': fetch_cat_fact(),
    }
    return render(request, 'core/api_demo.html', context)


class RealtyLoginView(LoginView):
    """Страница авторизации."""
    template_name = 'core/login.html'


class RealtyLogoutView(LogoutView):
    """Выход из аккаунта; в Django 5 вызывается POST-формой."""
    next_page = 'home'
