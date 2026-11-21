# Auto Volume Mixer

Приложение для автоматического управления громкостью Windows-приложений при активности в голосовых чатах Discord и Telegram.

## 🎯 Возможности

- 🎮 **Автоматическое управление громкостью** - Плавно уменьшает громкость музыки, игр и других программ когда кто-то говорит
- 💬 **Discord интеграция** - Отслеживание голосовой активности через официальный Discord Bot API
- 📱 **Telegram интеграция** - Мониторинг голосовых чатов через Telegram API
- 🎚️ **Гибкие настройки** - Настройка громкости для каждого приложения отдельно (0-100%)
- 🔄 **Плавные переходы** - Smooth volume transitions для комфортного прослушивания
- 🎯 **System Tray** - Работа в фоне, сворачивание в трей
- 💾 **Сохранение настроек** - Все настройки сохраняются автоматически

## 📋 Требования

- Windows 10/11
- Python 3.8 или выше
- Discord Bot Token (для Discord интеграции)
- Telegram API credentials (для Telegram интеграции)

## 🚀 Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/QuestGuideRF/auto-volume-mixer.git
cd auto-volume-mixer
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Настройка Discord Bot (опционально)

1. Перейдите на [Discord Developer Portal](https://discord.com/developers/applications)
2. Создайте новое приложение (Application)
3. Перейдите в раздел "Bot" и создайте бота
4. Скопируйте токен бота
5. Включите следующие Privileged Gateway Intents:
   - Presence Intent
   - Server Members Intent
   - Message Content Intent (опционально)
6. Добавьте бота на свой сервер:
   - Перейдите в OAuth2 → URL Generator
   - Выберите scopes: `bot`
   - Выберите Bot Permissions: `View Channels`, `Connect`, `Speak`
   - Скопируйте и откройте сгенерированный URL

### 4. Настройка Telegram API (опционально)

1. Перейдите на [my.telegram.org/apps](https://my.telegram.org/apps)
2. Войдите с вашим номером телефона
3. Создайте новое приложение
4. Скопируйте `api_id` и `api_hash`

### 5. Создание файла .env

Создайте файл `.env` в корневой директории проекта:

```env
# Discord Bot Token
DISCORD_TOKEN=your_discord_bot_token_here

# Telegram API credentials
TELEGRAM_API_ID=your_telegram_api_id
TELEGRAM_API_HASH=your_telegram_api_hash
TELEGRAM_PHONE=+1234567890
```

### 6. Запуск приложения

```bash
python main.py
```

## 📖 Использование

### Первый запуск

1. Запустите приложение
2. Включите мониторинг Discord и/или Telegram в разделе "Settings"
3. Нажмите "🔄 Refresh" чтобы увидеть все активные аудио-приложения
4. Добавьте нужные программы (например, `spotify.exe`, `chrome.exe`, `game.exe`)
5. Настройте уровень громкости для каждого приложения:
   - 0% = полное отключение звука
   - 50% = уменьшение на половину
   - 100% = без изменений

### Настройка программ

Для каждой программы можно настроить:
- ✅ **Enabled** - включить/выключить управление громкостью
- 🎚️ **Volume** - целевая громкость при разговоре (0-100%)
- ❌ **Remove** - удалить из списка

### Тестирование

Нажмите кнопку **"Test Volume Reduction"** чтобы проверить работу:
- Громкость снизится до настроенных значений
- Через 3 секунды громкость восстановится

### Работа в фоне

- Нажмите **"Minimize to Tray"** чтобы свернуть в системный трей
- Приложение продолжит работать в фоне
- Двойной клик по иконке в трее откроет окно
- Правый клик → Exit для выхода

## ⚙️ Настройки

### Основные параметры (config.json)

```json
{
    "smooth_transition": true,
    "transition_duration_ms": 500,
    "restore_delay_seconds": 2,
    "discord_enabled": false,
    "telegram_enabled": false,
    "minimize_to_tray": true,
    "start_minimized": false
}
```

- **smooth_transition** - плавное изменение громкости
- **transition_duration_ms** - длительность перехода в миллисекундах
- **restore_delay_seconds** - задержка перед восстановлением громкости после окончания разговора
- **minimize_to_tray** - сворачивать в трей при закрытии окна
- **start_minimized** - запускать свернутым

## 🔧 Как это работает

1. **Мониторинг голосовой активности**
   - Discord: Использует Discord Bot API для отслеживания voice state changes
   - Telegram: Использует Telethon для мониторинга voice chat participants

2. **Обнаружение речи**
   - Когда кто-то начинает говорить (unmute), приложение получает событие
   - Активируется режим "Speaking"

3. **Управление громкостью**
   - Приложение использует Windows Core Audio API (pycaw)
   - Для каждого настроенного процесса:
     - Сохраняется текущая громкость
     - Плавно изменяется до целевого значения

4. **Восстановление**
   - После окончания разговора (все на mute) запускается таймер
   - После истечения задержки громкость плавно восстанавливается

## 🐛 Troubleshooting

### Discord бот не подключается

- Проверьте правильность токена в `.env`
- Убедитесь что бот добавлен на сервер
- Проверьте что включены необходимые Intents

### Telegram не подключается

- Проверьте `api_id`, `api_hash` и номер телефона
- При первом запуске может потребоваться ввод кода из SMS
- Проверьте файл `auto_volume_mixer.session` (создается автоматически)

### Программа не найдена

- Убедитесь что программа запущена и воспроизводит звук
- Нажмите "🔄 Refresh" чтобы обновить список
- Проверьте точное имя процесса в Task Manager (например, `spotify.exe`)

### Громкость не меняется

- Проверьте что программа включена (галочка ✅)
- Убедитесь что процесс запущен
- Попробуйте кнопку "Test Volume Reduction"

## 📝 Примеры настроек

### Для геймера

```
spotify.exe     - 20%  (музыка почти выключена)
discord.exe     - 100% (голоса остаются на полной громкости)
Game.exe        - 30%  (игра тихая, но слышна)
```

### Для работы

```
chrome.exe      - 40%  (музыка в браузере)
teams.exe       - 100% (рабочие звонки не трогаем)
spotify.exe     - 30%  (фоновая музыка)
```

### Для стримера

```
obs64.exe       - 100% (OBS не трогаем)
spotify.exe     - 10%  (музыка почти выключена)
chrome.exe      - 20%  (алерты тише)
```

## 🔐 Безопасность

- Токены и API ключи хранятся в `.env` файле (добавьте в `.gitignore`!)
- Telegram сессия сохраняется в `auto_volume_mixer.session`
- Приложение использует только официальные API
- Никакие данные не отправляются на внешние серверы

## ⚠️ Важные замечания

### Discord Bot Limitations

Discord Bot API не предоставляет прямого доступа к событиям "speaking". Приложение отслеживает:
- Подключение/отключение от голосового канала
- Mute/Unmute пользователей
- Это не идеальное решение, но работает в рамках официального API

Для более точного определения речи потребуется user account bot (нарушает ToS Discord).

### Telegram

Telegram API работает через user account и требует первоначальной аутентификации.

## 🛠️ Разработка

### Структура проекта

```
Auto-Volume-Mixer/
├── main.py                 # Точка входа
├── main_window.py          # GUI (PyQt5)
├── audio_controller.py     # Управление громкостью (pycaw)
├── discord_monitor.py      # Discord интеграция
├── telegram_monitor.py     # Telegram интеграция
├── config_manager.py       # Управление настройками
├── requirements.txt        # Зависимости
├── config.json            # Настройки (создается автоматически)
├── .env                   # API ключи (создайте вручную)
└── README.md
```

### Зависимости

- **PyQt5** - GUI framework
- **discord.py** - Discord Bot API
- **telethon** - Telegram Client API
- **pycaw** - Windows Core Audio API
- **pystray** - System tray icon
- **python-dotenv** - Environment variables

---

Автор: legenda  
Telegram: [@LEGENDA_SD](https://t.me/LEGENDA_SD)
