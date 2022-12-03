import os

from api import PetFriends
from settings import valid_email, valid_password, invalid_email, invalid_password

pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этот ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='Боевой', animal_type='кенгуру',
                                     age='3', pet_photo='images/Kenguru_2.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_successful_update_self_pet_info(name='Поняшка-няшка', animal_type='Лошадка', age=1):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


def test_add_pets_with_valid_data_without_photo(name='Пони_Без_Фото', animal_type='Лошадка', age=1):
    """Проверяем возможность добавления нового питомца без фотo"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    assert status == 200
    assert result['name'] == name


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Пони", "лошадь", "2", "images/Poni_number_1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_add_photo_at_pet(pet_photo='images/Poni_number_1.jpg'):
    """Проверяем возможность добавления новой фотографии питомца"""
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    _, api_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(api_key, 'my_pets')

    if len(my_pets['pets']) > 0:
        status, result = pf.add_photo_of_pet(api_key, my_pets['pets'][0]['id'], pet_photo)

        _, my_pets = pf.get_list_of_pets(api_key, 'my_pets')

        assert status == 200
        assert result['pet_photo'] == my_pets['pets'][0]['pet_photo']
    else:
        raise Exception("Питомцы отсутствуют")


def test_add_pet_negative_age_number(name='Прыгун', animal_type='ken-guru', age='-8', pet_photo='images/Kenguru_2.jpg'):
    """Проверка с негативным сценарием. Добавление питомца с отрицательным числом в переменной age.
    Тест не будет пройден если питомец будет добавлен на сайт с отрицательным числом в поле возраст.
     """
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    _, api_key = pf.get_api_key(valid_email, valid_password)
    _, result = pf.add_new_pet(api_key, name, animal_type, age, pet_photo)

    assert age not in result['age'], 'Питомец добавлен на сайт с отрицательным числом в поле возраст'


def test_add_pet_with_four_digit_age_number(name='', animal_type='Лошадка', age='3589', pet_photo='images/Poni_2.jpg'):
    """Проверка с негативным сценарием. Добавление питомца с числом более трех знаков в переменной age.
    Тест не будет пройден если питомец будет добавлен на сайт с числом превышающим три знака в поле возраст."""
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    _, api_key = pf.get_api_key(valid_email, valid_password)
    _, result = pf.add_new_pet(api_key, name, animal_type, age, pet_photo)
    number = result['age']

    assert len(number) < 4, 'Питомец добавлен на сайт с числом превышающим 3 знака в поле возраст'


def test_add_pet_with_empty_value_in_var_name(name='', animal_type='Лошадка', age='3', pet_photo='images/Poni_2.jpg'):
    """Проверяем возможность добавления питомца с пустым значением в переменной name
    Тест не будет пройден если питомец будет добавлен на сайт с пустым значением в поле "имя\""""
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    _, api_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(api_key, name, animal_type, age, pet_photo)
    assert status == 200
    assert result['name'] != '', 'Питомец добавлен на сайт с пустым значением в имени'


def test_add_pet_with_a_lot_of_words_in_variable_name(animal_type='cat', age='2', pet_photo='images/Poni_2.jpg'):
    """Проверка с негативным сценарием. Добавления питомца имя которого превышает 10 слов
    Тест не будет пройден если питомец будет добавлен на сайт с именем состоящим из более 10 слов"""

    name = "Барсик Тобик Мурзиков Коала Прыгун Шустрик Домовой Рандомный Фартовый Игривый Ленивый Прыгун"

    _, api_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(api_key, name, animal_type, age, pet_photo)

    list_name = result['name'].split()
    word_count = len(list_name)

    assert status == 200
    assert word_count < 10, 'Питомец добавлен с именем больше 10 слов'


def test_add_pet_with_special_characters_in_variable_animal_type(name='Мачо', age='5', pet_photo='images/Poni_2.jpg'):
    """Проверка с негативным сценарием. Добавление питомца со специальными символами вместо букв в переменной
     animal_type.
    Тест не будет пройден если питомец будет добавлен на сайт со спец. символами вместо букв в поле порода.
    """
    animal_type = 'Лошадка%@%2№'
    symbols = '@#%$$~*&^%$#+_-*&'
    symbol = []

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    _, api_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(api_key, name, animal_type, age, pet_photo)

    assert status == 200
    for i in symbols:
        if i in result['animal_type']:
            symbol.append(i)
    assert symbol[0] not in result['animal_type'], 'Питомец добавлен с недопустимыми спец.символами'


def test_add_pet_with_numbers_in_variable_animal_type(name='Мачо', animal_type='131313', age='7',
                                                      pet_photo='images/Poni_2.jpg'):
    """Проверка с негативным сценарием. Добавление питомца с цифрами вместо букв в переменной animal_type.
    Тест не будет пройден если питомец будет добавлен на сайт с цифрами вместо букв в поле порода."""
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    _, api_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(api_key, name, animal_type, age, pet_photo)

    assert status == 200
    assert animal_type not in result['animal_type'], 'Питомец добавлен на сайт с цифрами вместо букв в поле порода'


def test_add_pet_with_a_lot_of_words_in_var_animal_type(name='Сизиф', age='2', pet_photo='images/Poni_tyagatch.jpg'):
    """Проверка с негативным сценарием. Добавления питомца название породы которого превышает 10 слов
    Тест не будет пройден если питомец будет добавлен на сайт с названием породы состоящим из более 10 слов"""

    animal_type = 'Я маленькая лошадка и мне живётся несладко мне трудно нести мою ношу  настанет день и я её брошу'

    _, api_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(api_key, name, animal_type, age, pet_photo)

    list_animal_type = result['animal_type'].split()
    word_count = len(list_animal_type)

    assert status == 200
    assert word_count < 10, 'Питомец добавлен с названием породы больше 10 слов'


def test_get_api_key_with_wrong_password_and_correct_mail(email=valid_email, password=invalid_password):
    """Проверяем запрос с валидным емайлом и невалидным паролем.
    Проверяем нет ли ключа в ответе"""
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'key' not in result


def test_get_api_key_with_wrong_email_and_correct_password(email=invalid_email, password=valid_password):
    """Проверяем запрос с валидным паролем и с невалидным емaйлом.
    Проверяем нет ли ключа в ответе"""
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'key' not in result


def test_get_api_key_with_wrong_email_and_wrong_password(email=invalid_email, password=invalid_password):
    """Проверяем запрос с невалидным паролем и с невалидным емaйлом.
    Проверяем нет ли ключа в ответе"""
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'key' not in result
