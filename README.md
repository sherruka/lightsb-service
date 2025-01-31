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
