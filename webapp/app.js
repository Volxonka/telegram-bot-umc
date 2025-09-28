// Telegram Web App Integration
const tg = (window.Telegram && window.Telegram.WebApp) || {
    ready: function() {},
    expand: function() {},
    initDataUnsafe: {},
    showAlert: function(msg) { alert(msg); },
    BackButton: {
        show: function() {},
        hide: function() {},
        onClick: function() {}
    },
    onEvent: function() {}
};

// Global state
let currentUser = null;
let currentGroup = null;
let isCurator = false;
let fabMenuOpen = false;
let apiBaseUrl = null; // Отключаем API для демо-режима

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

async function initializeApp() {
    try {
        // Show loading screen
        showLoadingScreen();
        
        // Initialize Telegram Web App (safe)
        try {
            tg.ready();
            tg.expand();
        } catch (e) {
            console.log('Telegram WebApp not available, using demo mode');
        }
        
        // Get user data from Telegram or use demo data
        const user = tg.initDataUnsafe && tg.initDataUnsafe.user;
        if (user && user.id) {
            currentUser = user;
            updateUserInfo(user);
        } else {
            // Demo data for testing
            currentUser = {
                id: 123456789,
                first_name: "Тест",
                last_name: "Пользователь"
            };
            currentGroup = "ж1";
            isCurator = false;
            updateUserInfo(currentUser);
        }
        
        // Initialize tabs first
        initializeTabs();
        
        // Hide loading screen and show app
        setTimeout(() => {
            hideLoadingScreen();
        }, 500);
        
        // Load initial data
        setTimeout(() => {
            loadInitialData();
        }, 600);
        
        // Show FAB for curators
        if (isCurator) {
            setTimeout(() => {
                showFab();
            }, 700);
        }
        
    } catch (error) {
        console.error('Error initializing app:', error);
        // Force show app even if there's an error
        hideLoadingScreen();
        showError('Ошибка инициализации приложения');
    }
}

function showLoadingScreen() {
    document.getElementById('loading-screen').style.display = 'flex';
    document.getElementById('app').style.display = 'none';
}

function hideLoadingScreen() {
    const loadingScreen = document.getElementById('loading-screen');
    const app = document.getElementById('app');
    
    loadingScreen.style.opacity = '0';
    setTimeout(() => {
        loadingScreen.style.display = 'none';
        app.style.display = 'flex';
    }, 500);
}

function updateUserInfo(user) {
    const userName = document.getElementById('user-name');
    const userGroup = document.getElementById('user-group');
    
    if (userName) {
        userName.textContent = user.first_name + (user.last_name ? ' ' + user.last_name : '');
    }
    
    if (userGroup) {
        userGroup.textContent = 'Группа загружается...';
    }
}

function initializeTabs() {
    const tabs = document.querySelectorAll('.nav-tab');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.getAttribute('data-tab');
            
            // Remove active class from all tabs and contents
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(tc => tc.classList.remove('active'));
            
            // Add active class to clicked tab and corresponding content
            tab.classList.add('active');
            document.getElementById(targetTab + '-tab').classList.add('active');
            
            // Load content for the active tab
            loadTabContent(targetTab);
        });
    });
}

async function loadInitialData() {
    try {
        // Always load demo data for now
        loadDemoData();
    } catch (error) {
        console.error('Error loading initial data:', error);
        // Force load demo data
        loadDemoData();
    }
}

function loadDemoData() {
    // Load demo data for testing
    loadScheduleDemo();
    loadAnnouncementsDemo();
    loadPollsDemo();
    loadQuestionsDemo();
}

async function loadTabContent(tabName) {
    switch(tabName) {
        case 'schedule':
            await loadSchedule();
            break;
        case 'announcements':
            await loadAnnouncements();
            break;
        case 'polls':
            await loadPolls();
            break;
        case 'questions':
            await loadQuestions();
            break;
    }
}

// Schedule functions
async function loadSchedule() {
    // Always use demo data for now
    loadScheduleDemo();
}

function loadScheduleDemo() {
    const content = document.getElementById('schedule-content');
    content.innerHTML = `
        <div class="content-card">
            <div class="card-header">
                <div class="card-title">📅 Расписание на сегодня</div>
                <div class="card-time">Сегодня, 10:30</div>
            </div>
            <div class="card-content">
                <p><strong>1 пара:</strong> Математика (9:00-10:30)</p>
                <p><strong>2 пара:</strong> Физика (10:45-12:15)</p>
                <p><strong>3 пара:</strong> Химия (13:00-14:30)</p>
                <p><strong>4 пара:</strong> Биология (14:45-16:15)</p>
            </div>
        </div>
        <div class="content-card">
            <div class="card-header">
                <div class="card-title">📅 Расписание на завтра</div>
                <div class="card-time">Завтра, 09:00</div>
            </div>
            <div class="card-content">
                <p><strong>1 пара:</strong> История (9:00-10:30)</p>
                <p><strong>2 пара:</strong> Литература (10:45-12:15)</p>
                <p><strong>3 пара:</strong> География (13:00-14:30)</p>
            </div>
        </div>
    `;
}

async function refreshSchedule() {
    const refreshBtn = document.querySelector('[onclick="refreshSchedule()"]');
    const icon = refreshBtn.querySelector('.refresh-icon');
    
    icon.style.transform = 'rotate(360deg)';
    await loadSchedule();
    
    setTimeout(() => {
        icon.style.transform = 'rotate(0deg)';
    }, 500);
}

// Announcements functions
async function loadAnnouncements() {
    // Always use demo data for now
    loadAnnouncementsDemo();
}

function loadAnnouncementsDemo() {
    const content = document.getElementById('announcements-content');
    content.innerHTML = `
        <div class="content-card">
            <div class="card-header">
                <div class="card-title">📢 Важное объявление</div>
                <div class="card-time">Сегодня, 14:20</div>
            </div>
            <div class="card-content">
                <p>Завтра в 10:00 состоится собрание группы. Присутствие обязательно!</p>
            </div>
        </div>
        <div class="content-card">
            <div class="card-header">
                <div class="card-title">📢 Напоминание</div>
                <div class="card-time">Вчера, 16:45</div>
            </div>
            <div class="card-content">
                <p>Не забудьте сдать домашнее задание по математике до пятницы.</p>
            </div>
        </div>
    `;
}

async function refreshAnnouncements() {
    const refreshBtn = document.querySelector('[onclick="refreshAnnouncements()"]');
    const icon = refreshBtn.querySelector('.refresh-icon');
    
    icon.style.transform = 'rotate(360deg)';
    await loadAnnouncements();
    
    setTimeout(() => {
        icon.style.transform = 'rotate(0deg)';
    }, 500);
}

// Polls functions
async function loadPolls() {
    // Always use demo data for now
    loadPollsDemo();
}

function loadPollsDemo() {
    const content = document.getElementById('polls-content');
    content.innerHTML = `
        <div class="poll-card">
            <div class="poll-header">
                <div class="poll-title">🗳 Голосование посещаемости</div>
                <div class="poll-status active">Активно</div>
            </div>
            <div class="poll-options">
                <div class="poll-option">
                    <input type="radio" id="present" name="attendance" value="present">
                    <label for="present">✅ Присутствую</label>
                </div>
                <div class="poll-option">
                    <input type="radio" id="absent" name="attendance" value="absent">
                    <label for="absent">❌ Отсутствую</label>
                </div>
                <div class="poll-option">
                    <input type="radio" id="late" name="attendance" value="late">
                    <label for="late">⏰ Опоздаю</label>
                </div>
            </div>
            <button class="poll-button" onclick="submitPoll()">Отправить ответ</button>
        </div>
        <div class="poll-card">
            <div class="poll-header">
                <div class="poll-title">🗳 Голосование по экскурсии</div>
                <div class="poll-status ended">Завершено</div>
            </div>
            <div class="card-content">
                <p>Результаты голосования:</p>
                <p>✅ За экскурсию: 15 голосов</p>
                <p>❌ Против экскурсии: 3 голоса</p>
            </div>
        </div>
    `;
}

function createPollHTML(poll) {
    if (poll.status === 'active') {
        return `
            <div class="poll-card">
                <div class="poll-header">
                    <div class="poll-title">🗳 ${poll.title}</div>
                    <div class="poll-status active">Активно</div>
                </div>
                <div class="poll-options">
                    <div class="poll-option">
                        <input type="radio" id="present_${poll.id}" name="attendance_${poll.id}" value="present">
                        <label for="present_${poll.id}">✅ Присутствую</label>
                    </div>
                    <div class="poll-option">
                        <input type="radio" id="absent_${poll.id}" name="attendance_${poll.id}" value="absent">
                        <label for="absent_${poll.id}">❌ Отсутствую</label>
                    </div>
                    <div class="poll-option">
                        <input type="radio" id="late_${poll.id}" name="attendance_${poll.id}" value="late">
                        <label for="late_${poll.id}">⏰ Опоздаю</label>
                    </div>
                </div>
                <button class="poll-button" onclick="submitPollVote(${poll.id})">Отправить ответ</button>
            </div>
        `;
    } else {
        return `
            <div class="poll-card">
                <div class="poll-header">
                    <div class="poll-title">🗳 ${poll.title}</div>
                    <div class="poll-status ended">Завершено</div>
                </div>
                <div class="card-content">
                    <p>Результаты голосования:</p>
                    <p>✅ Присутствуют: ${poll.results.present} голосов</p>
                    <p>❌ Отсутствуют: ${poll.results.absent} голосов</p>
                    <p>⏰ Опоздают: ${poll.results.late} голосов</p>
                </div>
            </div>
        `;
    }
}

async function refreshPolls() {
    const refreshBtn = document.querySelector('[onclick="refreshPolls()"]');
    const icon = refreshBtn.querySelector('.refresh-icon');
    
    icon.style.transform = 'rotate(360deg)';
    await loadPolls();
    
    setTimeout(() => {
        icon.style.transform = 'rotate(0deg)';
    }, 500);
}

function submitPoll() {
    const selectedOption = document.querySelector('input[name="attendance"]:checked');
    if (selectedOption) {
        showSuccess('Ваш ответ отправлен!');
        selectedOption.checked = false;
    } else {
        showError('Пожалуйста, выберите вариант ответа');
    }
}

function submitPollVote(pollId) {
    const selectedOption = document.querySelector(`input[name="attendance_${pollId}"]:checked`);
    if (selectedOption) {
        showSuccess('Ваш голос учтен!');
        selectedOption.checked = false;
    } else {
        showError('Пожалуйста, выберите вариант ответа');
    }
}

// Questions functions
async function loadQuestions() {
    // Always use demo data for now
    loadQuestionsDemo();
}

function loadQuestionsDemo() {
    const content = document.getElementById('questions-content');
    
    if (isCurator) {
        content.innerHTML = `
            <div class="content-card">
                <div class="card-header">
                    <div class="card-title">❓ Вопрос от студента</div>
                    <div class="card-time">Сегодня, 12:15</div>
                </div>
                <div class="card-content">
                    <p><strong>Студент:</strong> Иванов Иван</p>
                    <p><strong>Вопрос:</strong> Когда будет экзамен по математике?</p>
                    <div style="margin-top: 12px;">
                        <button class="form-button" onclick="answerQuestion(1)">Ответить</button>
                    </div>
                </div>
            </div>
        `;
    } else {
        content.innerHTML = `
            <div class="content-card">
                <div class="card-header">
                    <div class="card-title">❓ Задать вопрос</div>
                </div>
                <div class="card-content">
                    <div class="form-group">
                        <textarea class="form-textarea" id="question-text" placeholder="Введите ваш вопрос..."></textarea>
                    </div>
                    <button class="form-button" onclick="submitQuestion()">Отправить вопрос</button>
                </div>
            </div>
        `;
    }
}

function createQuestionHTML(question) {
    if (isCurator && !question.answered) {
        return `
            <div class="content-card">
                <div class="card-header">
                    <div class="card-title">❓ Вопрос от студента</div>
                    <div class="card-time">${question.time}</div>
                </div>
                <div class="card-content">
                    <p><strong>Студент:</strong> ${question.student_name}</p>
                    <p><strong>Вопрос:</strong> ${question.question}</p>
                    <div style="margin-top: 12px;">
                        <button class="form-button" onclick="answerQuestion(${question.id})">Ответить</button>
                    </div>
                </div>
            </div>
        `;
    } else if (!isCurator) {
        return `
            <div class="content-card">
                <div class="card-header">
                    <div class="card-title">❓ Ваш вопрос</div>
                    <div class="card-time">${question.time}</div>
                </div>
                <div class="card-content">
                    <p><strong>Вопрос:</strong> ${question.question}</p>
                    ${question.answered ? `<p><strong>Ответ:</strong> ${question.answer}</p>` : '<p><em>Ожидает ответа...</em></p>'}
                </div>
            </div>
        `;
    }
    return '';
}

async function refreshQuestions() {
    const refreshBtn = document.querySelector('[onclick="refreshQuestions()"]');
    const icon = refreshBtn.querySelector('.refresh-icon');
    
    icon.style.transform = 'rotate(360deg)';
    await loadQuestions();
    
    setTimeout(() => {
        icon.style.transform = 'rotate(0deg)';
    }, 500);
}

function submitQuestion() {
    const questionText = document.getElementById('question-text').value.trim();
    if (questionText) {
        showSuccess('Ваш вопрос отправлен куратору!');
        document.getElementById('question-text').value = '';
    } else {
        showError('Пожалуйста, введите вопрос');
    }
}

function answerQuestion(questionId) {
    openModal('Ответить на вопрос', `
        <div class="form-group">
            <label class="form-label">Ваш ответ:</label>
            <textarea class="form-textarea" id="answer-text" placeholder="Введите ответ..."></textarea>
        </div>
        <button class="form-button" onclick="submitAnswer(${questionId})">Отправить ответ</button>
    `);
}

function submitAnswer(questionId) {
    const answerText = document.getElementById('answer-text').value.trim();
    if (answerText) {
        showSuccess('Ответ отправлен студенту!');
        closeModal();
    } else {
        showError('Пожалуйста, введите ответ');
    }
}

// FAB (Floating Action Button) functions
function showFab() {
    document.getElementById('fab-container').style.display = 'block';
}

function toggleFabMenu() {
    const fabMenu = document.querySelector('.fab-menu');
    const fab = document.querySelector('.fab');
    
    fabMenuOpen = !fabMenuOpen;
    
    if (fabMenuOpen) {
        fabMenu.classList.add('active');
        fab.style.transform = 'rotate(45deg)';
    } else {
        fabMenu.classList.remove('active');
        fab.style.transform = 'rotate(0deg)';
    }
}

// Modal functions
function openModal(title, content) {
    const modal = document.getElementById('modal');
    const modalTitle = document.getElementById('modal-title');
    const modalForm = document.getElementById('modal-form');
    
    modalTitle.textContent = title;
    modalForm.innerHTML = content;
    modal.style.display = 'flex';
    
    setTimeout(() => {
        modal.classList.add('active');
    }, 10);
}

function closeModal() {
    const modal = document.getElementById('modal');
    modal.classList.remove('active');
    
    setTimeout(() => {
        modal.style.display = 'none';
    }, 300);
}

// Form functions for curators
function openScheduleForm() {
    closeFabMenu();
    openModal('📅 Отправить расписание', `
        <div class="form-group">
            <label class="form-label">Текст расписания:</label>
            <textarea class="form-textarea" id="schedule-text" placeholder="Введите расписание..."></textarea>
        </div>
        <button class="form-button" onclick="submitSchedule()">Отправить расписание</button>
    `);
}

function openAnnouncementForm() {
    closeFabMenu();
    openModal('📢 Создать объявление', `
        <div class="form-group">
            <label class="form-label">Заголовок:</label>
            <input type="text" class="form-input" id="announcement-title" placeholder="Введите заголовок...">
        </div>
        <div class="form-group">
            <label class="form-label">Текст объявления:</label>
            <textarea class="form-textarea" id="announcement-text" placeholder="Введите текст объявления..."></textarea>
        </div>
        <button class="form-button" onclick="submitAnnouncement()">Отправить объявление</button>
    `);
}

function openPollForm() {
    closeFabMenu();
    openModal('🗳 Создать голосование', `
        <div class="form-group">
            <label class="form-label">Тема голосования:</label>
            <input type="text" class="form-input" id="poll-title" placeholder="Введите тему...">
        </div>
        <div class="form-group">
            <label class="form-label">Длительность (минуты):</label>
            <input type="number" class="form-input" id="poll-duration" value="30" min="1" max="1440">
        </div>
        <button class="form-button" onclick="submitPoll()">Создать голосование</button>
    `);
}

function submitSchedule() {
    const scheduleText = document.getElementById('schedule-text').value.trim();
    if (scheduleText) {
        showSuccess('Расписание отправлено!');
        closeModal();
    } else {
        showError('Пожалуйста, введите расписание');
    }
}

function submitAnnouncement() {
    const title = document.getElementById('announcement-title').value.trim();
    const text = document.getElementById('announcement-text').value.trim();
    
    if (title && text) {
        showSuccess('Объявление отправлено!');
        closeModal();
    } else {
        showError('Пожалуйста, заполните все поля');
    }
}

function submitPoll() {
    const title = document.getElementById('poll-title').value.trim();
    const duration = document.getElementById('poll-duration').value;
    
    if (title && duration) {
        showSuccess('Голосование создано!');
        closeModal();
    } else {
        showError('Пожалуйста, заполните все поля');
    }
}

function closeFabMenu() {
    if (fabMenuOpen) {
        toggleFabMenu();
    }
}

// Utility functions
function showSuccess(message) {
    try {
        tg.showAlert(message);
    } catch (e) {
        alert(message);
    }
}

function showError(message) {
    try {
        tg.showAlert(message);
    } catch (e) {
        alert(message);
    }
}

// Close modal when clicking outside
document.addEventListener('click', function(event) {
    const modal = document.getElementById('modal');
    if (event.target === modal) {
        closeModal();
    }
});

// Handle back button (safe)
try {
    tg.onEvent('backButtonClicked', function() {
        if (document.getElementById('modal').style.display === 'flex') {
            closeModal();
        } else if (fabMenuOpen) {
            closeFabMenu();
        } else {
            try {
                tg.close();
            } catch (e) {
                console.log('Cannot close app');
            }
        }
    });
} catch (e) {
    console.log('Back button not available');
}

// Show back button when needed
function showBackButton() {
    try {
        tg.BackButton.show();
    } catch (e) {
        console.log('Back button not available');
    }
}

function hideBackButton() {
    try {
        tg.BackButton.hide();
    } catch (e) {
        console.log('Back button not available');
    }
}

