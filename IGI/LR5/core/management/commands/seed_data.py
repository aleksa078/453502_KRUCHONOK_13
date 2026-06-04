"""
Наполнение БД демонстрационными данными.

Безопасность:
- известные demo-пароли и demo-admin НЕ создаются по умолчанию;
- для локальной защиты используйте флаги:
  python manage.py seed_data --with-demo-users --with-demo-admin
"""
from datetime import date, timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.timezone_utils import activate_user_timezone
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


def _media_rel_if_exists(relative_path):
    """Возвращает путь для ImageField только если файл реально есть в MEDIA_ROOT."""
    path = settings.MEDIA_ROOT / relative_path
    return relative_path if path.exists() else ''


class Command(BaseCommand):
    """Management command для создания 10+ демо-записей."""

    help = 'Создаёт демо-данные для ЛР5.'

    def add_arguments(self, parser):
        """Добавляет безопасные флаги создания demo-пользователей и demo-admin."""
        parser.add_argument('--with-demo-users', action='store_true', help='Создать клиентов/сотрудников с demo-паролями')
        parser.add_argument('--with-demo-admin', action='store_true', help='Создать admin/admin12345 только локально')

    def handle(self, *args, **options):
        """Запускает наполнение БД и активирует demo-таймзону для timestamp-полей."""
        activate_user_timezone(settings.DEFAULT_USER_TIMEZONE)
        self._categories()
        self._owners()
        self._properties()
        if options['with_demo_users']:
            self._users_buyers_employees(with_demo_admin=options['with_demo_admin'])
            self._sales()
        self._content_pages()
        self.stdout.write(self.style.SUCCESS('seed_data: готово'))

    def _categories(self):
        """Создаёт категории недвижимости."""
        names = [
            'Квартиры', 'Дома', 'Коммерция', 'Земля', 'Новостройки',
            'Вторичка', 'Аренда', 'Элит', 'Студии', 'Коттеджи', 'Таунхаусы',
        ]
        for n in names:
            Category.objects.get_or_create(name=n, defaults={'description': f'Категория {n}'})

    def _owners(self):
        """Создаёт 10 владельцев недвижимости."""
        for i in range(1, 11):
            Owner.objects.get_or_create(
                full_name=f'Владелец {i}',
                defaults={
                    'email': f'owner{i}@example.com',
                    'phone': f'+375 (29) {100+i:03d}-{40+i:02d}-{50+i:02d}',
                    'birth_date': date(1975 + i, 3, 15),
                    'address': f'г. Минск, ул. {i}',
                },
            )

    def _properties(self):
        """
        Создаёт 5 домов и 5 квартир; к каждому объекту добавляет от 1 до 3 фото.

        Специально для защиты:
        - Дом 2 остаётся непроданным в категории «Дома»;
        - Дом 5 остаётся непроданным в категории «Коттеджи»;
        - Квартира 2 относится к категории «Студии»;
        - Квартира 4 относится к категории «Аренда»;
        - часть объектов будет продана в _sales(), часть останется доступной для покупки.
        """
        categories = {c.name: c for c in Category.objects.all()}
        owners = list(Owner.objects.all())

        objects = [
            {
                'old_title': 'Объект недвижимости 1',
                'title': 'Дом 1',
                'category': categories.get('Дома') or Category.objects.first(),
                'price': Decimal('148000'),
                'description': 'Дом 1 от homeFULL: просторный жилой дом с участком, гаражом и коммуникациями.',
                'characteristics': '122 м², участок 7 соток, парковка, газ, вода',
                'prefix': 'house_01',
            },
            {
                'old_title': 'Объект недвижимости 2',
                'title': 'Дом 2',
                'category': categories.get('Дома') or Category.objects.first(),
                'price': Decimal('166000'),
                'description': 'Дом 2 от homeFULL: непроданный дом для семейного проживания в спокойном районе.',
                'characteristics': '134 м², участок 8 соток, парковка, терраса',
                'prefix': 'house_02',
            },
            {
                'old_title': 'Объект недвижимости 3',
                'title': 'Дом 3',
                'category': categories.get('Дома') or Category.objects.first(),
                'price': Decimal('184000'),
                'description': 'Дом 3 от homeFULL: современный дом с готовым ремонтом и благоустроенным участком.',
                'characteristics': '146 м², участок 9 соток, гараж, сад',
                'prefix': 'house_03',
            },
            {
                'old_title': 'Объект недвижимости 4',
                'title': 'Дом 4',
                'category': categories.get('Дома') or Category.objects.first(),
                'price': Decimal('202000'),
                'description': 'Дом 4 от homeFULL: большой дом для семьи с несколькими спальнями.',
                'characteristics': '158 м², участок 10 соток, 4 спальни, парковка',
                'prefix': 'house_04',
            },
            {
                'old_title': 'Объект недвижимости 5',
                'title': 'Дом 5',
                'category': categories.get('Коттеджи') or categories.get('Дома') or Category.objects.first(),
                'price': Decimal('220000'),
                'description': 'Дом 5 от homeFULL: непроданный коттедж повышенного комфорта рядом с лесом.',
                'characteristics': '170 м², участок 11 соток, камин, терраса',
                'prefix': 'house_05',
            },
            {
                'old_title': 'Объект недвижимости 6',
                'title': 'Квартира 1',
                'category': categories.get('Квартиры') or Category.objects.first(),
                'price': Decimal('74500'),
                'description': 'Квартира 1 от homeFULL: удобная квартира для покупки и проживания.',
                'characteristics': '50 м², 2 комнаты, этаж 2, развитая инфраструктура',
                'prefix': 'apartment_01',
            },
            {
                'old_title': 'Объект недвижимости 7',
                'title': 'Квартира 2',
                'category': categories.get('Студии') or categories.get('Квартиры') or Category.objects.first(),
                'price': Decimal('84000'),
                'description': 'Квартира 2 от homeFULL: студия для одного человека, пары или инвестиционной покупки.',
                'characteristics': '58 м², студия, этаж 3, рядом метро',
                'prefix': 'apartment_02',
            },
            {
                'old_title': 'Объект недвижимости 8',
                'title': 'Квартира 3',
                'category': categories.get('Квартиры') or Category.objects.first(),
                'price': Decimal('93500'),
                'description': 'Квартира 3 от homeFULL: квартира с хорошей планировкой в жилом районе.',
                'characteristics': '66 м², 2 комнаты, этаж 4, лоджия',
                'prefix': 'apartment_03',
            },
            {
                'old_title': 'Объект недвижимости 9',
                'title': 'Квартира 4',
                'category': categories.get('Аренда') or categories.get('Квартиры') or Category.objects.first(),
                'price': Decimal('103000'),
                'description': 'Квартира 4 от homeFULL: объект в категории аренды, доступный для покупки клиентом.',
                'characteristics': '74 м², 3 комнаты, этаж 5, удобная транспортная доступность',
                'prefix': 'apartment_04',
            },
            {
                'old_title': 'Объект недвижимости 10',
                'title': 'Квартира 5',
                'category': categories.get('Квартиры') or Category.objects.first(),
                'price': Decimal('112500'),
                'description': 'Квартира 5 от homeFULL: просторная квартира для семьи.',
                'characteristics': '82 м², 3 комнаты, этаж 6, парковка рядом',
                'prefix': 'apartment_05',
            },
        ]

        for data in objects:
            cover_path = _media_rel_if_exists(f'properties/{data["prefix"]}_01.jpg')

            prop = Property.objects.filter(title=data['title']).first()
            if prop is None:
                prop = Property.objects.filter(title=data['old_title']).first()

            defaults = {
                'title': data['title'],
                'price': data['price'],
                'description': data['description'],
                'characteristics': data['characteristics'],
                'category': data['category'],
                'is_active': True,
                'image': cover_path,
            }

            if prop is None:
                prop = Property.objects.create(**defaults)
            else:
                for field, value in defaults.items():
                    setattr(prop, field, value)
                prop.save()

            prop.owners.set(owners[: min(3, len(owners))])

            used_orders = []
            for photo_num in range(1, 4):
                image_path = _media_rel_if_exists(f'properties/{data["prefix"]}_{photo_num:02d}.jpg')
                if image_path:
                    PropertyImage.objects.update_or_create(
                        property=prop,
                        sort_order=photo_num,
                        defaults={
                            'image': image_path,
                            'caption': f'{data["title"]}: фото {photo_num}',
                            'is_main': photo_num == 1,
                        },
                    )
                    used_orders.append(photo_num)

            prop.gallery_images.exclude(sort_order__in=used_orders).delete()

    def _users_buyers_employees(self, with_demo_admin=False):
        """Создаёт demo-клиентов и сотрудников только для локальной демонстрации."""
        if with_demo_admin and not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@realty.by', 'admin12345')
        admin = User.objects.filter(username='admin').first()
        if admin:
            UserProfile.objects.update_or_create(
                user=admin,
                defaults={
                    'role': UserProfile.ROLE_EMPLOYEE,
                    'timezone': 'Europe/Minsk',
                    'birth_date': date(1990, 1, 1),
                    'phone': '+375 (29) 111-11-11',
                },
            )

        for i in range(1, 11):
            uname = f'client{i}'
            u, created = User.objects.get_or_create(username=uname, defaults={'email': f'{uname}@mail.by'})
            if created:
                u.set_password('client12345')
                u.save()
            UserProfile.objects.update_or_create(
                user=u,
                defaults={
                    'role': UserProfile.ROLE_CLIENT,
                    'timezone': 'Europe/Minsk',
                    'birth_date': date(1995, 5, i),
                    'phone': f'+375 (33) {200+i:03d}-{10+i:02d}-{20+i:02d}',
                },
            )
            Buyer.objects.update_or_create(
                user=u,
                defaults={
                    'full_name': f'Клиент {i}',
                    'email': f'{uname}@mail.by',
                    'phone': f'+375 (33) {200+i:03d}-{10+i:02d}-{20+i:02d}',
                    'birth_date': date(1995, 5, i),
                },
            )

        for i in range(1, 4):
            uname = f'employee{i}'
            u, created = User.objects.get_or_create(username=uname, defaults={'email': f'{uname}@realty.by'})
            if created:
                u.set_password('employee12345')
                u.save()
            UserProfile.objects.update_or_create(
                user=u,
                defaults={
                    'role': UserProfile.ROLE_EMPLOYEE,
                    'timezone': 'Europe/Minsk',
                    'birth_date': date(1988, 8, i),
                    'phone': f'+375 (44) {300+i:03d}-{10+i:02d}-{20+i:02d}',
                },
            )
            Employee.objects.update_or_create(
                user=u,
                defaults={
                    'full_name': f'Сотрудник {i}',
                    'email': f'{uname}@realty.by',
                    'phone': f'+375 (44) {300+i:03d}-{10+i:02d}-{20+i:02d}',
                    'birth_date': date(1988, 8, i),
                    'hire_date': date(2015 + i, 1, 1),
                },
            )

        employees = list(Employee.objects.order_by('id'))
        for index, prop in enumerate(Property.objects.order_by('title')):
            prop.agents.clear()
            if employees:
                prop.agents.add(employees[index % len(employees)])

    def _sales(self):
        """
        Создаёт демонстрационные продажи.

        Важно для защиты:
        - 5 объектов уже проданы и используются для статистики;
        - 5 объектов остаются активными и доступны клиенту для покупки;
        - это позволяет показать и статистику Sale, и клиентский сценарий покупки.
        """
        buyers = list(Buyer.objects.order_by('id'))
        employees = list(Employee.objects.order_by('id'))

        if not employees or not buyers:
            return

        sold_titles = [
            'Дом 1',
            'Дом 3',
            'Дом 4',
            'Квартира 1',
            'Квартира 3',
        ]

        active_titles = [
            'Дом 2',
            'Дом 5',
            'Квартира 2',
            'Квартира 4',
            'Квартира 5',
        ]

        # Удаляем только устаревшие demo-продажи по объектам, которые теперь
        # должны быть активными. Это нужно, если seed_data запускали раньше,
        # когда Квартира 5 ошибочно создавалась как проданная.
        Sale.objects.filter(
            property__title__in=active_titles,
            buyer__full_name__startswith='Клиент ',
        ).delete()

        for i, title in enumerate(sold_titles):
            prop = Property.objects.filter(title=title).first()

            if not prop:
                continue

            sale, _ = Sale.objects.update_or_create(
                property=prop,
                defaults={
                    'buyer': buyers[i % len(buyers)],
                    'employee': employees[i % len(employees)],
                    'sale_date': date.today() - timedelta(days=i * 12),
                    'contract_date': date.today() - timedelta(days=i * 12 + 2),
                    'amount': prop.price,
                },
            )

            prop.is_active = False
            prop.save(update_fields=['is_active'])

        Property.objects.filter(title__in=active_titles).update(is_active=True)

    def _content_pages(self):
        """Создаёт страницы сайта, новости, контакты, вакансии, отзывы и промокоды."""
        logo = _media_rel_if_exists('company/logo.png')

        company, _ = CompanyInfo.objects.update_or_create(
            pk=1,
            defaults={
                'title': 'homeFULL',
                'about_text': (
                    'homeFULL — риэлтерское агентство полного цикла, которое помогает клиентам '
                    'покупать, продавать и подбирать квартиры, дома и коммерческую недвижимость.'
                ),
                'requisites': 'ООО «homeFULL», УНП 123456789, г. Минск, пр-т Независимости, 100',
                'logo': logo,
            },
        )

        for y in range(2015, 2025):
            CompanyHistory.objects.update_or_create(
                company=company,
                year=y,
                defaults={'event': f'Событие {y} года'},
            )

        homefull_news = [
            {
                'title': 'homeFULL открыл новый офис консультаций для покупателей недвижимости',
                'summary': 'Компания homeFULL открыла новый офис для консультаций клиентов по покупке квартир, домов и коммерческих помещений.',
                'full_text': (
                    'Риэлтерское агентство homeFULL открыло новый офис консультаций для покупателей недвижимости. '
                    'В офисе клиенты могут получить помощь с подбором объекта, проверкой документов, расчётом бюджета и подготовкой к сделке. '
                    'Особое внимание уделяется первичной консультации: специалист уточняет цель покупки, район, бюджет, сроки и дополнительные требования. '
                    'Такой формат помогает быстрее подобрать подходящие варианты и снизить риск ошибок при покупке недвижимости.'
                ),
                'image': 'news/news_01.jpg',
            },
            {
                'title': 'homeFULL обновил каталог квартир в Минске и пригороде',
                'summary': 'В каталоге homeFULL появились новые квартиры в Минске и ближайшем пригороде с фильтрацией по цене и категории.',
                'full_text': (
                    'Компания homeFULL обновила каталог квартир и добавила новые объекты в разных районах Минска и пригородных локациях. '
                    'Покупатели могут сравнивать предложения по цене, площади, количеству комнат, району и состоянию объекта. '
                    'Обновление каталога помогает клиентам быстрее находить подходящие варианты и видеть актуальные предложения на рынке. '
                    'Сотрудники агентства сопровождают клиента от первичного просмотра до заключения договора.'
                ),
                'image': 'news/news_02.jpg',
            },
            {
                'title': 'Эксперты homeFULL рассказали, как безопасно купить дом',
                'summary': 'Специалисты homeFULL подготовили рекомендации для покупателей частных домов и коттеджей.',
                'full_text': (
                    'Эксперты homeFULL подготовили рекомендации для покупателей частных домов. '
                    'Перед сделкой важно проверить документы на земельный участок, техническое состояние дома, инженерные коммуникации и историю владения. '
                    'Также специалисты советуют заранее оценить транспортную доступность, инфраструктуру района и расходы на обслуживание объекта. '
                    'Комплексная проверка помогает покупателю принимать решение на основе фактов, а не только внешнего вида дома.'
                ),
                'image': 'news/news_03.jpg',
            },
            {
                'title': 'homeFULL запустил услугу оценки рыночной стоимости недвижимости',
                'summary': 'Клиенты homeFULL могут заказать предварительную оценку стоимости квартиры, дома или коммерческого помещения.',
                'full_text': (
                    'homeFULL запустил услугу предварительной оценки рыночной стоимости недвижимости. '
                    'Специалисты анализируют район, площадь, состояние объекта, инфраструктуру, похожие предложения и динамику спроса. '
                    'Оценка помогает продавцам определить реалистичную цену, а покупателям понять, соответствует ли объект рыночным условиям. '
                    'Услуга особенно полезна перед публикацией объявления или началом переговоров по сделке.'
                ),
                'image': 'news/news_04.jpg',
            },
            {
                'title': 'homeFULL расширил базу домов для семейного проживания',
                'summary': 'В базе homeFULL появились новые дома для семей, которым важны участок, парковка и спокойный район.',
                'full_text': (
                    'homeFULL расширил базу домов для семейного проживания. '
                    'В подборку вошли дома с участками, парковочными местами, просторными кухнями-гостиными и удобным расположением относительно школ и магазинов. '
                    'Сотрудники агентства помогают клиентам сравнить варианты по площади, состоянию коммуникаций, стоимости обслуживания и перспективам района. '
                    'Такой подход делает выбор загородного или пригородного жилья более понятным и безопасным.'
                ),
                'image': 'news/news_05.jpg',
            },
            {
                'title': 'homeFULL подготовил памятку для первой покупки квартиры',
                'summary': 'Компания homeFULL опубликовала памятку для клиентов, которые впервые покупают квартиру.',
                'full_text': (
                    'Компания homeFULL подготовила памятку для клиентов, которые впервые покупают квартиру. '
                    'В памятке описаны основные этапы: определение бюджета, выбор района, проверка объекта, подготовка документов и заключение договора. '
                    'Отдельный раздел посвящён вопросам, которые стоит задать продавцу перед внесением аванса. '
                    'Памятка помогает новичкам ориентироваться в процессе покупки и понимать, какие действия выполняет агентство.'
                ),
                'image': 'news/news_06.jpg',
            },
            {
                'title': 'homeFULL усилил направление коммерческой недвижимости',
                'summary': 'Агентство homeFULL добавило больше предложений по офисам, торговым помещениям и объектам для бизнеса.',
                'full_text': (
                    'homeFULL усилил направление коммерческой недвижимости и добавил больше предложений для предпринимателей. '
                    'В базе появились офисы, торговые помещения, небольшие склады и объекты под сферу услуг. '
                    'При подборе коммерческого объекта специалисты учитывают поток клиентов, транспортную доступность, планировку, стоимость аренды или покупки и юридические ограничения. '
                    'Это направление помогает бизнесу находить помещения под реальные задачи, а не просто выбирать объект по площади.'
                ),
                'image': 'news/news_07.jpg',
            },
            {
                'title': 'homeFULL внедрил проверку объектов перед публикацией на сайте',
                'summary': 'Перед размещением в каталоге объекты homeFULL проходят базовую проверку данных и документов.',
                'full_text': (
                    'homeFULL внедрил дополнительную проверку объектов перед публикацией на сайте. '
                    'Сотрудники проверяют корректность адреса, характеристики, цену, наличие фотографий и основные документы по объекту. '
                    'Такая проверка помогает поддерживать актуальность каталога и снижает вероятность ошибок в описании недвижимости. '
                    'Для клиентов это означает более прозрачный и удобный выбор объектов.'
                ),
                'image': 'news/news_08.jpg',
            },
            {
                'title': 'homeFULL рассказал о спросе на квартиры возле метро',
                'summary': 'Аналитики homeFULL отметили устойчивый интерес покупателей к квартирам рядом с метро и крупными транспортными узлами.',
                'full_text': (
                    'Аналитики homeFULL отметили устойчивый интерес покупателей к квартирам рядом с метро и крупными транспортными узлами. '
                    'Такие объекты часто выбирают клиенты, которым важны быстрые поездки на работу, доступность магазинов и развитая городская инфраструктура. '
                    'При этом специалисты советуют оценивать не только расстояние до метро, но и состояние дома, уровень шума, парковку и перспективы района. '
                    'Комплексный анализ помогает не переплатить за локацию и выбрать действительно удобное жильё.'
                ),
                'image': 'news/news_09.jpg',
            },
            {
                'title': 'homeFULL запустил сезонную подборку объектов с промокодами',
                'summary': 'Клиенты homeFULL могут посмотреть сезонную подборку объектов и актуальные промокоды на услуги агентства.',
                'full_text': (
                    'homeFULL запустил сезонную подборку объектов недвижимости с актуальными промокодами на услуги агентства. '
                    'В подборку вошли квартиры, дома и коммерческие помещения, по которым доступны специальные условия сопровождения. '
                    'Промокоды помогают клиентам снизить расходы на отдельные услуги и быстрее принять решение о начале сделки. '
                    'Актуальные предложения отображаются на странице промокодов и купонов сайта.'
                ),
                'image': 'news/news_10.jpg',
            },
        ]

        for i, news in enumerate(homefull_news, start=1):
            news_image = _media_rel_if_exists(news['image'])
            NewsArticle.objects.update_or_create(
                title=news['title'],
                defaults={
                    'company': company,
                    'summary': news['summary'],
                    'full_text': news['full_text'],
                    'is_published': True,
                    'published_at': timezone.now() - timedelta(days=i),
                    'image': news_image,
                },
            )

        contacts = [
            ('Алексей Иванов', 'Старший риэлтор', 'contacts/contact_01.jpg'),
            ('Анна Смирнова', 'Риэлтор по жилой недвижимости', 'contacts/contact_02.jpg'),
            ('Дмитрий Ковалёв', 'Специалист по продажам', 'contacts/contact_03.jpg'),
            ('Мария Петрова', 'Консультант по сделкам', 'contacts/contact_04.jpg'),
            ('Сергей Морозов', 'Агент по недвижимости', 'contacts/contact_05.jpg'),
            ('Елена Соколова', 'Менеджер по клиентам', 'contacts/contact_06.jpg'),
            ('Павел Орлов', 'Эксперт по коммерческой недвижимости', 'contacts/contact_07.jpg'),
            ('Ольга Васильева', 'Специалист по ипотечным сделкам', 'contacts/contact_08.jpg'),
            ('Андрей Новиков', 'Риэлтор-консультант', 'contacts/contact_09.jpg'),
            ('Наталья Белова', 'Менеджер отдела продаж', 'contacts/contact_10.jpg'),
        ]

        for i, (full_name, position, photo_path) in enumerate(contacts, start=1):
            contact_photo = _media_rel_if_exists(photo_path)
            ContactPerson.objects.update_or_create(
                full_name=full_name,
                defaults={
                    'position': position,
                    'duties': 'Консультации клиентов, подбор объектов недвижимости, сопровождение сделок.',
                    'phone': f'+375 (25) {400+i:03d}-{10+i:02d}-{20+i:02d}',
                    'email': f'manager{i}@realty.by',
                    'photo': contact_photo,
                },
            )

        faq_items = [
            (
                'Что такое эскроу-счёт?',
                'Эскроу-счёт — это специальный счёт, на котором деньги покупателя хранятся до выполнения условий сделки.',
            ),
            (
                'Как проходит покупка квартиры через агентство?',
                'Покупатель выбирает объект, проверяет документы, подписывает договор, оплачивает сделку и регистрирует право собственности.',
            ),
            (
                'Какие документы нужны для покупки недвижимости?',
                'Обычно нужны паспорт покупателя, договор, документы на объект недвижимости и подтверждение оплаты.',
            ),
            (
                'Чем отличается квартира от студии?',
                'Студия — это квартира без отдельной кухни, где жилая зона и кухонная зона объединены в одном пространстве.',
            ),
            (
                'Что такое договор купли-продажи?',
                'Договор купли-продажи — это документ, который фиксирует передачу недвижимости от продавца покупателю.',
            ),
            (
                'Что проверяет риэлтер перед сделкой?',
                'Риэлтер проверяет документы, собственников, характеристики объекта, историю владения и возможные ограничения.',
            ),
            (
                'Что такое задаток при покупке недвижимости?',
                'Задаток — это сумма, которую покупатель передаёт продавцу как подтверждение намерения заключить сделку.',
            ),
            (
                'Можно ли купить недвижимость в ипотеку?',
                'Да, недвижимость можно купить в ипотеку, если банк одобрит кредит и объект соответствует требованиям банка.',
            ),
            (
                'Что значит объект продан?',
                'Объект продан, если по нему уже оформлена сделка Sale и он больше недоступен для повторной покупки.',
            ),
            (
                'Что такое рыночная стоимость недвижимости?',
                'Рыночная стоимость — это ориентировочная цена объекта, по которой его можно продать с учётом района, состояния и спроса.',
            ),
        ]

        vacancies = [
            (
                'Риэлтор по жилой недвижимости',
                'Консультация клиентов, подбор квартир и домов, организация просмотров и сопровождение сделки.',
                Decimal('1800'),
            ),
            (
                'Специалист по коммерческой недвижимости',
                'Работа с офисами, торговыми помещениями и объектами для бизнеса.',
                Decimal('2200'),
            ),
            (
                'Менеджер по работе с клиентами',
                'Приём заявок, первичная консультация покупателей и передача клиентов специалистам.',
                Decimal('1600'),
            ),
            (
                'Агент по продаже домов и коттеджей',
                'Подбор загородной недвижимости, выезды на объекты, переговоры с владельцами.',
                Decimal('2100'),
            ),
            (
                'Специалист по проверке документов',
                'Проверка правоустанавливающих документов, подготовка информации для безопасной сделки.',
                Decimal('2300'),
            ),
            (
                'Оценщик недвижимости',
                'Анализ рынка, подготовка предварительной оценки стоимости квартир, домов и коммерческих объектов.',
                Decimal('2400'),
            ),
            (
                'Ассистент риэлтора',
                'Подготовка карточек объектов, загрузка фотографий, работа с базой данных и расписанием просмотров.',
                Decimal('1400'),
            ),
            (
                'Контент-менеджер каталога недвижимости',
                'Обновление описаний объектов, проверка фотографий и публикация новостей компании homeFULL.',
                Decimal('1500'),
            ),
            (
                'Специалист по сопровождению сделок',
                'Координация этапов сделки, связь с клиентами, сотрудниками и партнёрами.',
                Decimal('2000'),
            ),
            (
                'Администратор офиса homeFULL',
                'Встреча клиентов, обработка звонков, ведение расписания консультаций и офисной документации.',
                Decimal('1300'),
            ),
        ]

        for question, answer in faq_items:
            FAQEntry.objects.update_or_create(
                question=question,
                defaults={'answer': answer},
            )

        for title, description, salary in vacancies:
            Vacancy.objects.update_or_create(
                title=title,
                defaults={
                    'description': description,
                    'salary_from': salary,
                    'is_active': True,
                },
            )

        for i in range(1, 11):
            Review.objects.update_or_create(
                author_name=f'Автор {i}',
                defaults={
                    'rating': (i % 5) + 1,
                    'text': f'Отзыв номер {i}',
                    'is_approved': True,
                },
            )

            PromoCode.objects.update_or_create(
                code=f'PROMO{i:02d}',
                defaults={
                    'description': f'Скидка {i}%',
                    'discount_percent': min(i + 3, 25),
                    'is_archived': i > 7,
                },
            )