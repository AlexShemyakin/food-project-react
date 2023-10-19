import csv

from django.http import HttpResponse


def download_csv(data):
    """
    Преобразует данные из словаря в csv формат
    и возвращает HttpResponse класс для отправки клиенту.
    """
    response = HttpResponse(content_type='text/csv')
    response.write(u'\ufeff'.encode('utf8'))
    

    field_name = data[0].keys()
    writer = csv.DictWriter(response, field_name)
    for ingredient in data:
        writer.writerow(ingredient)
    response['Content-Disposition'] = (
        'attachment; filename="shopping_list.csv"'
    )
    return response
