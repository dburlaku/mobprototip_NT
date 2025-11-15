// OCR Module для распознавания документов с улучшенной обработкой
// Использует Tesseract.js для распознавания текста из изображений

class DocumentOCR {
    constructor() {
        this.worker = null;
        this.isInitialized = false;
        this.recognizedDocuments = [];
        this.questions = [];
    }

    /**
     * Инициализация Tesseract OCR Worker
     */
    async initialize() {
        if (this.isInitialized) return;

        try {
            console.log('Инициализация Tesseract OCR...');
            this.worker = await Tesseract.createWorker('rus', 1, {
                logger: (m) => {
                    console.log(m);
                    this.updateProgress(m);
                }
            });

            // Настройки для улучшенного распознавания русского текста
            await this.worker.setParameters({
                tessedit_char_whitelist: 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя0123456789.,!?;:()№«»-–—— /\\',
                preserve_interword_spaces: '1',
                tessedit_pageseg_mode: Tesseract.PSM.AUTO_OSD,
            });

            this.isInitialized = true;
            console.log('Tesseract OCR инициализирован успешно');
        } catch (error) {
            console.error('Ошибка при инициализации OCR:', error);
            throw error;
        }
    }

    /**
     * Обновление прогресса распознавания
     */
    updateProgress(m) {
        const progressBar = document.getElementById('ocrProgress');
        const progressText = document.getElementById('ocrProgressText');

        if (m.status === 'recognizing text') {
            const percent = Math.round(m.progress * 100);
            if (progressBar) {
                progressBar.style.width = percent + '%';
                progressBar.textContent = percent + '%';
            }
            if (progressText) {
                progressText.textContent = `Распознавание: ${percent}%`;
            }
        }
    }

    /**
     * Предварительная обработка изображения для улучшения качества OCR
     */
    async preprocessImage(file) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');

            img.onload = () => {
                // Увеличиваем разрешение для лучшего распознавания
                const scale = 2;
                canvas.width = img.width * scale;
                canvas.height = img.height * scale;

                // Применяем фильтры для улучшения контраста
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

                // Увеличение контраста и резкости
                const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                const data = imageData.data;

                // Бинаризация для улучшения читаемости текста
                for (let i = 0; i < data.length; i += 4) {
                    const brightness = (data[i] + data[i + 1] + data[i + 2]) / 3;
                    const value = brightness > 128 ? 255 : 0;
                    data[i] = data[i + 1] = data[i + 2] = value;
                }

                ctx.putImageData(imageData, 0, 0);

                canvas.toBlob((blob) => {
                    resolve(blob);
                }, 'image/png', 1.0);
            };

            img.onerror = reject;
            img.src = URL.createObjectURL(file);
        });
    }

    /**
     * Распознавание текста из изображения
     */
    async recognizeDocument(file) {
        if (!this.isInitialized) {
            await this.initialize();
        }

        try {
            console.log('Начало распознавания документа:', file.name);

            // Показываем индикатор загрузки
            this.showLoadingIndicator();

            // Предобработка изображения
            const processedImage = await this.preprocessImage(file);

            // Распознавание текста
            const result = await this.worker.recognize(processedImage);

            // Постобработка текста для исправления ошибок и улучшения качества
            const processedText = this.postprocessText(result.data.text);

            // Сохраняем результат
            const document = {
                id: Date.now(),
                fileName: file.name,
                originalText: result.data.text,
                processedText: processedText,
                confidence: result.data.confidence,
                timestamp: new Date().toISOString(),
                blocks: this.extractTextBlocks(result.data),
                metadata: this.extractMetadata(processedText)
            };

            this.recognizedDocuments.push(document);

            console.log('Распознавание завершено. Уверенность:', result.data.confidence);
            console.log('Распознанный текст:', processedText);

            // Скрываем индикатор загрузки
            this.hideLoadingIndicator();

            return document;
        } catch (error) {
            console.error('Ошибка при распознавании документа:', error);
            this.hideLoadingIndicator();
            throw error;
        }
    }

    /**
     * Постобработка распознанного текста
     * Исправляет типичные ошибки OCR и улучшает форматирование
     */
    postprocessText(text) {
        if (!text) return '';

        let processed = text;

        // Удаляем лишние пробелы и переносы строк
        processed = processed.replace(/\s+/g, ' ').trim();

        // Восстанавливаем параграфы (двойные переносы строк)
        processed = processed.replace(/\.\s+([А-ЯA-Z])/g, '.\n\n$1');

        // Исправляем типичные ошибки OCR для русского языка
        const corrections = {
            'О О О': 'ООО',
            'П Р И К А З': 'ПРИКАЗ',
            'У Д О С Т О В Е Р Е Н И Е': 'УДОСТОВЕРЕНИЕ',
            'А К А Д Е М И Я': 'АКАДЕМИЯ',
            'Т Е Х Н И Ч Е С К А Я': 'ТЕХНИЧЕСКАЯ',
            '№ N': '№',
            'o': '0', // латинская o на цифру 0
            'O': '0',
            'l': '1', // латинская l на цифру 1
            'I': '1',
        };

        for (const [wrong, correct] of Object.entries(corrections)) {
            processed = processed.replace(new RegExp(wrong, 'g'), correct);
        }

        // Восстанавливаем правильное форматирование дат
        processed = processed.replace(/(\d{2})\s*\.\s*(\d{2})\s*\.\s*(\d{4})/g, '$1.$2.$3');

        // Убираем артефакты распознавания
        processed = processed.replace(/[|_~`]/g, '');

        // Восстанавливаем кавычки
        processed = processed.replace(/["]/g, '«');
        processed = processed.replace(/[«]([^»]+)$/g, '«$1»');

        return processed;
    }

    /**
     * Извлечение текстовых блоков с позиционированием
     */
    extractTextBlocks(data) {
        const blocks = [];

        if (data.blocks) {
            data.blocks.forEach((block, index) => {
                blocks.push({
                    id: index,
                    text: block.text,
                    confidence: block.confidence,
                    bbox: block.bbox,
                    // Определяем тип блока (заголовок, параграф, список)
                    type: this.detectBlockType(block.text)
                });
            });
        }

        return blocks;
    }

    /**
     * Определение типа текстового блока
     */
    detectBlockType(text) {
        if (!text) return 'paragraph';

        const upperCaseRatio = (text.match(/[А-ЯA-Z]/g) || []).length / text.length;

        if (upperCaseRatio > 0.7) return 'heading';
        if (text.match(/^[•\-\d]+\./)) return 'list';
        if (text.match(/^\d{2}\.\d{2}\.\d{4}/)) return 'date';
        if (text.match(/^№\s*\d+/)) return 'number';

        return 'paragraph';
    }

    /**
     * Извлечение метаданных из документа
     */
    extractMetadata(text) {
        const metadata = {
            organization: null,
            docType: null,
            docNumber: null,
            docDate: null,
            persons: [],
            keywords: []
        };

        // Извлечение названия организации
        const orgMatch = text.match(/(?:Общество с ограниченной ответственностью|ООО)\s*[«"]?([^»"]+)[»"]?/i);
        if (orgMatch) {
            metadata.organization = orgMatch[1].trim();
        }

        // Извлечение типа документа
        const docTypes = ['ПРИКАЗ', 'УДОСТОВЕРЕНИЕ', 'СПРАВКА', 'АКТ', 'ПРОТОКОЛ', 'ДОГОВОР'];
        for (const type of docTypes) {
            if (text.includes(type)) {
                metadata.docType = type;
                break;
            }
        }

        // Извлечение номера документа
        const numberMatch = text.match(/№\s*(\d+[\d\/\-]*)/);
        if (numberMatch) {
            metadata.docNumber = numberMatch[1];
        }

        // Извлечение даты документа
        const dateMatch = text.match(/(\d{2}\.\d{2}\.\d{4})/);
        if (dateMatch) {
            metadata.docDate = dateMatch[1];
        }

        // Извлечение имен (ФИО)
        const namePattern = /([А-ЯЁ][а-яё]+)\s+([А-ЯЁ][а-яё]+)\s+([А-ЯЁ][а-яё]+)/g;
        let nameMatch;
        while ((nameMatch = namePattern.exec(text)) !== null) {
            metadata.persons.push(nameMatch[0]);
        }

        // Извлечение ключевых слов
        const keywords = ['обучение', 'безопасность', 'культура', 'аудит', 'ремонт', 'техническое обслуживание'];
        keywords.forEach(keyword => {
            if (text.toLowerCase().includes(keyword)) {
                metadata.keywords.push(keyword);
            }
        });

        return metadata;
    }

    /**
     * Умное сопоставление вопросов с документами
     */
    async matchQuestionsToDocument(document, questions) {
        const matches = [];

        for (const question of questions) {
            const score = this.calculateRelevanceScore(question, document);

            if (score > 0.3) { // Порог релевантности
                const answer = this.extractAnswer(question, document);
                matches.push({
                    question: question,
                    answer: answer,
                    relevanceScore: score,
                    confidence: document.confidence,
                    source: {
                        fileName: document.fileName,
                        documentId: document.id
                    }
                });
            }
        }

        // Сортируем по релевантности
        matches.sort((a, b) => b.relevanceScore - a.relevanceScore);

        return matches;
    }

    /**
     * Расчет релевантности вопроса к документу
     */
    calculateRelevanceScore(question, document) {
        const questionLower = question.toLowerCase();
        const textLower = document.processedText.toLowerCase();

        let score = 0;

        // Ключевые слова из вопроса
        const questionKeywords = this.extractKeywords(questionLower);

        // Проверяем наличие ключевых слов в тексте
        for (const keyword of questionKeywords) {
            if (textLower.includes(keyword)) {
                score += 0.2;
            }
        }

        // Проверяем совпадение с метаданными
        if (document.metadata) {
            if (questionLower.includes('организация') && document.metadata.organization) {
                score += 0.3;
            }
            if (questionLower.includes('документ') && document.metadata.docType) {
                score += 0.2;
            }
            if (questionLower.includes('дата') && document.metadata.docDate) {
                score += 0.3;
            }

            // Проверяем ключевые слова
            for (const keyword of document.metadata.keywords) {
                if (questionLower.includes(keyword)) {
                    score += 0.25;
                }
            }
        }

        return Math.min(score, 1.0); // Ограничиваем максимальный score
    }

    /**
     * Извлечение ключевых слов из вопроса
     */
    extractKeywords(question) {
        // Удаляем стоп-слова
        const stopWords = ['есть', 'ли', 'какие', 'что', 'как', 'когда', 'где', 'кто', 'почему', 'зачем'];

        const words = question.split(/\s+/);
        const keywords = words.filter(word =>
            word.length > 3 &&
            !stopWords.includes(word) &&
            !/^[.,!?;:]$/.test(word)
        );

        return keywords;
    }

    /**
     * Извлечение ответа на вопрос из документа
     */
    extractAnswer(question, document) {
        const questionLower = question.toLowerCase();
        const text = document.processedText;
        const sentences = text.split(/[.!?]\s+/);

        // Поиск наиболее релевантного предложения
        let bestMatch = '';
        let bestScore = 0;

        for (const sentence of sentences) {
            const sentenceLower = sentence.toLowerCase();
            const keywords = this.extractKeywords(questionLower);

            let score = 0;
            for (const keyword of keywords) {
                if (sentenceLower.includes(keyword)) {
                    score++;
                }
            }

            if (score > bestScore) {
                bestScore = score;
                bestMatch = sentence;
            }
        }

        // Если нашли совпадение, возвращаем контекст
        if (bestMatch) {
            const index = sentences.indexOf(bestMatch);
            const context = sentences.slice(Math.max(0, index - 1), Math.min(sentences.length, index + 2)).join('. ');
            return context;
        }

        // Если не нашли точного совпадения, возвращаем релевантные метаданные
        if (document.metadata) {
            let metadataAnswer = '';

            if (questionLower.includes('организация') && document.metadata.organization) {
                metadataAnswer += `Организация: ${document.metadata.organization}. `;
            }
            if (questionLower.includes('тип') && document.metadata.docType) {
                metadataAnswer += `Тип документа: ${document.metadata.docType}. `;
            }
            if (questionLower.includes('номер') && document.metadata.docNumber) {
                metadataAnswer += `Номер: ${document.metadata.docNumber}. `;
            }
            if (questionLower.includes('дата') && document.metadata.docDate) {
                metadataAnswer += `Дата: ${document.metadata.docDate}. `;
            }

            if (metadataAnswer) {
                return metadataAnswer;
            }
        }

        return 'Информация не найдена в документе';
    }

    /**
     * Показать индикатор загрузки
     */
    showLoadingIndicator() {
        const indicator = document.getElementById('ocrLoadingIndicator');
        if (indicator) {
            indicator.style.display = 'block';
        }
    }

    /**
     * Скрыть индикатор загрузки
     */
    hideLoadingIndicator() {
        const indicator = document.getElementById('ocrLoadingIndicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
    }

    /**
     * Получить все распознанные документы
     */
    getRecognizedDocuments() {
        return this.recognizedDocuments;
    }

    /**
     * Очистка ресурсов
     */
    async cleanup() {
        if (this.worker) {
            await this.worker.terminate();
            this.worker = null;
            this.isInitialized = false;
        }
    }
}

// Экспорт для использования в других модулях
window.DocumentOCR = DocumentOCR;
