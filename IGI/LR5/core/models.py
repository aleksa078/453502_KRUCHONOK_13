"""
Модели предметной области: риэлтерское агентство, вариант 13.

Связи:
- OneToOneField: User-UserProfile, User-Buyer, User-Employee;
- ForeignKey: Property-Category, Sale-Property/Buyer/Employee;
- ManyToManyField: Property-Owner, Property-Employee.

Валидация выполняется и в формах, и в моделях. В save() вызывается full_clean(),
поэтому проверки работают не только через ModelForm, но и при программном создании
через objects.create().
"""
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from core.timezone_utils import current_timezone_name, local_stamp_text
from core.validators import validate_age_18_plus, validate_belarus_phone


def default_user_timezone():
    """Возвращает пользовательскую таймзону по умолчанию из settings."""
    return getattr(settings, 'DEFAULT_USER_TIMEZONE', 'Europe/Minsk')


def _not_blank(value, field_title):
    """Проверяет, что строковое поле не состоит только из пробелов."""
    if isinstance(value, str) and not value.strip():
        raise ValidationError({field_title: 'Поле не может быть пустым или состоять только из пробелов.'})


class ValidatedSaveMixin(models.Model):
    """Миксин: принудительно запускает model.clean()/validators перед save()."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Сохраняет объект только после full_clean(), кроме skip_validation=True."""
        skip_validation = kwargs.pop('skip_validation', False)
        if not skip_validation:
            self.full_clean()
        super().save(*args, **kwargs)


class TimeStampedMixin(ValidatedSaveMixin):
    """
    Миксин даты/времени.

    created_at_utc / updated_at_utc — aware datetime для БД.
    created_at_local_text / updated_at_local_text — строка локального времени пользователя,
    сохранённая в момент создания/изменения. Это нужно потому, что при USE_TZ=True Django
    физически хранит DateTimeField в UTC.
    """

    created_at_utc = models.DateTimeField(null=True, blank=True, editable=False)
    created_at_local = models.DateTimeField(null=True, blank=True, editable=False)
    created_at_timezone = models.CharField(max_length=64, blank=True, editable=False)
    created_at_local_text = models.CharField(max_length=64, blank=True, editable=False)
    updated_at_utc = models.DateTimeField(null=True, blank=True, editable=False)
    updated_at_local = models.DateTimeField(null=True, blank=True, editable=False)
    updated_at_timezone = models.CharField(max_length=64, blank=True, editable=False)
    updated_at_local_text = models.CharField(max_length=64, blank=True, editable=False)

    class Meta:
        abstract = True

    def _stamp_create_times(self):
        """Фиксирует UTC и локальную пользовательскую дату/время при создании."""
        now = timezone.now()
        tz_name = current_timezone_name()
        local_dt = timezone.localtime(now)
        self.created_at_utc = now
        self.created_at_local = local_dt
        self.created_at_timezone = tz_name
        self.created_at_local_text = local_stamp_text(now, tz_name)
        self.updated_at_utc = now
        self.updated_at_local = local_dt
        self.updated_at_timezone = tz_name
        self.updated_at_local_text = local_stamp_text(now, tz_name)

    def _stamp_update_times(self):
        """Фиксирует UTC и локальную пользовательскую дату/время при изменении."""
        now = timezone.now()
        tz_name = current_timezone_name()
        self.updated_at_utc = now
        self.updated_at_local = timezone.localtime(now)
        self.updated_at_timezone = tz_name
        self.updated_at_local_text = local_stamp_text(now, tz_name)

    def save(self, *args, **kwargs):
        """Перед сохранением валидирует объект и обновляет timestamp-поля."""
        skip_validation = kwargs.pop('skip_validation', False)
        if not skip_validation:
            self.full_clean()
        if self.pk is None or not self.created_at_utc or not self.created_at_local_text or not self.created_at_timezone:
            self._stamp_create_times()
            stamp_fields = {
                'created_at_utc', 'created_at_local', 'created_at_timezone', 'created_at_local_text',
                'updated_at_utc', 'updated_at_local', 'updated_at_timezone', 'updated_at_local_text',
            }
        else:
            self._stamp_update_times()
            stamp_fields = {
                'updated_at_utc', 'updated_at_local', 'updated_at_timezone', 'updated_at_local_text',
            }
        if kwargs.get('update_fields') is not None:
            kwargs['update_fields'] = set(kwargs['update_fields']) | stamp_fields
        super(ValidatedSaveMixin, self).save(*args, **kwargs)


class UserProfile(TimeStampedMixin):
    """Профиль пользователя: роль, телефон, дата рождения и IANA-таймзона."""

    ROLE_CLIENT = 'client'
    ROLE_EMPLOYEE = 'employee'
    ROLE_CHOICES = [
        (ROLE_CLIENT, 'Клиент'),
        (ROLE_EMPLOYEE, 'Сотрудник'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    timezone = models.CharField(max_length=64, default=default_user_timezone)
    birth_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=24, blank=True, validators=[validate_belarus_phone])
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default=ROLE_CLIENT)

    def clean(self):
        """
        Проверяет возраст 18+ и уникальность телефона профиля.

        Email проверяется в RegisterForm через стандартную модель User.
        Телефон хранится в UserProfile, поэтому уникальность телефона проверяется здесь.
        """
        super().clean()
        validate_age_18_plus(self.birth_date)

        if self.phone:
            duplicate = UserProfile.objects.exclude(pk=self.pk).filter(phone=self.phone).exists()
            if duplicate:
                raise ValidationError({'phone': 'Профиль с таким телефоном уже существует.'})

    def __str__(self):
        """Возвращает человекочитаемое имя профиля."""
        return f'Профиль {self.user.username}'


class Category(TimeStampedMixin):
    """Категория объектов недвижимости."""

    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def clean(self):
        """Запрещает пустое название категории."""
        _not_blank(self.name, 'name')

    def __str__(self):
        """Возвращает название категории."""
        return self.name


class Owner(TimeStampedMixin):
    """Владелец недвижимости."""

    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=24, validators=[validate_belarus_phone])
    birth_date = models.DateField()
    address = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name = 'Владелец'
        verbose_name_plural = 'Владельцы'

    def clean(self):
        """Проверяет ФИО и возраст владельца 18+."""
        _not_blank(self.full_name, 'full_name')
        validate_age_18_plus(self.birth_date)

    def __str__(self):
        """Возвращает ФИО владельца."""
        return self.full_name


class Property(TimeStampedMixin):
    """Объект недвижимости: цена, описание, категория, владельцы и агенты."""

    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    description = models.TextField()
    characteristics = models.TextField(help_text='Площадь, этаж, район и т.д.')
    image = models.ImageField(upload_to='properties/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='properties')
    owners = models.ManyToManyField(Owner, related_name='properties', blank=True)
    agents = models.ManyToManyField('Employee', related_name='properties', blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Объект недвижимости'
        verbose_name_plural = 'Объекты недвижимости'
        ordering = ['title']

    def clean(self):
        """Проверяет непустые строки и положительную цену."""
        _not_blank(self.title, 'title')
        _not_blank(self.description, 'description')
        _not_blank(self.characteristics, 'characteristics')
        if self.price is not None and self.price <= 0:
            raise ValidationError({'price': 'Цена должна быть больше 0.'})

    def __str__(self):
        """Возвращает название объекта."""
        return self.title


class PropertyImage(TimeStampedMixin):
    """Дополнительная картинка объекта недвижимости для галереи 1–3 фото."""

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='gallery_images',
        verbose_name='Объект недвижимости',
    )
    image = models.ImageField(upload_to='properties/gallery/', verbose_name='Картинка')
    caption = models.CharField(max_length=200, blank=True, verbose_name='Подпись')
    sort_order = models.PositiveSmallIntegerField(default=1, verbose_name='Порядок показа')
    is_main = models.BooleanField(default=False, verbose_name='Главная картинка')

    class Meta:
        verbose_name = 'Картинка объекта недвижимости'
        verbose_name_plural = 'Картинки объектов недвижимости'
        ordering = ['sort_order', 'id']
        unique_together = ('property', 'sort_order')

    def clean(self):
        """Проверяет наличие файла и корректный номер позиции в галерее."""
        super().clean()
        if not self.image:
            raise ValidationError({'image': 'Нужно выбрать картинку объекта недвижимости.'})
        if self.sort_order and not (1 <= self.sort_order <= 3):
            raise ValidationError({'sort_order': 'Для лабораторной работы используется от 1 до 3 фото на объект.'})

    def __str__(self):
        """Возвращает подпись картинки для админки."""
        title = self.property.title if self.property_id else 'объекта'
        return f'Фото {self.sort_order} для {title}'


class Buyer(TimeStampedMixin):
    """Покупатель / клиент агентства."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='buyer')
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=24, validators=[validate_belarus_phone])
    birth_date = models.DateField()
    address = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'

    def clean(self):
        """Проверяет ФИО, возраст клиента 18+, уникальность email и телефона."""
        errors = {}

        try:
            _not_blank(self.full_name, 'full_name')
        except ValidationError as exc:
            errors.update(exc.message_dict)

        try:
            validate_age_18_plus(self.birth_date)
        except ValidationError as exc:
            errors['birth_date'] = exc.messages

        if self.email:
            duplicate_email = Buyer.objects.exclude(pk=self.pk).filter(email__iexact=self.email).exists()
            if duplicate_email:
                errors['email'] = 'Покупатель с таким email уже существует.'

        if self.phone:
            duplicate_phone = Buyer.objects.exclude(pk=self.pk).filter(phone=self.phone).exists()
            if duplicate_phone:
                errors['phone'] = 'Покупатель с таким телефоном уже существует.'

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        """Возвращает ФИО клиента."""
        return self.full_name

    @property
    def age(self):
        """Рассчитывает возраст по дате рождения для статистики."""
        today = timezone.localdate()
        bd = self.birth_date
        return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))


class Employee(TimeStampedMixin):
    """Сотрудник компании, связанный с пользователем OneToOne."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
    full_name = models.CharField(max_length=200)
    department = models.CharField(max_length=100, default='Коммерческий отдел')
    phone = models.CharField(max_length=24, validators=[validate_belarus_phone])
    email = models.EmailField()
    birth_date = models.DateField()
    hire_date = models.DateField()

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def clean(self):
        """Проверяет ФИО и возраст сотрудника 18+."""
        _not_blank(self.full_name, 'full_name')
        validate_age_18_plus(self.birth_date)

    def __str__(self):
        """Возвращает ФИО сотрудника."""
        return self.full_name


class Sale(TimeStampedMixin):
    """Продажа: объект, клиент, сотрудник, дата продажи, дата договора и сумма."""

    property = models.ForeignKey(Property, on_delete=models.PROTECT, related_name='sales')
    buyer = models.ForeignKey(Buyer, on_delete=models.PROTECT, related_name='purchases')
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name='sales')
    sale_date = models.DateField()
    contract_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])

    class Meta:
        verbose_name = 'Продажа'
        verbose_name_plural = 'Продажи'

    def clean(self):
        """Проверяет положительную сумму и логичный порядок дат."""
        if self.amount is not None and self.amount <= 0:
            raise ValidationError({'amount': 'Сумма сделки должна быть больше 0.'})
        if self.contract_date and self.sale_date and self.contract_date > self.sale_date:
            raise ValidationError({'contract_date': 'Дата договора не может быть позже даты продажи.'})

    def __str__(self):
        """Возвращает краткое описание продажи."""
        return f'{self.property.title} — {self.buyer}'


class NewsArticle(TimeStampedMixin):
    """Новость сайта homeFULL: компания, заголовок, summary, картинка и полный текст."""

    company = models.ForeignKey(
        'CompanyInfo',
        on_delete=models.CASCADE,
        related_name='news',
        null=True,
        blank=True,
        verbose_name='Компания',
        help_text='Компания, к которой относится новость.',
    )
    title = models.CharField(max_length=200)
    summary = models.CharField(max_length=300, help_text='Одно предложение')
    image = models.ImageField(upload_to='news/', blank=True, null=True)
    full_text = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-published_at']

    def clean(self):
        """Проверяет заголовок и то, что summary выглядит как одно предложение."""
        _not_blank(self.title, 'title')
        _not_blank(self.summary, 'summary')
        sentence_marks = sum(self.summary.count(mark) for mark in '.!?')
        if sentence_marks > 1:
            raise ValidationError({'summary': 'Краткое содержание должно быть одним предложением.'})

    def __str__(self):
        """Возвращает заголовок новости."""
        return self.title


class CompanyInfo(TimeStampedMixin):
    """Страница «О компании»: текст, логотип, видео и реквизиты."""

    title = models.CharField(max_length=200, default='О компании')
    about_text = models.TextField()
    logo = models.ImageField(upload_to='company/', blank=True, null=True)
    video_url = models.URLField(blank=True)
    requisites = models.TextField(blank=True, help_text='Реквизиты организации')

    def clean(self):
        """Запрещает пустой текст о компании."""
        _not_blank(self.about_text, 'about_text')

    def __str__(self):
        """Возвращает заголовок страницы о компании."""
        return self.title


class CompanyHistory(TimeStampedMixin):
    """История компании по годам, привязанная к CompanyInfo."""

    year = models.PositiveIntegerField()
    event = models.TextField()
    company = models.ForeignKey(CompanyInfo, on_delete=models.CASCADE, related_name='history', null=True, blank=True)

    class Meta:
        ordering = ['year']
        unique_together = ('company', 'year')

    def clean(self):
        """Проверяет непустое описание события."""
        _not_blank(self.event, 'event')

    def __str__(self):
        """Возвращает год и начало события."""
        return f'{self.year}: {self.event[:50]}'


class FAQEntry(TimeStampedMixin):
    """Словарь терминов / FAQ."""

    question = models.CharField(max_length=300)
    answer = models.TextField()

    class Meta:
        verbose_name = 'FAQ'
        ordering = ['-created_at_utc']

    def clean(self):
        """Проверяет непустые вопрос и ответ."""
        _not_blank(self.question, 'question')
        _not_blank(self.answer, 'answer')

    def __str__(self):
        """Возвращает вопрос."""
        return self.question


class ContactPerson(TimeStampedMixin):
    """Контактное лицо: фото, должность, обязанности, телефон и email."""

    full_name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    duties = models.TextField()
    phone = models.CharField(max_length=24, validators=[validate_belarus_phone])
    email = models.EmailField()
    photo = models.ImageField(upload_to='contacts/', blank=True, null=True)

    def clean(self):
        """Проверяет непустые ФИО, должность и обязанности."""
        _not_blank(self.full_name, 'full_name')
        _not_blank(self.position, 'position')
        _not_blank(self.duties, 'duties')

    def __str__(self):
        """Возвращает ФИО контактного лица."""
        return self.full_name


class Vacancy(TimeStampedMixin):
    """Вакансия агентства."""

    title = models.CharField(max_length=200)
    description = models.TextField()
    salary_from = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.01)],
    )
    is_active = models.BooleanField(default=True)

    def clean(self):
        """Проверяет непустое название/описание и положительную зарплату."""
        _not_blank(self.title, 'title')
        _not_blank(self.description, 'description')
        if self.salary_from is not None and self.salary_from <= 0:
            raise ValidationError({'salary_from': 'Зарплата должна быть больше 0.'})

    def __str__(self):
        """Возвращает название вакансии."""
        return self.title


class Review(TimeStampedMixin):
    """Отзыв клиента: имя автора, оценка, текст и признак модерации."""

    author_name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = models.TextField()
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at_utc']

    def clean(self):
        """Проверяет автора и текст отзыва."""
        _not_blank(self.author_name, 'author_name')
        _not_blank(self.text, 'text')

    def __str__(self):
        """Возвращает автора и оценку."""
        return f'{self.author_name} ({self.rating})'


class PromoCode(TimeStampedMixin):
    """Промокод/купон: код, описание, скидка и архивный статус."""

    code = models.CharField(max_length=32, unique=True)
    description = models.TextField()
    discount_percent = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
    )
    is_archived = models.BooleanField(default=False)
    valid_until = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = 'Промокод'
        ordering = ['-is_archived', 'code']

    def clean(self):
        """Проверяет код, описание и диапазон скидки 1–100%."""
        _not_blank(self.code, 'code')
        _not_blank(self.description, 'description')
        if self.discount_percent and not (1 <= self.discount_percent <= 100):
            raise ValidationError({'discount_percent': 'Скидка должна быть от 1 до 100%.'})

    def __str__(self):
        """Возвращает код и статус."""
        status = 'архив' if self.is_archived else 'активен'
        return f'{self.code} ({status})'
