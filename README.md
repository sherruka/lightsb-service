# Инструкция по запуску проекта

## 1. Создание файлов конфигурации
На основе файлов `env.minio.example` и `env.backend.example` в папке `env` создайте следующие файлы:
- `.env.minio`
- `.env.backend`

## 2. Генерация SSL-сертификатов (для HTTPS)
Перед запуском проекта необходимо создать самоподписанные SSL-сертификаты.
Выполните команду:
```bash
mkdir -p docker/nginx/ssl && openssl req -x509 -newkey rsa:2048 -keyout docker/nginx/ssl/key.pem -out docker/nginx/ssl/cert.pem -days 365 -nodes
```

## 3. Запуск проекта
Для запуска проекта выполните команду:
```bash
./run.sh
```

## 4. Остановка проекта
Для остановки проекта выполните команду:
```bash
./stop.sh
```

## 5. Доступность сервисов

После запуска проекта, следующие сервисы будут доступны:

- **Веб-сервис** (основной функционал проекта) будет доступен по адресу:
  - [https://localhost:8080](https://localhost:8080)

- **MinIO** (объектное хранилище, похожее на Amazon S3) будет доступен на порту 9000 по адресу:
  - [http://localhost:9000](http://localhost:9000)

- **PgAdmin** (интерфейс для управления PostgreSQL базой данных) будет доступен на порту 15432 по адресу:
  - [http://localhost:15432](http://localhost:15432)

- **Locust** (интерфейс нагрузочного тестирования) будет доступен на порту 8089 по адресу:
  - [http://localhost:8089](http://localhost:8089)

Убедитесь, что все порты свободны перед запуском.


# Сервис для проекта LightSB

## 1. Установка драйверов для GPU

Установить драйверы NVIDIA:
1. Открыть **Программы и обновления** → **Дополнительные драйверы**.
2. Выбрать доступные драйверы NVIDIA и установить их.

## 2. Установка CUDA

Устанавливаем CUDA:
```bash
sudo apt install nvidia-cuda-toolkit
```
После установки выполните перезагрузку:
```bash
reboot
```

## 3. Клонирование репозитория проекта

Склонируйте репозиторий ALAE:
```bash
git clone https://github.com/podgorskiy/ALAE
cd ALAE
```

## 4. Установка Python 3.8 и создание виртуального окружения

Для работы потребуется Python 3.8 (подходят также версии ниже):
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.8 python3.8-venv
```

Создайте виртуальное окружение (можно выбрать любой путь вместо `myenv`):
```bash
python3.8 -m venv myenv
source myenv/bin/activate
```

## 5. Установка зависимостей

Перед установкой зависимостей исправьте `requirements.txt`: замените `sklearn` на `scikit-learn`.

Далее установите зависимости:
```bash
pip install -r requirements.txt
```

## 6. Исправление проблемы с `torch`

Откройте файл `myenv/lib/python3.8/site-packages/dlutils/pytorch/jacobian.py` и внесите изменения:

**Удалите строку:**
```python
from torch.autograd.gradcheck import zero_gradients
```

**Добавьте вместо неё:**
```python
def zero_gradients(i):
    for t in iter_gradients(i):
        t.zero_()
```

## 7. Загрузка необходимых данных

Перед запуском загрузите все необходимые файлы:
```bash
python training_artifacts/download_all.py
```

## 8. Запуск интерактивного демо

Запустите демонстрационную версию
```bash
python interactive_demo.py
```