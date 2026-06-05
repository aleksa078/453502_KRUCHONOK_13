"""Формы сайта: серверная и HTML5-валидация без JavaScript."""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Q

from core.models import Buyer, Category, Employee, Owner, Property, Review, Sale, UserProfile
from core.timezone_utils import valid_timezone_choices
from core.validators import validate_age_18_plus, validate_belarus_phone

PHONE_PATTERN = r'^\+375 \((29|33|44|25)\) [0-9]{3}-[0-9]{2}-[0-9]{2}$'


class MultipleFileInput(forms.ClearableFileInput):
    """HTML-input, который разрешает выбрать несколько файлов."""

    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    """Поле формы для списка изображений, полученных из input multiple."""

    widget = MultipleFileInput

    def clean(self, data, initial=None):
        """Проверяет, что каждый загруженный файл является изображением."""
        single_file_clean = super().clean
        if data in self.empty_values:
            return []
        if isinstance(data, (list, tuple)):
            return [single_file_clean(item, initial) for item in data]
        return [single_file_clean(data, initial)]


class RegisterForm(UserCreationForm):
    """Публичная регистрация только клиента; роль employee здесь недоступна."""

    email = forms.EmailField(required=True)
    birth_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'required': True}),
        help_text='Возраст 18+',
    )
    phone = forms.CharField(
        max_length=24,
        validators=[validate_belarus_phone],
        widget=forms.TextInput(attrs={
            'required': True,
            'placeholder': '+375 (29) 123-45-67',
            'pattern': PHONE_PATTERN,
            'title': 'Формат: +375 (29) 123-45-67',
        }),
        help_text='Формат: +375 (29) 123-45-67',
    )
    timezone = forms.ChoiceField(
        label='Часовой пояс',
        choices=valid_timezone_choices(limit_to_europe=True),
        initial='Europe/Minsk',
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        """Запрещает создать несколько аккаунтов с одним email."""
        email = (self.cleaned_data.get('email') or '').strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже зарегистрирован.')

        if Buyer.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Покупатель с таким email уже есть в базе.')

        return email

    def clean_phone(self):
        """Запрещает создать несколько аккаунтов с одним телефоном."""
        phone = (self.cleaned_data.get('phone') or '').strip()

        if UserProfile.objects.filter(phone=phone).exists():
            raise forms.ValidationError('Пользователь с таким телефоном уже зарегистрирован.')

        if Buyer.objects.filter(phone=phone).exists():
            raise forms.ValidationError('Покупатель с таким телефоном уже есть в базе.')

        return phone

    def clean_birth_date(self):
        """Проверяет возраст 18+ на уровне формы."""
        bd = self.cleaned_data['birth_date']
        validate_age_18_plus(bd)
        return bd


class ProfileSettingsForm(forms.ModelForm):
    """Настройки профиля: телефон, дата рождения и незахардкоженная таймзона."""

    timezone = forms.ChoiceField(choices=valid_timezone_choices(limit_to_europe=True))

    class Meta:
        model = UserProfile
        fields = ('phone', 'birth_date', 'timezone')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'phone': forms.TextInput(attrs={'pattern': PHONE_PATTERN}),
        }

    def clean_birth_date(self):
        """Проверяет возраст 18+, если дата рождения заполнена."""
        bd = self.cleaned_data.get('birth_date')
        if bd:
            validate_age_18_plus(bd)
        return bd


class PropertyForm(forms.ModelForm):
    """CRUD-форма объектов недвижимости с фронта и загрузка 1–3 фото галереи."""

    gallery_images = MultipleImageField(
        required=False,
        label='Фотографии галереи',
        help_text='Можно выбрать от 1 до 3 дополнительных фото объекта. JavaScript не используется.',
    )

    class Meta:
        model = Property
        fields = [
            'title', 'price', 'description', 'characteristics',
            'image', 'category', 'owners', 'is_active',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'required': True, 'minlength': 2}),
            'price': forms.NumberInput(attrs={'required': True, 'min': '0.01', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'rows': 4, 'required': True, 'minlength': 5}),
            'characteristics': forms.Textarea(attrs={'rows': 3, 'required': True, 'minlength': 3}),
            'owners': forms.SelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        """Superuser может назначать агентов, сотрудник назначается автоматически во view."""
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user and self.user.is_superuser:
            self.fields['agents'] = forms.ModelMultipleChoiceField(
                queryset=Employee.objects.all(),
                required=False,
                widget=forms.SelectMultiple(),
                label='Агенты',
            )
            if self.instance.pk:
                self.fields['agents'].initial = self.instance.agents.all()

    def clean_gallery_images(self):
        """Разрешает загрузить не больше трёх изображений галереи."""
        images = self.cleaned_data.get('gallery_images') or []
        if len(images) > 3:
            raise forms.ValidationError('Можно загрузить максимум 3 фотографии объекта.')
        return images

    def save(self, commit=True):
        """Сохраняет объект и, для superuser, выбранных агентов."""
        obj = super().save(commit=commit)
        if commit and 'agents' in self.fields:
            obj.agents.set(self.cleaned_data.get('agents'))
        return obj


class SaleForm(forms.ModelForm):
    """CRUD-форма сделок для сотрудника/superuser."""

    class Meta:
        model = Sale
        fields = ('property', 'buyer', 'employee', 'sale_date', 'contract_date', 'amount')
        widgets = {
            'sale_date': forms.DateInput(attrs={'type': 'date', 'required': True}),
            'contract_date': forms.DateInput(attrs={'type': 'date', 'required': True}),
            'amount': forms.NumberInput(attrs={'min': '0.01', 'step': '0.01', 'required': True}),
        }

    def __init__(self, *args, **kwargs):
        """
        Ограничивает выбор в форме сделки.

        Superuser видит все объекты, покупателей и сотрудников.
        Сотрудник видит только себя, свои объекты и подходящих покупателей.
        QuerySet покупателей строится через один filter(Q(...) | Q(...)),
        а не через объединение queryset1 | queryset2, чтобы не было ошибки
        "Cannot combine a unique query with a non-unique query".
        """
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user and not self.user.is_superuser and hasattr(self.user, 'employee'):
            employee = self.user.employee

            self.fields['employee'].queryset = Employee.objects.filter(pk=employee.pk)
            self.fields['employee'].initial = employee

            self.fields['property'].queryset = (
                Property.objects
                .filter(agents=employee)
                .distinct()
            )

            self.fields['buyer'].queryset = (
                Buyer.objects
                .filter(
                    Q(purchases__employee=employee)
                    | Q(purchases__isnull=True)
                )
                .distinct()
            )

    def clean_employee(self):
        """Гарантирует, что сотрудник не подменит себя в POST-данных."""
        if self.user and not self.user.is_superuser and hasattr(self.user, 'employee'):
            return self.user.employee
        return self.cleaned_data['employee']


class PurchaseConfirmForm(forms.Form):
    """Пустая форма подтверждения покупки объекта клиентом."""

    confirm = forms.BooleanField(
        required=True,
        label='Подтверждаю покупку выбранного объекта недвижимости',
    )


class CategoryForm(forms.ModelForm):
    """Форма категории для справочного CRUD."""

    class Meta:
        model = Category
        fields = ('name', 'description')


class OwnerForm(forms.ModelForm):
    """Форма владельца для справочного CRUD."""

    class Meta:
        model = Owner
        fields = ('full_name', 'email', 'phone', 'birth_date', 'address')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'phone': forms.TextInput(attrs={'pattern': PHONE_PATTERN}),
        }


class BuyerForm(forms.ModelForm):
    """Форма покупателя для справочного CRUD."""

    class Meta:
        model = Buyer
        fields = ('user', 'full_name', 'email', 'phone', 'birth_date', 'address')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'phone': forms.TextInput(attrs={'pattern': PHONE_PATTERN}),
        }


class EmployeeForm(forms.ModelForm):
    """Форма сотрудника для назначения роли через закрытый интерфейс/админку."""

    class Meta:
        model = Employee
        fields = ('user', 'full_name', 'department', 'phone', 'email', 'birth_date', 'hire_date')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
            'phone': forms.TextInput(attrs={'pattern': PHONE_PATTERN}),
        }


class ReviewForm(forms.ModelForm):
    """Форма отзыва; сохраняет отзыв на модерацию."""

    class Meta:
        model = Review
        fields = ('rating', 'text')
        widgets = {
            'rating': forms.Select(choices=[(i, str(i)) for i in range(1, 6)]),
            'text': forms.Textarea(attrs={'rows': 4, 'required': True, 'minlength': 3}),
        }
