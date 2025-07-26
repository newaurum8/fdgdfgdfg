#!/bin/bash

# Скрипт запуска Telegram гарант-бота

echo "🤖 Запуск Telegram гарант-бота..."

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python 3.8+ для работы бота."
    exit 1
fi

# Проверка наличия pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 не найден. Установите pip для работы бота."
    exit 1
fi

# Проверка файла .env
if [ ! -f ".env" ]; then
    echo "⚠️  Файл .env не найден. Создаю из примера..."
    cp .env.example .env
    echo "📝 Отредактируйте файл .env и укажите BOT_TOKEN"
    echo "🔧 Затем запустите скрипт снова"
    exit 1
fi

# Проверка наличия токена
if ! grep -q "BOT_TOKEN=" .env || grep -q "BOT_TOKEN=your_bot_token_here" .env; then
    echo "❌ BOT_TOKEN не настроен в файле .env"
    echo "📝 Получите токен от @BotFather и укажите в .env"
    exit 1
fi

echo "📦 Установка зависимостей..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Ошибка установки зависимостей"
    exit 1
fi

echo "🗃️  Инициализация базы данных..."
echo "🚀 Запуск бота..."

# Запуск бота
python3 main.py