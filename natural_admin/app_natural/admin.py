import os
import requests
import xlsxwriter
from django.contrib import admin
from django.http import FileResponse
from django.utils.safestring import mark_safe
from .models import Users, SearchOptions, Sympathy, ActiveUser, UniqueSympathy, DeleteMessage
from import_export.admin import ExportMixin


# Register your models here.


class UsersAdmin(ExportMixin, admin.ModelAdmin):
    list_display = [
        'id', 'telegram_id', 'boost', 'step', 'created_at_user', 'user_name', 'telegram_login', 'gender', 'age', 'get_image', 'photo_blur', 'communication_method',
        'premium', 'round', 'active_at', 'fake', 'all_rounds', 'status', 'status_full', 'get_status', 'send_status', 'win_round', 'count_skip'
    ]
    list_display_links = [
        'id', 'telegram_id', 'step', 'created_at_user', 'user_name', 'telegram_login', 'gender', 'age', 'get_image', 'photo_blur',
        'communication_method', 'premium', 'round',  'active_at', 'fake', 'all_rounds', 'get_status', 'send_status', 'win_round', 'count_skip'
    ]
    readonly_fields = ['status', 'status_full', 'get_image']
    fields = ['telegram_id', 'created_at_user', 'user_name', 'telegram_login', 'gender', 'age', ('photo', 'get_image'), 'photo_blur', 'communication_method',
              'premium', 'round', 'count', 'created_at_round', 'active_at', 'fake', 'all_rounds', 'status', 'status_full']
    actions = ['push_blocked', 'push_blocked_full']
    list_editable = ['boost']
    list_per_page = 1000
    save_on_top = True

    def get_image(self, obj):
        if obj.photo:
            return mark_safe(f'<img src={obj.photo.url} width="140" height="140"')
        else:
            return None

    get_image.short_description = 'Фото без блюра'

    def push_blocked(self, request, queryset):
        url = 'https://api.telegram.org/bot5314127646:AAGv0k5Tu3dnNmfDTT1u8Po8lbsS83hV2ZY/sendMessage'
        for elem in queryset:
            try:
                data = {
                    'chat_id': elem.telegram_id,
                    'text': 'Ваша анкета заблокирована. Причина: Загрузите фотографию где отчетливо видно ваше лицо и нет недопустимого содержания.',
                    'parse_mode': 'HTML'
                }
                if elem.status == False:
                    elem.status = True
                    elem.save()
                    response = requests.get(url, data=data)
                    DeleteMessage(chat_id=elem.telegram_id, message_id=str(response.json()['result']['message_id'])).save()
            except Exception:
                pass

    push_blocked.short_description = 'Статус блокировки фотки'

    def push_blocked_full(self, request, queryset):
        url = 'https://api.telegram.org/bot5314127646:AAGv0k5Tu3dnNmfDTT1u8Po8lbsS83hV2ZY/sendMessage'
        for elem in queryset:
            try:
                data = {
                    'chat_id': elem.telegram_id,
                    'text': 'Ваша анкета заблокирована.',
                    'parse_mode': 'HTML'
                }
                if elem.status_full is False:
                    elem.status_full = True
                    elem.save()
                    response = requests.get(url, data=data)
                    DeleteMessage(chat_id=elem.telegram_id, message_id=str(response)).save()
            except Exception:
                pass

    push_blocked_full.short_description = 'Статус блокировки'


class SearchOptionsAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ['id', 'gender', 'from_age', 'to_age', 'user']
    list_display_links = ['id', 'gender', 'from_age', 'to_age', 'user']


class SympathyAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ['id', 'addressee', 'sender', 'like_status', 'round', 'like_date']
    list_display_links = ['id', 'round', 'addressee', 'sender', 'like_status', 'like_date']
    actions = ['download_excel']

    def download_excel(self, request, queryset):
        workbook = xlsxwriter.Workbook('user_statistics.xlsx', options={"remove_timezone": True})
        worksheet = workbook.add_worksheet()
        sympathy = Sympathy.objects.filter(like_status=True)
        if len(sympathy) > 0:
            work_dict = dict()
            header_list = ['ID пользователя', 'Количество лайков', 'Пол', 'Возраст', 'Принадлежность']
            for sym in sympathy:
                if work_dict.get(sym.addressee.id, None):
                    work_dict[sym.addressee.id][0] += 1
                else:
                    work_dict[sym.addressee.id] = [
                        1,
                        sym.addressee.gender if sym.addressee.gender is not None else 'Не установлен',
                        sym.addressee.age if sym.addressee.age is not None else 'Не установлен'
                    ]
            for y in range(len(header_list)):
                worksheet.write(0, y, header_list[y])
            if len(work_dict) > 0:
                for index, key in enumerate(work_dict):
                    if work_dict[key][2] != 'Не установлен':
                        if 18 <= work_dict[key][2] <= 20:
                            i = '18 - 20'
                        elif 21 <= work_dict[key][2] <= 24:
                            i = '21 - 24'
                        elif 25 <= work_dict[key][2] <= 29:
                            i = '25 - 29'
                        elif 30 <= work_dict[key][2] <= 35:
                            i = '30 - 35'
                        elif 36 <= work_dict[key][2] <= 40:
                            i = '36 - 40'
                        else:
                            i = '40 и Старше'
                    else:
                        i = 'Не установлен'
                    worksheet.write(index + 1, 0, key)
                    worksheet.write(index + 1, 1, work_dict[key][0])
                    worksheet.write(index + 1, 2, work_dict[key][1])
                    worksheet.write(index + 1, 3, work_dict[key][2])
                    worksheet.write(index + 1, 4, i)
        workbook.close()
        response = FileResponse(open(f'user_statistics.xlsx', 'rb'))
        os.remove(f'user_statistics.xlsx')
        return response

    download_excel.short_description = 'Выгрузка лайков'


class ActiveUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at']
    list_display_links = ['id', 'user', 'created_at']


class UniqueSympathyAdmin(admin.ModelAdmin):
    list_display = ['id', 'addressee', 'sender', 'choice_round', 'like_status']
    list_display_links = ['id', 'like_status', 'addressee', 'sender', 'choice_round']


admin.site.register(Users, UsersAdmin)
admin.site.register(SearchOptions, SearchOptionsAdmin)
admin.site.register(Sympathy, SympathyAdmin)
admin.site.register(ActiveUser, ActiveUserAdmin)
admin.site.register(UniqueSympathy, UniqueSympathyAdmin)

admin.site.site_header = 'NATURAL'
admin.site.site_title = 'NATURAL'
