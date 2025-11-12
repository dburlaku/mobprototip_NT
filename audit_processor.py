#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Автоматическое заполнение таблиц аудита
Использует локальную нейросеть Ollama для обработки документов
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
from pathlib import Path
import threading
import json

# Проверка и импорт необходимых библиотек
try:
    import requests
except ImportError:
    print("❌ Ошибка: модуль 'requests' не установлен")
    print("Установите: pip install requests")
    sys.exit(1)

try:
    from openpyxl import Workbook, load_workbook
except ImportError:
    print("❌ Ошибка: модуль 'openpyxl' не установлен")
    print("Установите: pip install openpyxl")
    sys.exit(1)


class AuditProcessorApp:
    """Главное приложение для обработки аудита"""

    def __init__(self, root):
        self.root = root
        self.root.title("🔍 Audit Processor - Автозаполнение таблиц аудита")
        self.root.geometry("900x700")
        self.root.configure(bg="#f5f5f5")

        # Проверка Ollama при запуске
        self.ollama_available = self.check_ollama()
        self.model_name = "qwen2.5:latest"

        self.setup_ui()

    def check_ollama(self):
        """Проверка доступности Ollama"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                print(f"✅ Ollama запущен. Найдено моделей: {len(models)}")
                for model in models:
                    print(f"   - {model.get('name', 'unknown')}")
                return True
            return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Ollama недоступен: {e}")
            return False

    def setup_ui(self):
        """Создание интерфейса"""

        # Заголовок
        header = tk.Frame(self.root, bg="#2c3e50", height=80)
        header.pack(fill=tk.X)

        title_label = tk.Label(
            header,
            text="🔍 Audit Processor",
            font=("Arial", 24, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=20)

        # Основной контейнер
        main_container = tk.Frame(self.root, bg="#f5f5f5")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Статус Ollama
        status_frame = tk.Frame(main_container, bg="white", relief=tk.RAISED, borderwidth=1)
        status_frame.pack(fill=tk.X, pady=(0, 15))

        status_color = "#27ae60" if self.ollama_available else "#e74c3c"
        status_text = "✅ Ollama подключен" if self.ollama_available else "❌ Ollama не подключен"

        status_label = tk.Label(
            status_frame,
            text=status_text,
            font=("Arial", 12, "bold"),
            bg="white",
            fg=status_color,
            pady=10
        )
        status_label.pack()

        # Кнопка проверки
        check_btn = ttk.Button(
            status_frame,
            text="🔄 Проверить подключение",
            command=self.recheck_ollama
        )
        check_btn.pack(pady=(0, 10))

        # Секция выбора файлов
        files_frame = tk.LabelFrame(
            main_container,
            text="📁 Выбор файлов для обработки",
            font=("Arial", 12, "bold"),
            bg="white",
            padx=15,
            pady=15
        )
        files_frame.pack(fill=tk.X, pady=(0, 15))

        # Кнопки выбора файлов
        btn_frame = tk.Frame(files_frame, bg="white")
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(
            btn_frame,
            text="📄 Выбрать документы (.docx, .pdf)",
            command=self.select_documents,
            width=35
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="🖼️ Выбрать изображения (OCR)",
            command=self.select_images,
            width=35
        ).pack(side=tk.LEFT, padx=5)

        # Список выбранных файлов
        self.files_listbox = tk.Listbox(
            files_frame,
            height=5,
            font=("Arial", 10),
            bg="#f9f9f9"
        )
        self.files_listbox.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Секция вывода Excel
        excel_frame = tk.LabelFrame(
            main_container,
            text="📊 Выходной файл Excel",
            font=("Arial", 12, "bold"),
            bg="white",
            padx=15,
            pady=15
        )
        excel_frame.pack(fill=tk.X, pady=(0, 15))

        excel_btn_frame = tk.Frame(excel_frame, bg="white")
        excel_btn_frame.pack(fill=tk.X)

        self.excel_path_var = tk.StringVar(value="Не выбран")

        ttk.Button(
            excel_btn_frame,
            text="📁 Выбрать/создать Excel файл",
            command=self.select_excel,
            width=30
        ).pack(side=tk.LEFT, padx=5)

        excel_label = tk.Label(
            excel_btn_frame,
            textvariable=self.excel_path_var,
            font=("Arial", 10),
            bg="white",
            fg="#555"
        )
        excel_label.pack(side=tk.LEFT, padx=10)

        # Кнопка обработки
        process_btn = tk.Button(
            main_container,
            text="🚀 НАЧАТЬ ОБРАБОТКУ",
            font=("Arial", 14, "bold"),
            bg="#27ae60",
            fg="white",
            activebackground="#229954",
            activeforeground="white",
            command=self.start_processing,
            height=2,
            cursor="hand2"
        )
        process_btn.pack(fill=tk.X, pady=(0, 15))

        # Лог консоль
        log_frame = tk.LabelFrame(
            main_container,
            text="📋 Лог обработки",
            font=("Arial", 12, "bold"),
            bg="white",
            padx=10,
            pady=10
        )
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            font=("Consolas", 9),
            bg="#1e1e1e",
            fg="#00ff00",
            insertbackground="white"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Приветственное сообщение
        self.log("=" * 70)
        self.log("🔍 Audit Processor v1.0 запущен")
        self.log("=" * 70)
        if self.ollama_available:
            self.log("✅ Локальная нейросеть Ollama готова к работе")
        else:
            self.log("❌ ВНИМАНИЕ: Ollama не подключен!")
            self.log("   Убедитесь, что Ollama запущен: ollama serve")
            self.log("   И модель установлена: ollama pull qwen2.5:latest")
        self.log("")

        # Хранение выбранных файлов
        self.selected_files = []
        self.excel_file = None

    def log(self, message):
        """Добавить сообщение в лог"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.update()

    def recheck_ollama(self):
        """Повторная проверка Ollama"""
        self.log("🔄 Проверка подключения к Ollama...")
        self.ollama_available = self.check_ollama()

        if self.ollama_available:
            messagebox.showinfo("Успех", "✅ Ollama подключен успешно!")
            self.log("✅ Ollama подключен")
        else:
            messagebox.showerror("Ошибка", "❌ Не удалось подключиться к Ollama\n\nУбедитесь что:\n1. Ollama установлен\n2. Ollama запущен (ollama serve)\n3. Порт 11434 доступен")
            self.log("❌ Ollama недоступен")

        # Обновить UI
        self.setup_ui()

    def select_documents(self):
        """Выбор документов"""
        files = filedialog.askopenfilenames(
            title="Выберите документы",
            filetypes=[
                ("Документы", "*.docx *.pdf"),
                ("Word документы", "*.docx"),
                ("PDF файлы", "*.pdf"),
                ("Все файлы", "*.*")
            ]
        )

        if files:
            for file in files:
                if file not in self.selected_files:
                    self.selected_files.append(file)
                    self.files_listbox.insert(tk.END, f"📄 {os.path.basename(file)}")

            self.log(f"✅ Добавлено файлов: {len(files)}")

    def select_images(self):
        """Выбор изображений для OCR"""
        files = filedialog.askopenfilenames(
            title="Выберите изображения",
            filetypes=[
                ("Изображения", "*.jpg *.jpeg *.png *.bmp"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("Все файлы", "*.*")
            ]
        )

        if files:
            for file in files:
                if file not in self.selected_files:
                    self.selected_files.append(file)
                    self.files_listbox.insert(tk.END, f"🖼️ {os.path.basename(file)}")

            self.log(f"✅ Добавлено изображений: {len(files)}")

    def select_excel(self):
        """Выбор/создание Excel файла"""
        file = filedialog.asksaveasfilename(
            title="Выберите или создайте Excel файл",
            defaultextension=".xlsx",
            filetypes=[("Excel файлы", "*.xlsx"), ("Все файлы", "*.*")]
        )

        if file:
            self.excel_file = file
            self.excel_path_var.set(os.path.basename(file))
            self.log(f"✅ Выбран Excel файл: {os.path.basename(file)}")

    def query_ollama(self, prompt, context=""):
        """Запрос к Ollama API"""
        url = "http://localhost:11434/api/generate"

        full_prompt = f"{context}\n\n{prompt}" if context else prompt

        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": False
        }

        try:
            response = requests.post(url, json=payload, timeout=60)
            if response.status_code == 200:
                return response.json().get('response', '')
            else:
                return f"Ошибка: {response.status_code}"
        except Exception as e:
            return f"Ошибка подключения: {e}"

    def start_processing(self):
        """Начать обработку файлов"""

        if not self.selected_files:
            messagebox.showwarning("Предупреждение", "Выберите файлы для обработки!")
            return

        if not self.excel_file:
            messagebox.showwarning("Предупреждение", "Выберите выходной Excel файл!")
            return

        if not self.ollama_available:
            result = messagebox.askyesno(
                "Ollama недоступен",
                "Ollama не подключен. Обработка будет выполнена в демо-режиме.\n\nПродолжить?"
            )
            if not result:
                return

        # Запуск обработки в отдельном потоке
        thread = threading.Thread(target=self.process_files, daemon=True)
        thread.start()

    def process_files(self):
        """Обработка файлов"""

        self.log("\n" + "=" * 70)
        self.log("🚀 НАЧАЛО ОБРАБОТКИ")
        self.log("=" * 70)

        # Создание Excel файла
        self.log(f"📊 Создание Excel файла: {os.path.basename(self.excel_file)}")

        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "Аудит"

            # Заголовки
            headers = ["№", "Файл", "Тип", "Извлеченный текст", "Анализ", "Примечания"]
            for col, header in enumerate(headers, start=1):
                ws.cell(row=1, column=col, value=header)

            row = 2

            for idx, file_path in enumerate(self.selected_files, start=1):
                self.log(f"\n📄 [{idx}/{len(self.selected_files)}] Обработка: {os.path.basename(file_path)}")

                file_ext = os.path.splitext(file_path)[1].lower()
                file_type = self.get_file_type(file_ext)

                # Извлечение текста
                text = self.extract_text(file_path, file_ext)

                # Анализ через Ollama
                analysis = ""
                if self.ollama_available and text:
                    self.log("🤖 Анализ через нейросеть...")
                    analysis = self.analyze_document(text)
                else:
                    analysis = "Демо-режим: анализ недоступен"

                # Запись в Excel
                ws.cell(row=row, column=1, value=idx)
                ws.cell(row=row, column=2, value=os.path.basename(file_path))
                ws.cell(row=row, column=3, value=file_type)
                ws.cell(row=row, column=4, value=text[:500] + "..." if len(text) > 500 else text)
                ws.cell(row=row, column=5, value=analysis)
                ws.cell(row=row, column=6, value="")

                row += 1
                self.log(f"✅ Обработано: {os.path.basename(file_path)}")

            # Сохранение Excel
            wb.save(self.excel_file)
            self.log(f"\n💾 Excel файл сохранен: {self.excel_file}")

            self.log("\n" + "=" * 70)
            self.log("✅ ОБРАБОТКА ЗАВЕРШЕНА УСПЕШНО!")
            self.log("=" * 70)

            messagebox.showinfo(
                "Успех",
                f"✅ Обработка завершена!\n\nОбработано файлов: {len(self.selected_files)}\nРезультат: {os.path.basename(self.excel_file)}"
            )

        except Exception as e:
            self.log(f"\n❌ ОШИБКА: {e}")
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{e}")

    def get_file_type(self, ext):
        """Определить тип файла"""
        types = {
            '.docx': 'Word документ',
            '.pdf': 'PDF документ',
            '.jpg': 'Изображение JPG',
            '.jpeg': 'Изображение JPEG',
            '.png': 'Изображение PNG',
            '.bmp': 'Изображение BMP'
        }
        return types.get(ext, 'Неизвестный тип')

    def extract_text(self, file_path, file_ext):
        """Извлечение текста из файла"""

        if file_ext == '.docx':
            try:
                from docx import Document
                doc = Document(file_path)
                text = "\n".join([para.text for para in doc.paragraphs])
                self.log(f"   📝 Извлечено {len(text)} символов из Word")
                return text
            except ImportError:
                self.log("   ⚠️ python-docx не установлен")
                return "Ошибка: установите python-docx"
            except Exception as e:
                self.log(f"   ❌ Ошибка чтения Word: {e}")
                return f"Ошибка: {e}"

        elif file_ext == '.pdf':
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    text += page.get_text()
                self.log(f"   📝 Извлечено {len(text)} символов из PDF ({len(doc)} стр.)")
                return text
            except ImportError:
                self.log("   ⚠️ PyMuPDF не установлен")
                return "Ошибка: установите PyMuPDF"
            except Exception as e:
                self.log(f"   ❌ Ошибка чтения PDF: {e}")
                return f"Ошибка: {e}"

        elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp']:
            try:
                import easyocr
                self.log("   🔍 Запуск OCR распознавания...")
                self.log("   ⏳ Загрузка модели EasyOCR (первый запуск может занять время)...")
                reader = easyocr.Reader(['ru', 'en'], gpu=False)
                result = reader.readtext(file_path, detail=0)
                text = "\n".join(result)
                self.log(f"   📝 Распознано {len(text)} символов")
                return text
            except ImportError as ie:
                self.log("   ⚠️ EasyOCR не установлен")
                self.log(f"   Детали: {ie}")
                self.log("   Установите: pip install easyocr")
                return "⚠️ OCR недоступен: EasyOCR не установлен\nУстановите: pip install easyocr"
            except Exception as e:
                self.log(f"   ❌ Ошибка OCR: {e}")
                return f"Ошибка OCR: {e}"

        return "Неподдерживаемый формат файла"

    def analyze_document(self, text):
        """Анализ документа через Ollama"""

        if not text or len(text.strip()) < 10:
            return "Текст слишком короткий для анализа"

        prompt = f"""Проанализируй следующий документ аудита и выдели ключевые моменты:

{text[:2000]}

Предоставь краткий анализ:
1. Основная тема документа
2. Ключевые даты и цифры
3. Важные выводы
4. Рекомендации (если есть)

Ответ дай кратко, до 200 слов."""

        response = self.query_ollama(prompt)
        return response if response else "Ошибка анализа"


def main():
    """Точка входа в приложение"""

    print("=" * 70)
    print("🔍 Audit Processor - Автоматическое заполнение таблиц аудита")
    print("=" * 70)
    print()
    print("Архитектура:")
    print("  • OCR: EasyOCR (офлайн)")
    print("  • Документы: python-docx, PyMuPDF")
    print("  • Нейросеть: Ollama (локально)")
    print("  • Excel: openpyxl")
    print("  • GUI: tkinter")
    print()
    print("=" * 70)
    print()

    root = tk.Tk()
    app = AuditProcessorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
