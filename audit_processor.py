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
from datetime import datetime
import subprocess
import platform

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

        # Загрузка конфигурации
        self.load_config()

        # Инициализация AI провайдера
        self.init_ai_provider()

        self.setup_ui()

    def load_config(self):
        """Загрузка конфигурации из config.json"""
        config_path = Path(__file__).parent / "config.json"

        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                print(f"✅ Конфигурация загружена из {config_path}")
            except Exception as e:
                print(f"⚠️ Ошибка загрузки config.json: {e}")
                self.config = {"ai_provider": "ollama"}
        else:
            print("ℹ️ config.json не найден, используется Ollama по умолчанию")
            self.config = {"ai_provider": "ollama"}

    def init_ai_provider(self):
        """Инициализация AI провайдера"""
        self.ai_provider = self.config.get("ai_provider", "ollama")

        if self.ai_provider == "gemini":
            # Google Gemini
            gemini_config = self.config.get("gemini", {})
            self.gemini_api_key = gemini_config.get("api_key")
            self.gemini_model = gemini_config.get("model", "gemini-1.5-flash")

            if self.gemini_api_key:
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=self.gemini_api_key)
                    # Убираем префикс "models/" если он есть
                    model_name = self.gemini_model.replace("models/", "")
                    self.gemini_client = genai.GenerativeModel(model_name)
                    self.ai_available = True
                    print(f"✅ Google Gemini подключен ({model_name})")
                    print("🎉 Обработка будет в 10-20 раз быстрее чем с Ollama!")
                except Exception as e:
                    print(f"❌ Ошибка подключения Gemini: {e}")
                    print(f"   Попробуйте модель: gemini-1.5-flash-latest")
                    self.ai_available = False
            else:
                print("❌ API ключ Gemini не найден в config.json")
                self.ai_available = False
        else:
            # Ollama (по умолчанию)
            self.ollama_available = self.check_ollama()
            self.ai_available = self.ollama_available

            if self.check_model_available("llama3.2:1b"):
                self.model_name = "llama3.2:1b"
                print("✅ Используется быстрая модель llama3.2:1b")
            else:
                self.model_name = "llama3.2:latest"
                print("ℹ️ Используется стандартная модель llama3.2:latest")

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

    def check_model_available(self, model_name):
        """Проверка доступности конкретной модели"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return any(model_name in model.get('name', '') for model in models)
            return False
        except:
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

        # Статус AI
        status_frame = tk.Frame(main_container, bg="white", relief=tk.RAISED, borderwidth=1)
        status_frame.pack(fill=tk.X, pady=(0, 15))

        # Определяем статус в зависимости от провайдера
        if self.ai_provider == "gemini":
            status_color = "#27ae60" if self.ai_available else "#e74c3c"
            status_text = f"✅ Google Gemini подключен ({self.gemini_model})" if self.ai_available else "❌ Gemini не подключен"
        else:
            status_color = "#27ae60" if self.ai_available else "#e74c3c"
            status_text = "✅ Ollama подключен" if self.ai_available else "❌ Ollama не подключен"

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

        # Секция шаблона Excel
        excel_frame = tk.LabelFrame(
            main_container,
            text="📊 Шаблон Excel для заполнения",
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
            text="📁 Выбрать шаблон Excel",
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
        self.process_btn = tk.Button(
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
        self.process_btn.pack(fill=tk.X, pady=(0, 15))

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
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Кнопки управления логами и файлом
        log_buttons_frame = tk.Frame(log_frame, bg="white")
        log_buttons_frame.pack(fill=tk.X)

        ttk.Button(
            log_buttons_frame,
            text="📋 Копировать логи",
            command=self.copy_logs,
            width=20
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            log_buttons_frame,
            text="🗑️ Очистить логи",
            command=self.clear_logs,
            width=20
        ).pack(side=tk.LEFT, padx=5)

        self.open_file_btn = ttk.Button(
            log_buttons_frame,
            text="📂 Открыть готовый файл",
            command=self.open_result_file,
            width=25,
            state=tk.DISABLED
        )
        self.open_file_btn.pack(side=tk.LEFT, padx=5)

        # Приветственное сообщение
        self.log("=" * 70)
        self.log("🔍 Audit Processor v1.0 запущен")
        self.log("=" * 70)
        if self.ai_provider == "gemini":
            if self.ai_available:
                self.log(f"✅ Google Gemini подключен ({self.gemini_model})")
                self.log("🎉 Обработка будет быстрой и качественной!")
            else:
                self.log("❌ ВНИМАНИЕ: Gemini не подключен!")
                self.log("   Проверьте API ключ в config.json")
        else:
            if self.ai_available:
                self.log("✅ Локальная нейросеть Ollama готова к работе")
            else:
                self.log("❌ ВНИМАНИЕ: Ollama не подключен!")
                self.log("   Убедитесь, что Ollama запущен: ollama serve")
        self.log("")

        # Хранение выбранных файлов
        self.selected_files = []
        self.excel_file = None
        self.excel_header_row = 1  # Номер строки с заголовками (по умолчанию 1)
        self.last_created_file = None  # Последний созданный файл
        self.is_processing = False  # Флаг выполнения обработки

    def log(self, message):
        """Добавить сообщение в лог"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.update()

    def copy_logs(self):
        """Копировать логи в буфер обмена"""
        logs = self.log_text.get("1.0", tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(logs)
        self.root.update()
        messagebox.showinfo("Успех", "✅ Логи скопированы в буфер обмена!")
        self.log("📋 Логи скопированы в буфер обмена")

    def clear_logs(self):
        """Очистить логи"""
        result = messagebox.askyesno("Подтверждение", "Очистить все логи?")
        if result:
            self.log_text.delete("1.0", tk.END)
            self.log("🔍 Audit Processor v1.0")
            self.log("Логи очищены")

    def open_result_file(self):
        """Открыть готовый Excel файл"""
        if not self.last_created_file or not os.path.exists(self.last_created_file):
            messagebox.showerror("Ошибка", "Файл не найден!")
            return

        try:
            # Открыть файл в системном приложении
            if platform.system() == 'Windows':
                os.startfile(self.last_created_file)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', self.last_created_file])
            else:  # Linux
                subprocess.run(['xdg-open', self.last_created_file])

            self.log(f"📂 Открыт файл: {os.path.basename(self.last_created_file)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{e}")
            self.log(f"❌ Ошибка открытия файла: {e}")

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
        """Выбор шаблона Excel файла"""
        file = filedialog.askopenfilename(
            title="Выберите шаблон Excel для заполнения",
            defaultextension=".xlsx",
            filetypes=[("Excel файлы", "*.xlsx *.xls"), ("Все файлы", "*.*")]
        )

        if file:
            # Проверяем, что файл существует и можно прочитать
            try:
                wb = load_workbook(file)
                ws = wb.active

                # Ищем заголовки в первых 10 строках
                self.log(f"📊 Анализ структуры файла: {os.path.basename(file)}")
                self.log(f"   Активный лист: {ws.title}")
                self.log(f"   Размер: {ws.max_row} строк x {ws.max_column} колонок")

                # Показываем первые строки для диагностики
                self.log("\n   Содержимое первых строк:")
                header_row = None
                headers = []

                for row_idx in range(1, min(11, ws.max_row + 1)):
                    row_values = []
                    non_empty_count = 0

                    for col_idx in range(1, min(ws.max_column + 1, 21)):  # Максимум 20 колонок
                        cell = ws.cell(row=row_idx, column=col_idx)
                        value = cell.value

                        if value is not None and str(value).strip():
                            non_empty_count += 1
                            row_values.append(str(value).strip()[:30])
                        else:
                            row_values.append("")

                    # Показываем строку
                    display_values = [v if v else "(пусто)" for v in row_values[:5]]
                    self.log(f"   Строка {row_idx}: {' | '.join(display_values)}{'...' if len(row_values) > 5 else ''}")

                    # Если нашли строку с несколькими заполненными ячейками - это кандидат на заголовки
                    if non_empty_count >= 2 and not header_row:
                        header_row = row_idx
                        headers = [str(cell.value).strip() for cell in ws[row_idx] if cell.value is not None and str(cell.value).strip()]

                if not headers:
                    error_msg = f"""В файле не найдены заголовки!

Проверьте:
1. Первая строка должна содержать названия колонок
2. Ячейки не должны быть пустыми
3. Файл должен быть в формате .xlsx

Диагностика показала:
- Строк в файле: {ws.max_row}
- Колонок: {ws.max_column}

Смотрите лог для деталей."""
                    messagebox.showerror("Ошибка анализа файла", error_msg)
                    self.log("\n❌ Заголовки не найдены!")
                    self.log("   Возможные причины:")
                    self.log("   - Первые строки пустые")
                    self.log("   - Заголовки объединены в одну ячейку")
                    self.log("   - Файл имеет нестандартную структуру")
                    return

                self.excel_file = file
                self.excel_header_row = header_row  # Сохраняем номер строки с заголовками
                self.excel_path_var.set(os.path.basename(file))

                self.log(f"\n✅ Выбран шаблон Excel: {os.path.basename(file)}")
                self.log(f"   Строка заголовков: {header_row}")
                self.log(f"   Найдено колонок: {len(headers)}")
                self.log(f"   Заголовки:")
                for i, h in enumerate(headers[:10], start=1):
                    self.log(f"      {i}. {h}")
                if len(headers) > 10:
                    self.log(f"      ... и еще {len(headers) - 10} колонок")

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть шаблон:\n{e}")
                self.log(f"❌ Ошибка чтения шаблона: {e}")
                import traceback
                self.log(f"   Подробности:\n{traceback.format_exc()}")

    def query_ollama(self, prompt, context=""):
        """Запрос к AI (поддержка Ollama и Gemini)"""
        full_prompt = f"{context}\n\n{prompt}" if context else prompt

        # Google Gemini
        if self.ai_provider == "gemini":
            try:
                response = self.gemini_client.generate_content(
                    full_prompt,
                    generation_config={
                        "temperature": 0.1,
                        "max_output_tokens": 500,
                    },
                    safety_settings=[
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                    ]
                )

                # Безопасная проверка наличия текста в ответе
                if response.candidates and len(response.candidates) > 0:
                    candidate = response.candidates[0]

                    # Проверяем finish_reason
                    if hasattr(candidate, 'finish_reason'):
                        finish_reason = str(candidate.finish_reason)
                        if finish_reason != "STOP" and finish_reason != "1":  # 1 = STOP
                            return f"Gemini заблокировал ответ: {finish_reason}"

                    # Пытаемся получить текст
                    if candidate.content and candidate.content.parts:
                        return candidate.content.parts[0].text
                    else:
                        return "Gemini вернул пустой ответ"
                else:
                    return "Gemini не вернул кандидатов ответа"

            except Exception as e:
                return f"Ошибка Gemini: {e}"

        # Ollama (по умолчанию)
        url = "http://localhost:11434/api/generate"

        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 250,
                "top_k": 10,
                "top_p": 0.9
            }
        }

        try:
            response = requests.post(url, json=payload, timeout=300)
            if response.status_code == 200:
                return response.json().get('response', '')
            else:
                return f"Ошибка: {response.status_code}"
        except Exception as e:
            return f"Ошибка подключения: {e}"

    def start_processing(self):
        """Начать обработку файлов"""

        # Проверка, не запущена ли уже обработка
        if self.is_processing:
            messagebox.showwarning("Внимание", "⚠️ Обработка уже выполняется!\nПожалуйста, дождитесь завершения.")
            return

        if not self.selected_files:
            messagebox.showwarning("Предупреждение", "Выберите файлы для обработки!")
            return

        if not self.excel_file:
            messagebox.showwarning("Предупреждение", "Выберите выходной Excel файл!")
            return

        if not self.ai_available:
            provider_name = "Google Gemini" if self.ai_provider == "gemini" else "Ollama"
            result = messagebox.askyesno(
                f"{provider_name} недоступен",
                f"{provider_name} не подключен. Обработка будет выполнена в демо-режиме.\n\nПродолжить?"
            )
            if not result:
                return

        # Блокируем кнопку и устанавливаем флаг
        self.is_processing = True
        self.process_btn.config(state=tk.DISABLED, text="⏳ ОБРАБОТКА...", bg="#95a5a6")

        # Запуск обработки в отдельном потоке
        thread = threading.Thread(target=self.process_files, daemon=True)
        thread.start()

    def read_existing_table_content(self, ws, header_row_num, headers, header_positions):
        """
        Читает ВСЕ строки таблицы с их содержимым (включая колонку C)

        Returns:
            dict: {row_number: {column_name: value, ...}, ...}
        """
        self.log("📖 Чтение существующего содержимого таблицы...")
        table_rows = {}

        for row_idx in range(header_row_num + 1, ws.max_row + 1):
            row_data = {}
            has_content = False

            # Читаем ВСЕ колонки (A, B, C и дальше)
            for col_name, col_idx in header_positions.items():
                cell_value = ws.cell(row=row_idx, column=col_idx).value
                if cell_value and str(cell_value).strip():
                    row_data[col_name] = str(cell_value).strip()
                    has_content = True

            # Сохраняем ВСЕ строки, даже если в них только одна колонка заполнена
            if has_content:
                table_rows[row_idx] = row_data

        self.log(f"   ✓ Найдено строк с данными: {len(table_rows)}")

        # Подсчитываем строки для заполнения (не заголовки)
        # Заголовки обычно короткие (<50 символов) или содержат ключевые слова
        fillable_count = 0
        header_keywords = ['элемент стандарта', 'пункты к проверке', 'комментарии:',
                          'представитель', 'проверка дополнительных', 'критерий:', 'требования к см']

        for row_data in table_rows.values():
            row_text = " ".join([str(v).lower() for v in row_data.values()])
            # Строка для заполнения если:
            # 1. Длиннее 50 символов (не короткий заголовок)
            # 2. Не содержит ключевые слова заголовков
            is_header = len(row_text) < 50 or any(keyword in row_text for keyword in header_keywords)
            if not is_header:
                fillable_count += 1

        self.log(f"   ✓ Из них строк для заполнения: {fillable_count} (остальные - заголовки)")

        # Показываем примеры первых 5 строк
        sample_count = min(5, len(table_rows))
        if sample_count > 0:
            self.log(f"   Примеры первых {sample_count} строк:")
            for i, (row_num, row_data) in enumerate(list(table_rows.items())[:sample_count]):
                # Показываем только колонку B (вопросы/информация)
                col_b_value = row_data.get("Информацию представляет организация. В случае не применимости раздела или пункта - делайте соответствующую пометку, например Не применимо", "")
                if not col_b_value:
                    # Берем первое непустое значение
                    col_b_value = next(iter(row_data.values()), "")
                preview = col_b_value[:80] + "..." if len(col_b_value) > 80 else col_b_value
                self.log(f"     Строка {row_num}: {preview}")

        return table_rows

    def create_table_index(self, table_rows):
        """
        Создает индекс строк таблицы ОДИН РАЗ
        ТОЛЬКО для строк для заполнения (не заголовков)

        Returns:
            str: Список строк для заполнения с их содержимым
        """
        self.log("🗂️ Создание индекса строк таблицы (один раз)...")

        # Ключевые слова заголовков (та же логика что в read_existing_table_content)
        header_keywords = ['элемент стандарта', 'пункты к проверке', 'комментарии:',
                          'представитель', 'проверка дополнительных', 'критерий:', 'требования к см']

        # Формируем описание ТОЛЬКО строк для заполнения (пропускаем заголовки)
        rows_description = []
        fillable_rows_count = 0

        for row_num, row_data in table_rows.items():
            # Берем текст из всех колонок
            row_text = " | ".join([f"{val}" for val in row_data.values()])

            # Определяем, является ли это заголовком
            row_text_lower = row_text.lower()
            is_header = len(row_text) < 50 or any(keyword in row_text_lower for keyword in header_keywords)

            # Включаем в индекс ТОЛЬКО строки для заполнения
            if not is_header:
                # Показываем до 25 символов на строку (оптимизация для ollama)
                rows_description.append(f"Строка {row_num}: {row_text[:25]}")
                fillable_rows_count += 1

        index_text = "\n".join(rows_description)

        # Устанавливаем лимит 6000 символов (оптимизация нагрузки на ollama)
        # При 25 символах на строку + 12 префикс = 37*152 = ~5624, влезет все 152 строки
        max_index_size = 6000
        if len(index_text) > max_index_size:
            # Обрезаем если все равно не влезло
            lines = index_text.split('\n')
            truncated_lines = []
            current_size = 0
            for line in lines:
                if current_size + len(line) + 1 > max_index_size:
                    break
                truncated_lines.append(line)
                current_size += len(line) + 1
            index_text = "\n".join(truncated_lines)
            rows_shown = len(truncated_lines)
            self.log(f"✅ Индекс создан ({len(index_text)} символов, {rows_shown}/{fillable_rows_count} строк для заполнения)")
        else:
            self.log(f"✅ Индекс создан ({len(index_text)} символов, {fillable_rows_count} строк для заполнения)")

        return index_text

    def clean_json_for_parsing(self, json_str):
        """
        Очищает JSON от проблемных символов, которые AI часто вставляет

        Проблемы:
        - Переносы строк \n внутри строковых значений
        - Неэкранированные кавычки
        - Неправильные escape последовательности вроде \[ или \]

        Returns:
            str: Очищенный JSON, готовый к парсингу
        """
        import re

        # 0. КРИТИЧНО: AI llama возвращает JSON с одинарными кавычками {'key': 'value'}
        # Заменяем одинарные кавычки на двойные (но только для ключей и значений, не внутри текста)
        # Простая эвристика: заменяем ' на " если они окружают буквы/цифры
        json_str = re.sub(r"'(\w+)'", r'"\1"', json_str)  # 'key' → "key"
        json_str = re.sub(r":\s*'([^']*)'", r': "\1"', json_str)  # : 'value' → : "value"

        # 1. Удаляем буквальные переносы строк внутри строковых значений
        # Заменяем \n на пробел
        json_str = json_str.replace('\\n', ' ')

        # 2. Удаляем реальные переносы строк внутри строковых значений
        # Находим все строковые значения и заменяем переносы на пробелы
        def replace_newlines_in_strings(match):
            string_content = match.group(1)
            # Заменяем переносы строк на пробелы
            cleaned = string_content.replace('\n', ' ').replace('\r', ' ')
            # Удаляем множественные пробелы
            cleaned = re.sub(r'\s+', ' ', cleaned)
            return f'"{cleaned}"'

        json_str = re.sub(r'"([^"]*)"', replace_newlines_in_strings, json_str)

        # 3. Исправляем неправильные escape последовательности
        # \[ → [ и \] → ]
        json_str = json_str.replace('\\[', '[').replace('\\]', ']')

        # 4. Удаляем другие проблемные escape последовательности
        # Кроме валидных: \", \\, \/, \b, \f, \n, \r, \t, \uXXXX
        json_str = re.sub(r'\\(?!["\\/bfnrtu])', '', json_str)

        return json_str

    def match_text_to_rows(self, extracted_text, table_rows, file_path, headers, table_index=None):
        """
        Использует AI для определения, в какую строку таблицы нужно вставить извлеченный текст

        Args:
            extracted_text: Текст, извлеченный из документа/изображения
            table_rows: Словарь существующих строк таблицы {row_num: {col: value}}
            file_path: Путь к обрабатываемому файлу
            headers: Список заголовков таблицы

        Returns:
            dict: {
                "matched_rows": [row_numbers],
                "data_to_insert": {column_name: value},
                "explanation": "..."
            }
        """
        self.log("   🧠 AI анализирует соответствие текста строкам таблицы...")

        # Если есть индекс - используем его (БЫСТРО!)
        if table_index:
            prompt = f"""ТАБЛИЦА:
{table_index}

ТЕКСТ:
{extracted_text[:450]}

Найди 1-2 строки таблицы для этого текста. JSON:
{{"matched_rows":[номера],"target_column":"Свидетельства","extracted_data":"весь текст выше","explanation":"причина"}}"""
            self.log(f"   Использую индекс строк (ускоренный режим)")
        else:
            # Без индекса - полный анализ (МЕДЛЕННО)
            rows_description = []
            for row_num, row_data in table_rows.items():
                row_text = " | ".join([f"{col}: {val}" for col, val in row_data.items()])
                # Увеличиваем лимит до 300 символов
                rows_description.append(f"Строка {row_num}: {row_text[:300]}")

            rows_text = "\n".join(rows_description)

            prompt = f"""Ты помогаешь заполнить таблицу аудита. Я дам тебе:
1. Список вопросов/тем из таблицы
2. Текст из фотографии/документа (ответ/свидетельство)

ВОПРОСЫ ИЗ ТАБЛИЦЫ ({len(table_rows)} строк):
{rows_text[:15000]}

ТЕКСТ ИЗ ФОТОГРАФИИ (может быть ответом на один из вопросов):
{extracted_text[:1200]}

ЗАДАЧА:
1. Исправь ошибки OCR в ТЕКСТЕ ИЗ ФОТОГРАФИИ
2. Определи, на какие ВОПРОСЫ ИЗ ТАБЛИЦЫ отвечает этот текст
3. Верни НОМЕРА СТРОК где эти вопросы + ИСПРАВЛЕННЫЙ ТЕКСТ ИЗ ФОТОГРАФИИ

ФОРМАТ ОТВЕТА (строго JSON):
{{"matched_rows":[123,145],"target_column":"Свидетельства","extracted_data":"исправленный текст из фото","explanation":"текст отвечает на вопросы о..."}}

ВЕРНИ ТОЛЬКО JSON!"""

        # Логируем размер промпта
        prompt_size = len(prompt)
        self.log(f"   Размер промпта: ~{prompt_size} символов")

        try:
            response = self.query_ollama(prompt)

            if not response or len(response.strip()) < 10:
                self.log("   ⚠️ AI вернул пустой ответ")
                return None

            # Логируем начало ответа
            self.log(f"   AI ответ (начало): {response[:200]}...")

            # Парсим JSON из ответа
            import re
            json_match = re.search(r'\{[\s\S]*?"matched_rows"[\s\S]*?\}', response)

            if not json_match:
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response)

            if json_match:
                try:
                    json_str = json_match.group(0)

                    # КРИТИЧНО: Очистка JSON от проблемных символов перед парсингом
                    # AI часто возвращает текст с переносами строк и неэкранированными символами
                    json_str = self.clean_json_for_parsing(json_str)

                    result = json.loads(json_str)

                    if "matched_rows" in result:
                        # Преобразуем все элементы в целые числа (AI может вернуть '26', 26.0, "26")
                        # Фильтруем невалидные значения (дробные числа, не-числа)
                        rows_list = result['matched_rows']
                        valid_rows = []
                        for r in rows_list:
                            try:
                                # Преобразуем в float, потом в int
                                num = float(r) if isinstance(r, str) else r
                                # Проверяем что это целое число (без дробной части)
                                if isinstance(num, (int, float)) and num == int(num):
                                    valid_rows.append(int(num))
                                else:
                                    self.log(f"   ⚠️ Пропущен дробный номер строки: {r}")
                            except (ValueError, TypeError):
                                self.log(f"   ⚠️ Пропущен невалидный номер строки: {r}")

                        if not valid_rows:
                            self.log(f"   ⚠️ Нет валидных номеров строк после фильтрации")
                            return None

                        result['matched_rows'] = valid_rows
                        matched_count = len(valid_rows)
                        self.log(f"   ✓ AI определил соответствие с {matched_count} строками")

                        if matched_count > 0:
                            self.log(f"     Строки: {valid_rows}")
                            self.log(f"     Целевая колонка: {result.get('target_column', 'не указана')}")

                        return result
                    else:
                        self.log("   ⚠️ JSON не содержит поле 'matched_rows'")
                        return None

                except json.JSONDecodeError as je:
                    self.log(f"   ⚠️ Ошибка парсинга JSON: {je}")
                    return None
            else:
                self.log("   ⚠️ JSON не найден в ответе AI")
                return None

        except Exception as e:
            self.log(f"   ⚠️ Ошибка AI-анализа: {e}")
            import traceback
            self.log(f"   Трейсбек: {traceback.format_exc()[:300]}")
            return None

    def process_files(self):
        """Обработка файлов с анализом существующей таблицы и умным размещением данных"""

        import time
        start_time_total = time.time()

        self.log("\n" + "=" * 70)
        self.log("🚀 НАЧАЛО ОБРАБОТКИ")
        self.log("=" * 70)

        # Создание нового файла с timestamp (не перезаписываем шаблон)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_dir = os.path.dirname(self.excel_file)
        base_name = os.path.splitext(os.path.basename(self.excel_file))[0]
        new_filename = f"{base_name}_заполнен_{timestamp}.xlsx"
        output_file = os.path.join(base_dir, new_filename)

        self.log(f"📊 Загрузка шаблона: {os.path.basename(self.excel_file)}")

        try:
            # Загрузка шаблона (сохраняя форматирование)
            wb = load_workbook(self.excel_file)
            ws = wb.active

            # Анализ структуры шаблона
            self.log("🔍 Анализ структуры шаблона...")
            headers = []
            header_positions = {}  # {имя колонки: индекс колонки}

            # Используем сохраненный номер строки с заголовками
            header_row_num = getattr(self, 'excel_header_row', 1)
            self.log(f"   Чтение заголовков из строки {header_row_num}")

            for idx, cell in enumerate(ws[header_row_num], start=1):
                if cell.value and str(cell.value).strip():
                    header_name = str(cell.value).strip()
                    headers.append(header_name)
                    header_positions[header_name] = idx
                    self.log(f"   Колонка {idx}: {header_name}")

            # ВАЖНО: Добавляем колонку C (Свидетельства) вручную, если её нет
            if 3 not in header_positions.values():
                evidence_col_name = "Свидетельства"
                headers.append(evidence_col_name)
                header_positions[evidence_col_name] = 3
                self.log(f"   Колонка 3: {evidence_col_name} (добавлена вручную)")

            if not headers:
                raise Exception("В шаблоне не найдены заголовки!")

            self.log(f"✅ Найдено {len(headers)} колонок (включая Свидетельства)")

            # Читаем существующее содержимое таблицы
            table_rows = self.read_existing_table_content(ws, header_row_num, headers, header_positions)

            if not table_rows:
                self.log("⚠️ ВНИМАНИЕ: В таблице нет существующих данных!")
                self.log("   Программа будет добавлять новые строки.")

            # Добавляем колонку для объяснений если её нет
            explanation_col = None
            for col_name in ["Объяснение размещения", "Пояснения", "Комментарии AI", "Объяснение AI"]:
                if col_name in header_positions:
                    explanation_col = header_positions[col_name]
                    self.log(f"   Используется существующая колонка '{col_name}' для объяснений")
                    break

            if not explanation_col:
                explanation_col = ws.max_column + 1
                # Добавляем в строку заголовков
                ws.cell(row=header_row_num, column=explanation_col, value="Объяснение AI")
                header_positions["Объяснение AI"] = explanation_col
                self.log(f"   Добавлена колонка 'Объяснение AI' (позиция {explanation_col})")

            # Счетчики для статистики
            matched_count = 0
            not_matched_count = 0
            updated_rows = []

            # СОЗДАЕМ ИНДЕКС ТАБЛИЦЫ ОДИН РАЗ (ускорение!)
            table_index = None
            if self.ai_available and table_rows:
                table_index = self.create_table_index(table_rows)

            # Обработка каждого файла
            for idx, file_path in enumerate(self.selected_files, start=1):
                file_start_time = time.time()
                self.log(f"\n📄 [{idx}/{len(self.selected_files)}] Обработка: {os.path.basename(file_path)}")

                file_ext = os.path.splitext(file_path)[1].lower()

                # Извлечение текста
                text = self.extract_text(file_path, file_ext)

                if not text or len(text.strip()) < 10:
                    self.log("   ⚠️ Извлечено недостаточно текста, пропускаем")
                    continue

                # Показываем распознанный текст (первые 300 символов)
                text_preview = text[:300].replace('\n', ' ')
                self.log(f"   📝 Распознанный текст: {text_preview}...")

                # AI-анализ и сопоставление с существующими строками
                if self.ai_available and table_rows:
                    match_result = self.match_text_to_rows(text, table_rows, file_path, headers, table_index)

                    if match_result and match_result.get("matched_rows"):
                        # Нашли соответствие - вставляем в найденные строки
                        matched_rows = match_result["matched_rows"]
                        target_column = match_result.get("target_column", "")
                        extracted_data = match_result.get("extracted_data", text[:500])
                        explanation = match_result.get("explanation", "AI определил соответствие")

                        for row_num in matched_rows:
                            if row_num in table_rows:
                                # Проверяем что это не заголовок (те же критерии что в create_table_index)
                                row_data = table_rows[row_num]
                                row_text = " ".join([str(v).lower() for v in row_data.values()])
                                header_keywords = ['элемент стандарта', 'пункты к проверке', 'комментарии:',
                                                  'представитель', 'проверка дополнительных', 'критерий:', 'требования к см']
                                is_header = len(row_text) < 50 or any(keyword in row_text for keyword in header_keywords)

                                if is_header:
                                    self.log(f"   ⚠️ Строка {row_num} является заголовком, пропускаем вставку")
                                    continue

                                # Вставляем извлеченные данные в целевую колонку (БЕЗ названия файла)
                                # Приоритет: Свидетельства, если target_column не найдена
                                col_idx = None
                                if target_column and target_column in header_positions:
                                    col_idx = header_positions[target_column]
                                elif "Свидетельства" in header_positions:
                                    col_idx = header_positions["Свидетельства"]
                                    self.log(f"   ⚠️ Колонка '{target_column}' не найдена, использую 'Свидетельства'")

                                if col_idx:
                                    # Добавляем к существующим данным (не перезаписываем)
                                    existing_value = ws.cell(row=row_num, column=col_idx).value
                                    if existing_value:
                                        new_value = f"{existing_value}\n\n{extracted_data}"
                                    else:
                                        new_value = extracted_data

                                    ws.cell(row=row_num, column=col_idx, value=new_value)
                                    self.log(f"   ✓ Данные добавлены в строку {row_num}, колонка 'Свидетельства'")

                                # ВСЕГДА добавляем объяснение С НАЗВАНИЕМ ФАЙЛА в колонку D (даже если данные не вставлены)
                                ws.cell(row=row_num, column=explanation_col, value=f"Файл: {os.path.basename(file_path)}\n{explanation}")

                                updated_rows.append(row_num)

                        matched_count += 1
                        self.log(f"✅ Данные размещены в {len(matched_rows)} строках")
                    else:
                        # Не нашли соответствие - пропускаем или добавляем в конец
                        not_matched_count += 1
                        self.log(f"⚠️ AI не нашел подходящих строк для этого документа")
                        self.log(f"   Документ пропущен (данные не добавлены)")
                else:
                    # Fallback: AI недоступен или нет существующих строк
                    self.log("⚠️ AI недоступен или таблица пуста - файл пропущен")
                    not_matched_count += 1

                # Логируем время обработки файла
                file_elapsed = time.time() - file_start_time
                self.log(f"   ⏱️ Время обработки файла: {file_elapsed:.1f} сек")

            # Сохранение файла
            self.log(f"\n💾 Сохранение результата: {new_filename}")
            wb.save(output_file)
            self.last_created_file = output_file

            # Подсчет общего времени
            total_elapsed = time.time() - start_time_total
            minutes = int(total_elapsed // 60)
            seconds = int(total_elapsed % 60)
            time_str = f"{minutes} мин {seconds} сек" if minutes > 0 else f"{seconds} сек"

            self.log("\n" + "=" * 70)
            self.log("✅ ОБРАБОТКА ЗАВЕРШЕНА УСПЕШНО!")
            self.log("=" * 70)
            self.log(f"⏱️  ОБЩЕЕ ВРЕМЯ ОБРАБОТКИ: {time_str}")
            self.log(f"📂 Файл доступен: {output_file}")
            self.log(f"📝 Обработано файлов: {len(self.selected_files)}")
            self.log(f"📊 Статистика:")
            self.log(f"   • Файлов с найденным соответствием: {matched_count}")
            self.log(f"   • Файлов без соответствия: {not_matched_count}")
            self.log(f"   • Обновлено уникальных строк: {len(set(updated_rows))}")
            if updated_rows:
                unique_rows = sorted(set(updated_rows))
                self.log(f"   • Номера обновленных строк: {unique_rows[:10]}{'...' if len(unique_rows) > 10 else ''}")

            # Активировать кнопку открытия файла
            self.open_file_btn.config(state=tk.NORMAL)

            messagebox.showinfo(
                "Успех",
                f"✅ Обработка завершена!\n\nОбработано файлов: {len(self.selected_files)}\nНайдено соответствий: {matched_count}\nОбновлено строк: {len(set(updated_rows))}\n\nРезультат: {new_filename}\n\nНажмите '📂 Открыть готовый файл'"
            )

        except Exception as e:
            self.log(f"\n❌ ОШИБКА: {e}")
            import traceback
            self.log(f"   Подробности: {traceback.format_exc()}")
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{e}")

        finally:
            # Всегда разблокируем кнопку после завершения (успешного или с ошибкой)
            self.is_processing = False
            self.process_btn.config(state=tk.NORMAL, text="🚀 НАЧАТЬ ОБРАБОТКУ", bg="#27ae60")

    def smart_data_mapping(self, extracted_text, template_headers, file_path):
        """
        Использует AI для умного размещения данных в колонки шаблона

        Returns:
            dict: {"data": {column_name: value}, "explanation": "..."}
        """
        self.log("   🧠 Запрос к AI для анализа структуры...")

        # Формируем промпт для AI
        headers_list = '\n'.join([f'  - "{h}"' for h in template_headers])

        prompt = f"""Ты - ассистент для заполнения таблиц аудита.

ЗАДАЧА: Извлеки из текста информацию и размести её в колонки таблицы.

КОЛОНКИ ТАБЛИЦЫ:
{headers_list}

ИЗВЛЕЧЕННЫЙ ТЕКСТ (из файла "{os.path.basename(file_path)}"):
---
{extracted_text[:2500]}
---

ИНСТРУКЦИИ:
1. Проанализируй текст
2. Определи, какая информация подходит для каждой колонки
3. Извлеки релевантные данные
4. Верни ТОЛЬКО JSON, БЕЗ дополнительного текста

ФОРМАТ ОТВЕТА (верни ТОЛЬКО это, без объяснений до или после):
{{
  "data": {{
    "Точное название колонки 1": "извлеченное значение",
    "Точное название колонки 2": "извлеченное значение"
  }},
  "explanation": "Объяснение размещения в 1-2 предложениях"
}}

ВАЖНО: Используй ТОЧНЫЕ названия колонок из списка выше!"""

        try:
            response = self.query_ollama(prompt)

            if not response or len(response.strip()) < 10:
                self.log("   ⚠️ AI вернул пустой ответ")
                return self.fallback_mapping(extracted_text, template_headers, file_path)

            # Логируем первые 200 символов ответа для отладки
            self.log(f"   AI ответ (начало): {response[:200]}...")

            # Попытка распарсить JSON из ответа
            import re

            # Ищем JSON в ответе (более гибко)
            json_match = re.search(r'\{[\s\S]*?"data"[\s\S]*?\}[\s\S]*?\}', response)

            if not json_match:
                # Пытаемся найти любой JSON объект
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response)

            if json_match:
                try:
                    json_str = json_match.group(0)
                    result = json.loads(json_str)

                    # Проверяем что JSON имеет правильную структуру
                    if "data" in result and isinstance(result["data"], dict):
                        data_count = len(result.get('data', {}))
                        self.log(f"   ✓ AI определил размещение для {data_count} колонок")

                        # Показываем какие колонки заполнены
                        for col in list(result["data"].keys())[:3]:
                            self.log(f"     - {col}")
                        if data_count > 3:
                            self.log(f"     ... и еще {data_count - 3} колонок")

                        return result
                    else:
                        self.log("   ⚠️ JSON не содержит поле 'data'")
                        return self.fallback_mapping(extracted_text, template_headers, file_path)

                except json.JSONDecodeError as je:
                    self.log(f"   ⚠️ Ошибка парсинга JSON: {je}")
                    self.log(f"   JSON строка: {json_str[:200]}...")
                    return self.fallback_mapping(extracted_text, template_headers, file_path)
            else:
                self.log("   ⚠️ JSON не найден в ответе AI")
                self.log(f"   Полный ответ: {response[:500]}...")
                return self.fallback_mapping(extracted_text, template_headers, file_path)

        except Exception as e:
            self.log(f"   ⚠️ Ошибка AI-анализа: {e}")
            import traceback
            self.log(f"   Трейсбек: {traceback.format_exc()[:300]}")
            return self.fallback_mapping(extracted_text, template_headers, file_path)

    def fallback_mapping(self, text, headers, file_path):
        """Базовое размещение данных при недоступности AI"""
        mapping = {"data": {}, "explanation": "Автоматическое размещение (AI недоступен)"}

        # Универсальный подход: размещаем данные в первые доступные колонки
        # Обычно первая колонка - номер/имя файла, вторая - содержимое/комментарии

        if len(headers) >= 1:
            # Первая колонка - обычно для краткой информации или названия
            first_col = headers[0]
            # Помещаем имя файла или первые 100 символов
            mapping["data"][first_col] = f"Файл: {os.path.basename(file_path)[:50]}"

        if len(headers) >= 2:
            # Вторая колонка - обычно для основного содержимого
            second_col = headers[1]
            # Помещаем весь распознанный текст
            mapping["data"][second_col] = text[:2000]  # Ограничим 2000 символами

        # Дополнительно: пытаемся найти специфичные колонки по ключевым словам
        for header in headers:
            header_lower = header.lower()

            # Если находим колонку с ключевыми словами
            if any(keyword in header_lower for keyword in ["комментари", "примечани", "описани", "текст", "содержан"]):
                if header not in mapping["data"]:  # Если еще не заполнили
                    mapping["data"][header] = text[:1500]

            elif any(keyword in header_lower for keyword in ["файл", "документ", "название", "источник"]):
                if header not in mapping["data"]:
                    mapping["data"][header] = os.path.basename(file_path)

        # Обновляем объяснение с информацией о размещении
        filled_cols = list(mapping["data"].keys())
        if filled_cols:
            mapping["explanation"] = f"Автоматическое размещение (AI недоступен). Данные размещены в колонки: {', '.join(filled_cols[:3])}{'...' if len(filled_cols) > 3 else ''}"

        return mapping

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
                import numpy as np
                from PIL import Image

                self.log("   🔍 Запуск OCR распознавания...")

                # Проверка существования файла
                if not os.path.exists(file_path):
                    self.log(f"   ❌ Файл не найден: {file_path}")
                    return "Ошибка: файл не найден"

                # Попытка открыть изображение через PIL (работает с кириллицей)
                try:
                    img = Image.open(file_path)
                    img_array = np.array(img)
                    self.log(f"   📷 Изображение загружено: {img.size[0]}x{img.size[1]} пикселей")
                except Exception as img_err:
                    self.log(f"   ❌ Не удалось открыть изображение: {img_err}")
                    return f"Ошибка: не удалось открыть изображение - {img_err}"

                self.log("   ⏳ Загрузка модели EasyOCR (первый запуск может занять время)...")
                reader = easyocr.Reader(['ru', 'en'], gpu=False, verbose=False)

                # Используем массив numpy вместо пути к файлу
                result = reader.readtext(img_array, detail=0)
                text = "\n".join(result)

                if text.strip():
                    self.log(f"   📝 Распознано {len(text)} символов")
                else:
                    self.log("   ⚠️ Текст не распознан (пустое изображение или нет текста)")
                    text = "(Текст не обнаружен на изображении)"

                return text

            except ImportError as ie:
                self.log("   ⚠️ EasyOCR или зависимости не установлены")
                self.log(f"   Детали: {ie}")
                self.log("   Установите: pip install easyocr pillow")
                return "⚠️ OCR недоступен: установите easyocr и pillow"
            except Exception as e:
                self.log(f"   ❌ Ошибка OCR: {e}")
                import traceback
                self.log(f"   Подробности: {traceback.format_exc()}")
                return f"Ошибка OCR: {e}"

        return "Неподдерживаемый формат файла"



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
