# py1cORM

`py1cORM` — небольшая типизированная ORM для чтения данных из стандартного
OData-интерфейса 1С. Библиотека описывает сущности 1С Python-моделями, строит
OData-параметры (`$select`, `$expand`, `$filter`, `$orderby`, `$top`, `$skip`) и
преобразует JSON-ответы в объекты с типизированными полями.

> Проект находится в beta-стадии. Текущий API ориентирован на чтение коллекций;
> создание, изменение и удаление объектов пока не реализованы.

## Возможности

- декларативные модели и псевдонимы полей 1С;
- обычные, вложенные и связанные поля (`Field`, `Embedded`, `ForeignKey`);
- типизированное преобразование значений, включая UUID и даты;
- выбор отдельных полей и раскрытие связей;
- фильтры через Python-выражения или raw OData;
- `contains`, `startswith`, `endswith`, `like`, `in`;
- сортировка, пагинация и последовательная загрузка батчами;
- настраиваемая пауза между batch-запросами;
- контроль незагруженных полей и доступ к дополнительным полям ответа.

## Требования и установка

- Python `3.12`;
- опубликованный стандартный OData-интерфейс информационной базы 1С.

Установка из локального репозитория:

```shell
pip install .
```

Для разработки:

```shell
pip install -e ".[dev]"
```

Установленную версию можно получить программно:

```python
from py1cORM import __version__
```

## Быстрый старт

### 1. Опишите модель

`alias` — имя поля в OData 1С, а `entity_name` — имя набора сущностей.

```python
from uuid import UUID

from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Field


class Nomenclature(ODataModel):
    uid: UUID = Field(alias='Ref_Key')
    name: str = Field(alias='Description')
    article: str = Field(alias='Артикул')
    is_deleted: bool = Field(alias='DeletionMark')

    class Meta:
        entity_name = 'Catalog_Номенклатура'
        pk = 'uid'
```

Если указан `Meta.pk`, первичный ключ автоматически добавляется к явному
`select()`. Это позволяет идентифицировать полученные сущности, даже когда ключ
не был перечислен вручную.

### 2. Создайте подключение

```python
import os

from py1cORM.connection import ODataConnection


connection = ODataConnection(
    host=os.environ['ONE_C_HOST'],
    database=os.environ['ONE_C_DATABASE'],
    username=os.environ['ONE_C_USERNAME'],
    password=os.environ['ONE_C_PASSWORD'],
)
```

Будет использован адрес вида:

```text
{host}/{database}/odata/standard.odata/{entity_name}
```

Не храните учётные данные 1С в исходном коде; передавайте их через переменные
окружения или менеджер секретов.

### 3. Выполните запрос

```python
query = Nomenclature.using(connection)

items = (
    query.select(Nomenclature.name, Nomenclature.article)
    .filter(Nomenclature.is_deleted == False)  # noqa: E712
    .order_by((Nomenclature.name, 'asc'))
    .paginate(top=20)
    .all()
)

for item in items:
    print(item.uid, item.name, item.article)
```

Методы построения запроса можно объединять в цепочки, близкие по стилю к ORM.

## Построение запросов

### Выбор полей

Можно передавать ссылки на поля или их Python-имена:

```python
query.select(Nomenclature.name, 'article').all()
```

Поле, которое не пришло в ответе, считается незагруженным. Проверить его можно
через `entity.is_loaded("field_name")`; обращение к незагруженному полю вызывает
`FieldNotLoadedError`.

### Фильтрация

Поддерживаются `==`, `!=`, `>`, `>=`, `<`, `<=` и логические группы `AND`/`OR`:

```python
from py1cORM.odata.expressions import AND, OR


query.filter(
    AND(
        Nomenclature.is_deleted == False,  # noqa: E712
        OR(
            Nomenclature.name.startswith('Стакан'),
            Nomenclature.article == 'A-001',
        ),
    )
).all()
```

Строковые и множественные операции:

```python
from py1cORM.odata.fields import like


query.filter(Nomenclature.name.contains('стекло')).all()
query.filter(Nomenclature.name.endswith('100 мл')).all()
query.filter(Nomenclature.uid.in_([first_uid, second_uid])).all()
query.filter(like(Nomenclature.name, 'Стакан%')).all()
```

Для возможностей сервера, ещё не представленных выражениями ORM, можно передать
готовый OData-фильтр:

```python
query.filter('DeletionMark eq false').all()
```

### Сортировка

```python
query.order_by('name').all()
query.order_by(('name', 'desc')).all()
query.order_by((Nomenclature.name, 'asc'), (Nomenclature.article, 'desc')).all()
```

Направление передаётся в OData как есть; используйте `"asc"` или `"desc"`.

### Пагинация

```python
page = query.paginate(top=100, skip=200).all()
```

`top` соответствует `$top`, `skip` — `$skip`.

### Загрузка батчами

`batched()` последовательно запрашивает страницы и возвращает итератор списков:

```python
for batch in query.batched(batch_size=100):
    process(batch)
```

Чтобы снизить нагрузку на сервер 1С, задайте паузу между запросами в секундах:

```python
for batch in query.batched(batch_size=100, delay=0.5):
    process(batch)
```

Паузы перед первым запросом нет. Отрицательное значение `delay` вызывает
`ValueError`.

### Получение одной записи

```python
item = query.get(uid=target_uid)
```

`get()` запрашивает не более двух элементов и вызывает `LookupError`, если
ничего не найдено или найдено больше одной записи. Имена полей передаются как
именованные аргументы; доступны lookup-суффиксы `contains`, `startswith`,
`endswith` и `isnull`:

```python
item = query.get(name__startswith='Стакан')
```

## Связи и вложенные данные

### ForeignKey

```python
from py1cORM.models.fields import ForeignKey


class Category(ODataModel):
    uid: UUID = Field(alias='Ref_Key')
    name: str = Field(alias='Description')

    class Meta:
        entity_name = 'Catalog_КатегорииНоменклатуры'


class Product(ODataModel):
    uid: UUID = Field(alias='Ref_Key')
    name: str = Field(alias='Description')
    category: Category | None = ForeignKey(
        model=Category,
        alias='КатегорияНоменклатуры',
        key_field='КатегорияНоменклатуры_Key',
    )

    class Meta:
        entity_name = 'Catalog_Номенклатура'
```

Связь раскрывается через `$expand`:

```python
products = Product.using(connection).expand(Product.category).all()

for product in products:
    if product.is_loaded('category') and product.category.is_loaded():
        print(product.category.name)
```

У `ForeignKey` отдельно доступны ключ связи и загруженная сущность. Если
`$expand` не использовался, объект связи может содержать только ключ.

По связанным полям также можно строить OData-пути:

```python
Product.using(connection).filter(Product.category.name == 'Посуда').all()
```

### Embedded

Вложенные структуры и табличные части описываются через `Embedded`:

```python
from py1cORM.models.fields import Embedded


class Row(ODataModel):
    product_key: UUID = Field(alias='Номенклатура_Key')
    quantity: float = Field(alias='Количество')


class Document(ODataModel):
    uid: UUID = Field(alias='Ref_Key')
    rows: list[Row] = Embedded(model=Row, alias='Товары')

    class Meta:
        entity_name = 'Document_РеализацияТоваровУслуг'
```

## Дополнительные поля ответа

Поля JSON, отсутствующие в модели, не теряются. Они доступны через `extra()`:

```python
for item in query.all():
    print(item.extra())
```

## Разработка

Перед отправкой изменений выполните тот же набор проверок, который используется
в CI:

```shell
ruff format --check .
ruff check .
pytest -q
```

GitHub Actions запускает проверки для pull request и при отправке изменений в
ветки `main` и `dev`.

## Версионирование

Проект использует Semantic Versioning и Conventional Commits. Версия и
`CHANGELOG.md` обновляются `python-semantic-release`; релиз запускается вручную
через GitHub Actions из ветки `main`. Правила сообщений коммитов и начальной
настройки релизов описаны в [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Лицензия

Проект распространяется по лицензии MIT. См. [`LICENSE`](LICENSE).
