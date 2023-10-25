from rest_framework.validators import ValidationError


def check_unique_data(data):
    """Проверка данных (tags/ingredients) на уникальность."""
    unique_data = []
    for item in data:
        if item in unique_data:
            raise ValidationError({
                'error': 'Данные должно быть уникальны.'
            })
        unique_data.append(item)
    return data
