#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт проверки установки всех зависимостей Audit Processor
"""

import sys
import subprocess

print("=" * 70)
print("🔍 Проверка установки зависимостей Audit Processor")
print("=" * 70)
print()

# Информация о Python
print(f"Python версия: {sys.version}")
print(f"Python путь: {sys.executable}")
print()

print("=" * 70)
print("Проверка модулей:")
print("=" * 70)

modules_to_check = [
    ("requests", "Работа с HTTP запросами"),
    ("openpyxl", "Работа с Excel"),
    ("docx", "Чтение Word документов"),
    ("fitz", "Чтение PDF (PyMuPDF)"),
    ("easyocr", "OCR распознавание текста"),
    ("torch", "PyTorch для EasyOCR"),
    ("cv2", "OpenCV для обработки изображений"),
]

results = []

for module_name, description in modules_to_check:
    try:
        module = __import__(module_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {module_name:20} v{version:15} - {description}")
        results.append((module_name, True, version))
    except ImportError as e:
        print(f"❌ {module_name:20} {'НЕ УСТАНОВЛЕН':15} - {description}")
        print(f"   Ошибка: {e}")
        results.append((module_name, False, None))

print()
print("=" * 70)
print("Сводка:")
print("=" * 70)

installed = sum(1 for _, status, _ in results if status)
total = len(results)

print(f"Установлено: {installed}/{total}")
print()

# Критичные модули
critical = ["requests", "openpyxl"]
critical_ok = all(status for name, status, _ in results if name in critical)

if critical_ok:
    print("✅ Все критичные модули установлены")
    print("   Приложение может работать в базовом режиме")
else:
    print("❌ Не установлены критичные модули!")
    print("   Установите: pip install requests openpyxl")

print()

# Опциональные модули для документов
docs = ["docx", "fitz"]
docs_ok = all(status for name, status, _ in results if name in docs)

if docs_ok:
    print("✅ Модули для работы с документами установлены")
else:
    print("⚠️  Модули для документов не установлены")
    print("   Для Word/PDF установите: pip install python-docx PyMuPDF")

print()

# OCR модули
ocr = ["easyocr", "torch", "cv2"]
ocr_ok = all(status for name, status, _ in results if name in ocr)

if ocr_ok:
    print("✅ Модули OCR установлены")
else:
    print("⚠️  OCR недоступен (опционально)")
    if not any(status for name, status, _ in results if name == "easyocr"):
        print("   Для OCR установите: pip install easyocr")

print()
print("=" * 70)
print("Команды для установки недостающих модулей:")
print("=" * 70)

missing = [name for name, status, _ in results if not status]

if missing:
    print()
    print("# Установить все недостающие:")

    if "easyocr" in missing:
        basic = [m for m in missing if m != "easyocr"]
        if basic:
            print(f"pip install {' '.join(basic)}")
        print("pip install easyocr  # Опционально, для OCR (~2GB)")
    else:
        print(f"pip install {' '.join(missing)}")
else:
    print("\n✅ Все модули установлены!")

print()
print("=" * 70)
print("Тест импорта EasyOCR:")
print("=" * 70)

try:
    import easyocr
    print("✅ EasyOCR импортирован успешно")
    print(f"   Версия: {easyocr.__version__ if hasattr(easyocr, '__version__') else 'unknown'}")
    print(f"   Путь: {easyocr.__file__}")

    # Попробовать создать Reader
    try:
        print("\n🔄 Тестирование инициализации Reader...")
        print("   (первый запуск может загрузить модели)")
        # Не создаём reader, так как это долго
        print("   Для полного теста запустите audit_processor.py")
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")

except ImportError as e:
    print(f"❌ EasyOCR не найден")
    print(f"   Ошибка: {e}")
    print()
    print("Возможные причины:")
    print("  1. EasyOCR не установлен")
    print("     Решение: pip install easyocr")
    print()
    print("  2. EasyOCR установлен в другое окружение Python")
    print(f"     Текущий Python: {sys.executable}")
    print("     Решение: установите в это же окружение")
    print()
    print("  3. Используете виртуальное окружение")
    print("     Решение: активируйте окружение перед запуском")

print()
print("=" * 70)
print("Для запуска приложения:")
print("=" * 70)
print()
print(f"python audit_processor.py")
print()
