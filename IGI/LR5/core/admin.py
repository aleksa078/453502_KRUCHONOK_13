"""Админ-панель: модели, фильтры, поиск, inline и модерация отзывов."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from core.models import (
    Buyer,
    Category,
    CompanyHistory,
    CompanyInfo,
    ContactPerson,
    Employee,
    FAQEntry,
    NewsArticle,
    Owner,
    PromoCode,
    Property,
    PropertyImage,
    Review,
    Sale,
    UserProfile,
    Vacancy,
)


class UserProfileInline(admin.StackedInline):
    """Inline-профиль пользователя в стандартной модели User."""
    model = UserProfile
    can_delete = False
    extra = 0


class ExtendedUserAdmin(BaseUserAdmin):
    """Расширенный UserAdmin: показывает UserProfile внутри пользователя."""
    inlines = [UserProfileInline]


admin.site.unregister(User)
admin.site.register(User, ExtendedUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Отдельная страница профилей, чтобы админ мог назначать role/timezone."""
    list_display = ('user', 'role', 'timezone', 'phone', 'birth_date')
    list_filter = ('role', 'timezone')
    search_fields = ('user__username', 'phone')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админка категорий."""
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    """Админка владельцев."""
    list_display = ('full_name', 'phone', 'email')
    search_fields = ('full_name', 'email')


class PropertyImageInline(admin.TabularInline):
    """Inline-галерея 1–3 фото внутри объекта недвижимости."""
    model = PropertyImage
    extra = 3
    max_num = 3


class SaleInline(admin.TabularInline):
    """Inline-сделки внутри объекта недвижимости."""
    model = Sale
    extra = 0


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    """Админка объектов недвижимости с inline-галереей и inline-сделками."""
    list_display = ('title', 'category', 'price', 'is_active', 'created_at_utc')
    list_filter = ('category', 'is_active')
    search_fields = ('title', 'description')
    filter_horizontal = ('owners', 'agents')
    inlines = [PropertyImageInline, SaleInline]


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    """Отдельная админка фотографий объектов недвижимости."""
    list_display = ('property', 'caption', 'sort_order', 'is_main')
    list_filter = ('is_main', 'property__category')
    search_fields = ('property__title', 'caption')


@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    """Админка покупателей."""
    list_display = ('full_name', 'phone', 'email', 'birth_date')
    search_fields = ('full_name', 'email')


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Админка сотрудников."""
    list_display = ('full_name', 'department', 'email')
    list_filter = ('department',)
    search_fields = ('full_name', 'email')


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    """Админка продаж/сделок."""
    list_display = ('property', 'buyer', 'employee', 'amount', 'sale_date', 'contract_date')
    list_filter = ('sale_date', 'employee')
    date_hierarchy = 'sale_date'
    search_fields = ('property__title', 'buyer__full_name', 'employee__full_name')


@admin.register(NewsArticle)
class NewsAdmin(admin.ModelAdmin):
    """Админка новостей."""
    list_display = ('title', 'company', 'published_at', 'is_published')
    list_filter = ('company', 'is_published')
    search_fields = ('title', 'summary')


class HistoryInline(admin.TabularInline):
    """Inline истории компании внутри CompanyInfo."""
    model = CompanyHistory
    extra = 1


@admin.register(CompanyInfo)
class CompanyAdmin(admin.ModelAdmin):
    """Админка страницы «О компании» с историей по годам."""
    inlines = [HistoryInline]
    list_display = ('title',)


@admin.register(CompanyHistory)
class CompanyHistoryAdmin(admin.ModelAdmin):
    """Отдельная страница истории компании."""
    list_display = ('company', 'year', 'event')
    list_filter = ('company', 'year')


@admin.register(FAQEntry)
class FAQAdmin(admin.ModelAdmin):
    """Админка словаря терминов."""
    list_display = ('question', 'created_at_utc', 'created_at_local_text')
    search_fields = ('question', 'answer')


@admin.register(ContactPerson)
class ContactAdmin(admin.ModelAdmin):
    """Админка контактов."""
    list_display = ('full_name', 'position', 'phone')
    search_fields = ('full_name', 'position', 'email')


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    """Админка вакансий."""
    list_display = ('title', 'is_active', 'salary_from')
    list_filter = ('is_active',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Админка отзывов с action для модерации."""
    list_display = ('author_name', 'rating', 'is_approved', 'created_at_utc')
    list_filter = ('is_approved', 'rating')
    search_fields = ('author_name', 'text')
    actions = ['approve_reviews']

    @admin.action(description='Одобрить выбранные отзывы')
    def approve_reviews(self, request, queryset):
        """Помечает выбранные отзывы как одобренные для показа на сайте."""
        queryset.update(is_approved=True)


@admin.register(PromoCode)
class PromoAdmin(admin.ModelAdmin):
    """Админка промокодов и купонов."""
    list_display = ('code', 'discount_percent', 'is_archived', 'valid_until')
    list_filter = ('is_archived',)
    search_fields = ('code', 'description')
