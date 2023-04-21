from datetime import datetime
from peewee import *
from settings.settings import DATABASE, USER, PASSWORD, HOST, PORT

db = PostgresqlDatabase(database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT, autorollback=True)


class BaseModel(Model):
    id = PrimaryKeyField(unique=True)

    class Meta:
        database = db


class DeleteMessage(BaseModel):
    chat_id = BigIntegerField()
    message_id = CharField(max_length=200)

    class Meta:
        db_table = 'delete_message'


class Users(BaseModel):
    telegram_id = BigIntegerField(null=True)
    created_at_user = DateTimeField(null=True)
    user_name = CharField(max_length=100, null=True)
    telegram_login = CharField(max_length=100, null=True)
    gender = CharField(max_length=50, null=True)
    age = IntegerField(verbose_name='Возраст', null=True)
    photo = CharField(max_length=500, null=True)
    photo_blur = CharField(max_length=500, null=True)
    social = CharField(max_length=50, default='other')
    communication_method = CharField(max_length=100, null=True)
    premium = BooleanField(default=False)
    round = IntegerField(default=0)
    count = IntegerField(default=0)
    count_skip = IntegerField(default=0)
    created_at_round = DateTimeField(null=True)
    active_at = DateTimeField(null=True)
    fake = BooleanField(default=False)
    all_rounds = IntegerField(default=0)
    status = BooleanField(default=False)
    status_full = BooleanField(default=False)
    notifications_true = BooleanField(default=False)
    sign_up = DateTimeField(null=True)
    push_fifteen_min = DateTimeField(null=True)
    push_twenty_four_min = DateTimeField(null=True)
    number_of_likes_fifteen_min = IntegerField(default=0)
    number_of_likes_twenty_four_min = IntegerField(default=0)
    sent_likes_fifteen_min = IntegerField(default=0)
    sent_likes_twenty_four_min = IntegerField(default=0)
    get_status = IntegerField(default=0)
    send_status = IntegerField(default=0)
    win_round = IntegerField(default=0)
    boost = BooleanField(default=False)
    step = CharField(max_length=50, default='0')

    class Meta:
        db_table = 'users'


class SearchOptions(BaseModel):
    user = ForeignKeyField(Users, related_name='search_user', null=True, on_delete='CASCADE')
    gender = CharField(max_length=50, null=True)
    from_age = IntegerField()
    to_age = IntegerField()

    class Meta:
        db_table = 'search_options'


class Sympathy(BaseModel):
    addressee = ForeignKeyField(Users, related_name='sympathy_addressee', null=True, on_delete='CASCADE')
    sender = ForeignKeyField(Users, related_name='sympathy_sender',  null=True, on_delete='CASCADE')
    like_status = BooleanField(default=False)
    round = IntegerField(default=0)
    like_date = DateTimeField(null=True)

    class Meta:
        db_table = 'sympathy'


class ActiveUser(BaseModel):
    user = ForeignKeyField(Users, related_name='avtive_user', on_delete='CASCADE')
    created_at = DateTimeField()

    class Meta:
        db_table = 'active_user'


class UniqueSympathy(BaseModel):
    addressee = ForeignKeyField(Users, related_name='sympathy_addressee', null=True, on_delete='CASCADE')
    sender = ForeignKeyField(Users, related_name='sympathy_sender', null=True, on_delete='CASCADE')
    choice_round = BooleanField(verbose_name='Выбор в раунде', default=False)
    like_status = BooleanField(verbose_name='Статус взаимного лайка', default=False)
    guest = BooleanField(default=False)

    class Meta:
        db_table = 'unique_sympathy'


class FakeLikes(BaseModel):
    user = ForeignKeyField(Users, related_name='fake_user_likes', on_delete='CASCADE')
    fake = ForeignKeyField(Users, related_name='fake_fake_likes', on_delete='CASCADE')
    created_at = DateTimeField(null=True)

    class Meta:
        db_table = 'fake_likes'
