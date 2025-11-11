// Nadi - JavaScript для интерактивных сценариев (обновленная версия)

// Состояние приложения
const appState = {
    currentScreen: 'splash',
    previousScreens: [],
    userType: null, // 'new', 'returning', 'advanced'
    userName: 'Дмитрий',
    selectedTheme: null,
    uploadedPhotos: [],
    chatMessages: [],
    exchangeCount: 0,
    timeCount: 0,
    isVoiceActive: false,
    memories: [],
    photosCount: 0,
    storiesCount: 0
};

// Темы для диалогов
const themes = {
    home: {
        name: 'Семейный очаг',
        questions: [
            'Расскажите о доме, где вы выросли. Какой он был?',
            'Какие запахи и звуки вы помните из детства?',
            'Было ли у вас особое место в доме, где вы любили проводить время?',
            'Расскажите о семейных традициях в вашем доме',
            'Какие истории связаны с вашим домом?'
        ]
    },
    childhood: {
        name: 'Детство под солнцем',
        questions: [
            'Расскажите, какое воспоминание из детства всплывает первым?',
            'Как часто вы занимались этим?',
            'Кто был с вами в те моменты?',
            'Какие эмоции вы испытывали?',
            'Есть ли какие-то особенные детали, которые вы помните?'
        ]
    },
    family: {
        name: 'Сила рода',
        questions: [
            'Расскажите о своих предках. Что вы о них знаете?',
            'Какие семейные истории передавались из поколения в поколение?',
            'Кто из родственников оказал на вас наибольшее влияние?',
            'Какие черты характера или таланты передаются в вашей семье?',
            'Какое наследие вы хотите оставить следующим поколениям?'
        ]
    },
    happiness: {
        name: 'Моменты счастья',
        questions: [
            'Какой момент в жизни вы вспоминаете с особой теплотой?',
            'Что делало этот момент особенным?',
            'Кто был рядом с вами?',
            'Как вы себя чувствовали?',
            'Что бы вы хотели сказать себе в тот момент, зная то, что знаете сейчас?'
        ]
    }
};

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOMContentLoaded fired');

    // Splash screen теперь постоянная главная страница, не проверяем localStorage
    console.log('Showing splash screen as main page');

    // Добавляем обработчик для кнопки "Начать" напрямую
    const startBtn = document.querySelector('.splash-start-btn');
    if (startBtn) {
        console.log('Start button found, adding listener');
        startBtn.addEventListener('click', function(e) {
            console.log('Button clicked via event listener');
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
            startFromSplash();
        }, { once: false });
    } else {
        console.error('Start button not found!');
    }

    // Таймер для чата
    setInterval(() => {
        if (appState.currentScreen === 'chat' && appState.chatMessages.length > 0) {
            appState.timeCount++;
            updateChatStatus();
        }
    }, 60000); // Каждую минуту
});

// Клик на splash screen (старая функция для совместимости)
function splashClick() {
    startFromSplash();
}

// Флаг для предотвращения множественных вызовов
let isTransitioning = false;

// Начать работу со splash screen
function startFromSplash() {
    console.log('startFromSplash called, isTransitioning:', isTransitioning);

    // Если уже выполняется переход, игнорируем повторные вызовы
    if (isTransitioning) {
        console.log('Already transitioning, ignoring call');
        return;
    }

    isTransitioning = true;
    console.log('Starting transition to scenarioSelect');

    try {
        showScreen('scenarioSelect');
        console.log('showScreen completed');

        // Сбрасываем флаг через задержку
        setTimeout(() => {
            isTransitioning = false;
            console.log('Transition flag reset');
        }, 1000);
    } catch (error) {
        isTransitioning = false;
        console.error('Error in startFromSplash:', error);
        alert('Ошибка: ' + error.message);
    }
}

// Вернуться к splash screen (главная страница)
function goToSplash() {
    appState.previousScreens = [];
    showScreen('splash');
    // Закрыть меню если оно открыто
    const menu = document.getElementById('sideMenu');
    const overlay = document.getElementById('menuOverlay');
    if (menu && menu.classList.contains('active')) {
        menu.classList.remove('active');
        overlay.classList.remove('active');
    }
}

// Навигация между экранами
function showScreen(screenId) {
    console.log('showScreen called with:', screenId);

    // Скрыть все экраны
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
        console.log('Removed active from:', screen.id);
    });

    // Показать нужный экран
    const screen = document.getElementById(screenId);
    if (screen) {
        console.log('Screen found:', screenId, 'adding active class');
        screen.classList.add('active');
        if (appState.currentScreen !== screenId) {
            appState.previousScreens.push(appState.currentScreen);
        }
        appState.currentScreen = screenId;

        // Обновить welcome экран при его показе
        if (screenId === 'welcome') {
            updateWelcomeScreen();
        }
        console.log('Current screen is now:', appState.currentScreen);
    } else {
        console.error('Screen not found:', screenId);
    }
}

function goBack() {
    if (appState.previousScreens.length > 0) {
        const previousScreen = appState.previousScreens.pop();
        showScreen(previousScreen);
    } else {
        showScreen('welcome');
    }
}

function goToScenarios() {
    appState.previousScreens = [];
    showScreen('scenarioSelect');
    // Закрыть меню если оно открыто
    const menu = document.getElementById('sideMenu');
    const overlay = document.getElementById('menuOverlay');
    if (menu && menu.classList.contains('active')) {
        menu.classList.remove('active');
        overlay.classList.remove('active');
    }
}

function backToWelcome() {
    appState.previousScreens = [];
    showScreen('welcome');
}

// Выбор сценария тестирования
function selectScenario(scenarioType) {
    appState.userType = scenarioType;

    if (scenarioType === 'new') {
        // Новый пользователь - показываем экран регистрации
        localStorage.setItem('nadiUserType', 'new');
        localStorage.removeItem('nadiUserName');
        showScreen('registration');
    } else if (scenarioType === 'returning') {
        // Возвращающийся пользователь - предлагаем продолжить или начать новую
        localStorage.setItem('nadiUserType', 'returning');
        localStorage.setItem('nadiUserName', 'Дмитрий');
        appState.userName = 'Дмитрий';
        showScreen('welcome');
        updateWelcomeScreen();
    } else if (scenarioType === 'advanced') {
        // Продвинутый пользователь - развиваем существующую историю
        localStorage.setItem('nadiUserType', 'advanced');
        localStorage.setItem('nadiUserName', 'Дмитрий');
        appState.userName = 'Дмитрий';
        appState.storiesCount = 5;
        appState.photosCount = 15;
        showScreen('welcome');
        updateWelcomeScreen();
    }
}

// Обновление welcome экрана в зависимости от типа пользователя
function updateWelcomeScreen() {
    const userType = appState.userType || localStorage.getItem('nadiUserType');
    const userName = appState.userName || localStorage.getItem('nadiUserName') || 'друг';
    const title = document.getElementById('welcomeTitle');
    const text = document.getElementById('welcomeText');
    const hint = document.getElementById('welcomeHint');
    const advancedTopics = document.getElementById('advancedUserTopics');
    const mainAction = document.getElementById('mainAction');

    if (userType === 'new') {
        // Новый пользователь
        title.textContent = `👋 Приятно познакомиться, ${userName}!`;
        text.textContent = 'Я помогу вам сохранить воспоминания. Начнем с простого разговора — я задам несколько вопросов, а потом создам из ваших ответов красивую историю.';
        hint.textContent = 'Это просто! Я буду задавать вопросы, вы отвечайте';
        advancedTopics.style.display = 'none';
        mainAction.style.display = 'block';
    } else if (userType === 'returning') {
        // Возвращающийся пользователь
        title.textContent = `👋 Рады видеть вас снова, ${appState.userName}!`;
        text.textContent = 'Продолжим создавать ваши истории? Начните новый разговор или просмотрите уже созданные воспоминания.';
        hint.textContent = 'Начните новую историю или продолжите существующую';
        advancedTopics.style.display = 'none';
        mainAction.style.display = 'block';
    } else if (userType === 'advanced') {
        // Продвинутый пользователь
        title.textContent = `✨ С возвращением, ${appState.userName}!`;
        text.textContent = `У вас уже есть ${appState.storiesCount} историй и ${appState.photosCount} фотографий. Давайте продолжим развивать вашу коллекцию воспоминаний!`;
        // Показываем темы для продвинутого пользователя
        advancedTopics.style.display = 'block';
        mainAction.style.display = 'none';
    }
}

// Бургер-меню
function toggleMenu() {
    const menu = document.getElementById('sideMenu');
    const overlay = document.getElementById('menuOverlay');

    menu.classList.toggle('active');
    overlay.classList.toggle('active');
}

function newChat() {
    toggleMenu();
    showScreen('themes');
}

function showMediaFiles() {
    toggleMenu();
    showScreen('mediaFiles');
}

function showArtifacts() {
    toggleMenu();
    showScreen('artifacts');
}

function showNadiStats() {
    toggleMenu();
    showScreen('nadiStats');
}

function showChatList() {
    toggleMenu();
    showScreen('chatList');
}

function showResult() {
    generateStory();
    showScreen('fullStoryPage');
}

function showAccount() {
    toggleMenu();
    showScreen('account');
}

function showAbout() {
    if (appState.currentScreen === 'scenarioSelect') {
        showScreen('about');
    } else {
        toggleMenu();
        showScreen('about');
    }
}

// Модальные окна
function showInfo() {
    document.getElementById('infoModal').classList.add('active');
}

function closeInfo() {
    document.getElementById('infoModal').classList.remove('active');
}

// Начать рассказывать историю
function startStory() {
    showScreen('themes');
}

// Выбор темы
function selectTheme(themeId) {
    appState.selectedTheme = themeId;
    const theme = themes[themeId];

    // Очистить предыдущие сообщения
    appState.chatMessages = [];
    appState.exchangeCount = 0;
    appState.timeCount = 0;

    // Очистить чат
    document.getElementById('chatMessages').innerHTML = '';

    // Показать экран чата
    showScreen('chat');

    // Начать диалог
    setTimeout(() => {
        addNadiMessage(
            `Отличный выбор! ${theme.questions[0]}`,
            'Можете ответить голосом или текстом'
        );

        // Добавляем подсказку о фотографии после первого вопроса
        setTimeout(() => {
            addNadiMessage(
                '💡 Кстати, вы можете добавить фотографии к вашему рассказу — это сделает историю еще более живой и качественной!',
                'Нажмите на 📎 чтобы прикрепить фото'
            );
        }, 2000);
    }, 500);
}

function customTheme() {
    const customThemeName = prompt('Введите название темы:');
    if (customThemeName) {
        appState.selectedTheme = 'custom';

        appState.chatMessages = [];
        appState.exchangeCount = 0;
        appState.timeCount = 0;
        document.getElementById('chatMessages').innerHTML = '';

        showScreen('chat');

        setTimeout(() => {
            addNadiMessage(
                `"${customThemeName}" — замечательная тема! Расскажите, что вы хотите вспомнить?`,
                'Можете ответить голосом или текстом'
            );

            // Добавляем подсказку о фотографии
            setTimeout(() => {
                addNadiMessage(
                    '💡 Кстати, вы можете добавить фотографии к вашему рассказу — это сделает историю еще более живой и качественной!',
                    'Нажмите на 📎 чтобы прикрепить фото'
                );
            }, 2000);
        }, 500);
    }
}

// Чат
function addNadiMessage(text, hint = null) {
    const chatMessages = document.getElementById('chatMessages');

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message nadi';

    messageDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div>
            <div class="message-bubble">
                ${text}
                ${hint ? `<div class="message-hint">💬 ${hint}</div>` : ''}
            </div>
            <div class="message-time">${getCurrentTime()}</div>
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    appState.chatMessages.push({ type: 'nadi', text, time: getCurrentTime() });
}

function addUserMessage(text) {
    const chatMessages = document.getElementById('chatMessages');

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user';

    messageDiv.innerHTML = `
        <div class="message-avatar">👤</div>
        <div>
            <div class="message-bubble">${text}</div>
            <div class="message-time">${getCurrentTime()}</div>
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    appState.chatMessages.push({ type: 'user', text, time: getCurrentTime() });
    appState.exchangeCount++;
    updateChatStatus();
}

function showTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');

    const typingDiv = document.createElement('div');
    typingDiv.className = 'message nadi typing-message';
    typingDiv.id = 'typingIndicator';

    typingDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div>
            <div class="message-bubble">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        </div>
    `;

    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function sendMessage() {
    const input = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const text = input.value.trim();

    if (text) {
        addUserMessage(text);
        input.value = '';

        // Скрыть кнопку отправки после отправки
        if (sendButton) {
            sendButton.classList.remove('visible');
        }

        // Показать индикатор печатания
        showTypingIndicator();

        // Через 2 секунды ответить
        setTimeout(() => {
            removeTypingIndicator();
            respondToUser(text);
        }, 2000);
    }
}

function respondToUser(userText) {
    const theme = themes[appState.selectedTheme];
    let response = '';

    if (theme && appState.exchangeCount <= theme.questions.length) {
        const nextQuestion = theme.questions[appState.exchangeCount];
        if (nextQuestion) {
            response = getContextualResponse(userText) + ' ' + nextQuestion;
        } else {
            response = 'Замечательно! Кажется, мы собрали все о этой теме. Хотите что-то добавить?';
        }
    } else {
        response = getContextualResponse(userText) + ' Расскажите об этом подробнее.';
    }

    addNadiMessage(response);
}

function getContextualResponse(userText) {
    const responses = [
        'Как интересно!',
        'Замечательно!',
        'Это очень трогательно',
        'Какое прекрасное воспоминание',
        'Я понимаю вас'
    ];
    return responses[Math.floor(Math.random() * responses.length)];
}

function updateChatStatus() {
    const totalQuestions = 10; // Общее количество вопросов для заполнения
    const progress = Math.min((appState.exchangeCount / totalQuestions) * 100, 100);

    // Обновляем прогресс-бар
    const progressBarFill = document.getElementById('progressBarFill');
    const progressPercentage = document.getElementById('progressPercentage');

    if (progressBarFill) {
        progressBarFill.style.width = progress + '%';
    }

    if (progressPercentage) {
        progressPercentage.textContent = Math.round(progress) + '%';
    }

    // Кнопка истории всегда видима, но активна после 50% прогресса (5 ответов)
    const historyButton = document.getElementById('historyButton');
    if (historyButton) {
        historyButton.style.display = 'block';
        if (appState.exchangeCount >= 5) {
            historyButton.disabled = false;
            historyButton.style.opacity = '1';
            historyButton.classList.add('animated');
        } else {
            historyButton.disabled = true;
            historyButton.style.opacity = '0.5';
            historyButton.classList.remove('animated');
        }
    }
}

function getCurrentTime() {
    const now = new Date();
    return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
}

// Голосовой ввод
function toggleVoice() {
    if (appState.isVoiceActive) {
        stopVoice();
    } else {
        startVoice();
    }
}

function startVoice() {
    appState.isVoiceActive = true;
    document.getElementById('voiceIndicator').classList.add('active');

    // Имитация голосового ввода
    setTimeout(() => {
        const simulatedText = 'Помню, как мы с дедом ходили на рыбалку каждое лето...';
        const userInput = document.getElementById('userInput');
        const sendButton = document.getElementById('sendButton');

        userInput.value = simulatedText;

        // Показать кнопку отправки после голосового ввода
        if (sendButton) {
            sendButton.classList.add('visible');
        }

        stopVoice();
    }, 3000);
}

function stopVoice() {
    appState.isVoiceActive = false;
    document.getElementById('voiceIndicator').classList.remove('active');
}

// Прикрепление файлов в чате
function attachFile() {
    document.getElementById('fileInput').click();
}

function handleFileUpload(event) {
    const files = event.target.files;
    if (files.length > 0) {
        const file = files[0];
        appState.uploadedPhotos.push(file);

        // Добавить сообщение о загруженном файле
        addUserMessage(`[Фото загружено: ${file.name}]`);

        // Nadi отвечает на фото
        setTimeout(() => {
            showTypingIndicator();
            setTimeout(() => {
                removeTypingIndicator();
                addNadiMessage('Какая замечательная фотография! Расскажите, что на ней изображено и когда это было?');
            }, 2000);
        }, 500);
    }
}

// Действия в чате
function finishChat() {
    showScreen('result');
    generateStory();
}

function showChatMenu() {
    alert('Меню чата (в разработке)');
}

// Генерация истории
function generateStory() {
    const storyTitle = document.getElementById('storyTitle');
    const storyPreview = document.getElementById('storyPreview');

    // Генерация заголовка на основе темы
    const theme = themes[appState.selectedTheme];
    if (theme) {
        storyTitle.textContent = `📖 ${theme.name}`;
    }

    // Генерация превью истории
    const userMessages = appState.chatMessages
        .filter(msg => msg.type === 'user')
        .map(msg => msg.text)
        .join(' ');

    if (userMessages) {
        storyPreview.innerHTML = `<p>"${userMessages.substring(0, 200)}..."</p>`;
    }

    // Обновить статистику
    document.getElementById('wordsCount').textContent = userMessages.split(' ').length;
    document.getElementById('imagesCount').textContent = appState.uploadedPhotos.length;
    document.getElementById('durationCount').textContent = appState.timeCount || 8;
}

function readFull() {
    // Собрать полную историю
    const userMessages = appState.chatMessages
        .filter(msg => msg.type === 'user')
        .map(msg => msg.text);

    document.getElementById('fullStoryContent').innerHTML =
        userMessages.map(msg => `<p>${msg}</p>`).join('');

    showScreen('fullStoryPage');
}

function closeFullStory() {
    showScreen('chat');
}

function continueEditing() {
    // Возвращаемся к чату для продолжения диалога
    showScreen('chat');
}

// Редактирование истории
function editStory() {
    toggleEditStory();
}

function toggleEditStory() {
    const storyText = document.getElementById('fullStoryContent');
    const editButton = document.getElementById('editButton');
    const isEditable = storyText.getAttribute('contenteditable') === 'true';

    if (isEditable) {
        // Сохранить изменения
        storyText.setAttribute('contenteditable', 'false');
        if (editButton) {
            editButton.textContent = '✏️ Редактировать';
            editButton.classList.remove('editing');
        }
        alert('История сохранена!');
    } else {
        // Включить режим редактирования
        storyText.setAttribute('contenteditable', 'true');
        if (editButton) {
            editButton.textContent = '💾 Сохранить';
            editButton.classList.add('editing');
        }
        storyText.focus();
    }
}

// Изменение фото истории
function changeStoryPhoto() {
    // В полной версии здесь будет загрузка фото
    alert('Функция загрузки фото будет доступна в полной версии');
}

// Поделиться историей
function shareStory() {
    alert('Функция "Поделиться" будет доступна в полной версии');
}

function startNewStory() {
    showScreen('themes');
}

// Медиафайлы
function uploadMediaFile() {
    document.getElementById('fileInput').click();
}

// Артефакты
function viewArtifact(artifactType) {
    alert(`Просмотр артефакта "${artifactType}" будет доступен в полной версии`);
}

function viewRawMemories() {
    // В полной версии здесь будет показ списка всех записей
    alert('Просмотр записей воспоминаний будет доступен в полной версии.\n\nЗдесь вы увидите все ваши необработанные записи, заметки и тексты, которые можно будет использовать для создания новых историй со Сказочником.');
}

// Список чатов
function openChat(chatId) {
    // Переходим в режим общения с выбранным чатом
    // В полной версии здесь будет загрузка истории чата
    console.log('Открываем чат:', chatId);
    showScreen('chat');
}

// Аккаунт
function editProfile() {
    alert('Редактирование профиля будет доступно в полной версии');
}

function showSettings() {
    alert('Настройки будут доступны в полной версии');
}

function showSubscription() {
    alert('Управление подпиской будет доступно в полной версии');
}

function exportData() {
    alert('Экспорт данных будет доступен в полной версии');
}

function logout() {
    if (confirm('Вы уверены, что хотите выйти?')) {
        localStorage.clear();
        location.reload();
    }
}

// Обработка Enter в текстовом поле и динамический показ кнопки отправки
document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');

    if (userInput && sendButton) {
        // Обработка Enter
        userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Динамический показ кнопки отправки
        userInput.addEventListener('input', () => {
            const hasText = userInput.value.trim().length > 0;
            if (hasText) {
                sendButton.classList.add('visible');
            } else {
                sendButton.classList.remove('visible');
            }
        });
    }
});

// Переключение табов медиафайлов
document.addEventListener('DOMContentLoaded', () => {
    const mediaTabs = document.querySelectorAll('.media-tab');
    mediaTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Убрать active у всех
            mediaTabs.forEach(t => t.classList.remove('active'));
            // Добавить active к текущему
            tab.classList.add('active');

            // В реальном приложении здесь будет переключение контента
            const tabType = tab.dataset.tab;
            console.log('Выбран таб:', tabType);
        });
    });
});

// Регистрация нового пользователя
function completeRegistration() {
    const nameInput = document.getElementById('userName');
    const name = nameInput.value.trim();

    if (!name) {
        alert('Пожалуйста, введите ваше имя');
        nameInput.focus();
        return;
    }

    // Сохранить имя пользователя
    appState.userName = name;
    localStorage.setItem('nadiUserName', name);

    // Перейти на welcome screen
    showScreen('welcome');
    updateWelcomeScreen();
}

// Функция скрытия нового splash screen
function hideNewSplash() {
    const splash = document.getElementById('newSplashScreen');
    if (splash) {
        splash.classList.add('hidden');
    }
}

// Показать новый splash screen (для демонстрации)
function showNewSplash() {
    const splash = document.getElementById('newSplashScreen');
    if (splash) {
        splash.style.display = 'flex';
        splash.classList.remove('hidden');
    }
}

// Свайп для истории
let touchStartX = 0;
let touchEndX = 0;
let storyIndex = 0;

// Демо массив историй с данными
const stories = [
    {
        title: '📖 Рыбалка с дедом',
        content: [
            'Каждое лето, с июля до сентября, мы с дедом ходили на рыбалку. Помню, как однажды поймал щуку больше килограмма — дед так гордился. Он говорил, что в августе лучший клёв.',
            'Мы вставали рано утром, когда ещё солнце не взошло. Дед готовил снасти, а я помогал копать червей. Дорога до озера занимала около получаса пешком через лес.',
            'Больше всего я любил момент, когда поплавок начинал дёргаться. Дед учил меня терпению — не торопиться, дождаться правильного момента. Эти уроки остались со мной на всю жизнь.'
        ],
        tags: ['рыбалка', 'детство', 'дед', 'лето']
    },
    {
        title: '📖 Первый день в школе',
        content: [
            'Помню, как мама провожала меня в первый класс. Я держал её за руку так крепко, что побелели костяшки пальцев. Огромный портфель казался тяжелее меня самого.',
            'Наша первая учительница, Мария Ивановна, улыбалась так тепло, что страх сразу отступил. Она подарила каждому из нас по цветному карандашу и сказала, что мы будем рисовать свое будущее.',
            'К концу дня я уже подружился с Сашей, который сидел за соседней партой. Мы смеялись над одними и теми же шутками и не могли дождаться завтрашнего дня.'
        ],
        tags: ['школа', 'детство', 'друзья', 'первый раз']
    },
    {
        title: '📖 Бабушкины пироги',
        content: [
            'Каждое воскресенье бабушка пекла пироги. Запах дрожжевого теста и корицы наполнял весь дом ещё с утра. Я всегда просыпался от этого аромата.',
            'Она учила меня месить тесто, показывала, как правильно раскатывать и делать защипы. «Главное — делать с любовью», — говорила она. И правда, её пироги были самыми вкусными на свете.',
            'Теперь, когда я сам пеку, я всегда вспоминаю её руки в муке и добрую улыбку. Рецепт у меня сохранился, написанный её рукой на пожелтевшей бумаге.'
        ],
        tags: ['бабушка', 'семья', 'традиции', 'еда']
    }
];

function handleSwipe() {
    const swipeThreshold = 50;
    const diff = touchEndX - touchStartX;

    if (Math.abs(diff) > swipeThreshold) {
        if (diff > 0) {
            // Свайп вправо - предыдущая история
            navigateStory('prev');
        } else {
            // Свайп влево - следующая история
            navigateStory('next');
        }
    }
}

function navigateStory(direction) {
    const indicator = document.getElementById('swipeIndicator');

    if (direction === 'prev' && storyIndex > 0) {
        storyIndex--;
        updateStoryDisplay();
        showSwipeMessage(`← История ${storyIndex + 1} из ${stories.length}`);
    } else if (direction === 'next' && storyIndex < stories.length - 1) {
        storyIndex++;
        updateStoryDisplay();
        showSwipeMessage(`История ${storyIndex + 1} из ${stories.length} →`);
    } else if (direction === 'prev' && storyIndex === 0) {
        showSwipeMessage('Это первая история');
    } else if (direction === 'next' && storyIndex === stories.length - 1) {
        showSwipeMessage('Это последняя история');
    }
}

function updateStoryDisplay() {
    const story = stories[storyIndex];

    // Обновить заголовок
    const titleElement = document.getElementById('fullStoryTitle');
    if (titleElement) {
        titleElement.textContent = story.title;
    }

    // Обновить контент
    const contentElement = document.getElementById('fullStoryContent');
    if (contentElement) {
        contentElement.innerHTML = story.content.map(p => `<p>${p}</p>`).join('');
    }

    // Обновить теги
    const tagsContainer = document.querySelector('.tags-container');
    if (tagsContainer && story.tags) {
        tagsContainer.innerHTML = story.tags.map(tag => `<span class="tag">${tag}</span>`).join('');
    }
}

function showSwipeMessage(message) {
    const indicator = document.getElementById('swipeIndicator');
    if (indicator) {
        const hint = indicator.querySelector('.swipe-hint');
        const originalText = hint.textContent;
        hint.textContent = message;
        hint.style.fontWeight = '600';

        setTimeout(() => {
            hint.textContent = originalText;
            hint.style.fontWeight = '500';
        }, 1500);
    }
}

// Инициализация свайпа при загрузке страницы истории
document.addEventListener('DOMContentLoaded', () => {
    const storyContent = document.getElementById('storyPageContent');

    if (storyContent) {
        storyContent.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });

        storyContent.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        }, { passive: true });
    }

    // Инициализация свайпа для элементов чата
    initChatListSwipe();
});

// Свайп для элементов списка чатов
function initChatListSwipe() {
    const chatItems = document.querySelectorAll('.chat-list-item');

    chatItems.forEach(item => {
        let startX = 0;
        let currentX = 0;
        let isSwiping = false;

        item.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            isSwiping = true;
            item.classList.add('swiping');
        }, { passive: true });

        item.addEventListener('touchmove', (e) => {
            if (!isSwiping) return;
            currentX = e.touches[0].clientX;
            const diffX = currentX - startX;

            if (Math.abs(diffX) > 10) {
                e.preventDefault();
                item.style.transform = `translateX(${diffX}px)`;
            }
        }, { passive: false });

        item.addEventListener('touchend', (e) => {
            if (!isSwiping) return;
            isSwiping = false;
            item.classList.remove('swiping');

            const diffX = currentX - startX;
            const threshold = 50;

            if (diffX > threshold) {
                // Свайп вправо - показать предыдущую
                item.style.transform = 'translateX(100px)';
                setTimeout(() => {
                    item.style.transform = '';
                    showSwipeMessage('← Предыдущая история');
                }, 200);
            } else if (diffX < -threshold) {
                // Свайп влево - показать следующую
                item.style.transform = 'translateX(-100px)';
                setTimeout(() => {
                    item.style.transform = '';
                    showSwipeMessage('Следующая история →');
                }, 200);
            } else {
                // Вернуть на место
                item.style.transform = '';
            }
        }, { passive: true });
    });
}

// Редактирование метаданных
function editMetadata(button) {
    const item = button.closest('.metadata-item');
    const input = item.querySelector('.value-input');
    if (input) {
        input.focus();
        input.select();
    }
}

// Экспортировать функции для тестирования
window.nadiDebug = {
    showScreen,
    toggleMenu,
    appState,
    showNewSplash,
    hideNewSplash,
    navigateStory,
    updateStoryDisplay
};
