from django.db import models


class DeleteMessage(models.Model):
    chat_id = models.BigIntegerField(verbose_name='Чат ID')
    message_id = models.CharField(max_length=200, verbose_name='Сообщение ID')

    def __str__(self):
        return f"{self.chat_id}"

    class Meta:
        verbose_name = 'Удаление сообщения'
        verbose_name_plural = 'Удаление сообщений'
        db_table = 'delete_message'


class Users(models.Model):
    GENDER = [
        ('Парень', 'Парень'),
        ('Девушка', 'Девушка'),
    ]
    CHOICE_SOCIAL = [
        ('Telegram', 'Telegram'),
        ('Instagram', 'Instagram'),
        ('Whatsapp', 'Whatsapp')
    ]
    STEP = [
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('999', '999')
    ]
    telegram_id = models.BigIntegerField(verbose_name='Телеграм ID')
    created_at_user = models.DateTimeField(null=True, blank=True, verbose_name='Дата регистрации пользователя')
    user_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='Имя пользователя',)
    telegram_login = models.CharField(max_length=100, null=True, blank=True, verbose_name='Телеграм логин')
    gender = models.CharField(max_length=50, choices=GENDER, blank=True, null=True, verbose_name='Пол')
    age = models.IntegerField(verbose_name='Возраст', blank=True, null=True)
    photo = models.ImageField(upload_to='img/', null=True, verbose_name='Фото без блюра')
    photo_blur = models.ImageField(upload_to='img_blur/', null=True, verbose_name='Фото с блюром')
    social = models.CharField(max_length=50, choices=CHOICE_SOCIAL, default='other')
    communication_method = models.CharField(max_length=100, blank=True, null=True, verbose_name='Способ связи')
    premium = models.BooleanField(verbose_name='Статус премиума', default=False)
    round = models.IntegerField(verbose_name='Раунды', default=0)
    all_rounds = models.IntegerField(verbose_name='Общее количество раундов', default=0)
    count = models.IntegerField(verbose_name='Количество баталий', default=0)
    count_skip = models.IntegerField(default=0, verbose_name='Количество пропусков')
    created_at_round = models.DateTimeField(blank=True, null=True, verbose_name='Дата и время запуска раунда')
    active_at = models.DateTimeField(blank=True, null=True, verbose_name='Активная команда')
    fake = models.BooleanField(verbose_name='Статус фейк-аккаунта', default=False)
    status = models.BooleanField(default=False, verbose_name='Статус блокировки фотки')
    status_full = models.BooleanField(default=False, verbose_name='Статус блокировки')
    notifications_true = models.BooleanField(default=False, verbose_name='Статус уведомления анкет')
    sign_up = models.DateTimeField(blank=True, null=True, verbose_name='Дата начала регистрации')
    push_fifteen_min = models.DateTimeField(blank=True, null=True, verbose_name='Дата количество лайков 15 минут')
    push_twenty_four_min = models.DateTimeField(blank=True, null=True, verbose_name='Дата количество лайков 24 часа')
    number_of_likes_fifteen_min = models.IntegerField(verbose_name='Количество лайков 15 минут', default=0)
    number_of_likes_twenty_four_min = models.IntegerField(verbose_name='Количество лайков 24 часа', default=0)
    sent_likes_fifteen_min = models.IntegerField(verbose_name='Отправлено лайков 15 минут', default=0)
    sent_likes_twenty_four_min = models.IntegerField(verbose_name='Отправлено лайков 24 часа', default=0)
    get_status = models.IntegerField(verbose_name='Получил лайков', default=0)
    send_status = models.IntegerField(verbose_name='Отправил лайков', default=0)
    win_round = models.IntegerField(verbose_name='Побед в раунде', default=0)
    boost = models.BooleanField(default=False, verbose_name='Буст')
    step = models.CharField(max_length=50, choices=STEP, default='0', verbose_name='Шаг')

    def __str__(self):
        return f'{self.id}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        db_table = 'users'


class SearchOptions(models.Model):
    GENDER = [
        ('Парень', 'Парень'),
        ('Девушка', 'Девушка'),
    ]
    user = models.ForeignKey(Users, related_name='search_user', blank=True, null=True, on_delete=models.CASCADE, verbose_name='Пользователь')
    gender = models.CharField(max_length=50, choices=GENDER, blank=True, null=True, verbose_name='Пол')
    from_age = models.IntegerField(verbose_name=' Возраст от')
    to_age = models.IntegerField(verbose_name='Возраст до')


    def __str__(self):
        return f"{self.gender}"

    class Meta:
        verbose_name = 'Параметр поиска'
        verbose_name_plural = 'Параметры поиска'
        db_table = 'search_options'


class Sympathy(models.Model):
    addressee = models.ForeignKey(Users, related_name='sympathy_addressee', blank=True, null=True, on_delete=models.CASCADE, verbose_name='Кого лайкнули')
    sender = models.ForeignKey(Users, related_name='sympathy_sender', blank=True, null=True, on_delete=models.CASCADE, verbose_name='Кто лайкнул')
    like_status = models.BooleanField(verbose_name='Статус лайка', default=False)
    round = models.IntegerField(verbose_name='раунд', default=0)
    like_date = models.DateTimeField(blank=True, null=True, verbose_name='Дата и время')

    def __str__(self):
        return f"{self.like_status}"

    class Meta:
        verbose_name = 'Симпатия'
        verbose_name_plural = 'Симпатии'
        db_table = 'sympathy'


class ActiveUser(models.Model):
    user = models.ForeignKey(Users, related_name='avtive_user', on_delete=models.CASCADE, verbose_name='Пользователь')
    created_at = models.DateField(verbose_name='Дата', blank=True, null=True)

    def __str__(self):
        return f"{self.user}"

    class Meta:
        verbose_name = 'Активность'
        verbose_name_plural = 'Активности'
        db_table = 'active_user'


class UniqueSympathy(models.Model):
    addressee = models.ForeignKey(Users, related_name='unique_sympathy_addressee', blank=True, null=True,
                                  on_delete=models.CASCADE, verbose_name='Кого лайкнули')
    sender = models.ForeignKey(Users, related_name='unique_sympathy_sender', blank=True, null=True, on_delete=models.CASCADE,
                               verbose_name='Кто лайкнул')
    choice_round = models.BooleanField(verbose_name='Выбор в раунде', default=False)
    like_status = models.BooleanField(verbose_name='Статус взаимного лайка', default=False)
    guest = models.BooleanField(default=False, verbose_name='Статус гостевого лайка')

    def __str__(self):
        return f"{self.addressee}"

    class Meta:
        verbose_name = 'Уникальная симпатия'
        verbose_name_plural = 'Уникальные симпатии'
        db_table = 'unique_sympathy'


class FakeLikes(models.Model):
    user = models.ForeignKey(Users, related_name='fake_user_likes', on_delete=models.CASCADE, verbose_name='Пользователь')
    fake = models.ForeignKey(Users, related_name='fake_fake_likes', on_delete=models.CASCADE, verbose_name='Пользователь')
    created_at = models.DateTimeField(verbose_name='Дата', blank=True, null=True)

    def __str__(self):
        return f"{self.user}"

    class Meta:
        verbose_name = 'Активность'
        verbose_name_plural = 'Активности'
        db_table = 'fake_likes'
