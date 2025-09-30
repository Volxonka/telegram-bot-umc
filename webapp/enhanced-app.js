// Enhanced УМЦ Web App JavaScript

// Enhanced Telegram Web App Integration based on Context7 documentation
const tg = (window.Telegram && window.Telegram.WebApp) || {
    ready: function() {
        // Proper mobile event handling based on Context7
        if (window.TelegramWebviewProxy) {
            window.TelegramWebviewProxy.postEvent('web_app_ready', {});
        }
    },
    expand: function() {
        // Expand mini app to maximum height
        if (window.TelegramWebviewProxy) {
            window.TelegramWebviewProxy.postEvent('web_app_expand', {});
        }
    },
    initDataUnsafe: {},
    showAlert: function(msg) { 
        if (window.TelegramWebviewProxy) {
            window.TelegramWebviewProxy.postEvent('web_app_show_alert', {message: msg});
        } else {
            alert(msg); 
        }
    },
    BackButton: {
        show: function() {
            if (window.TelegramWebviewProxy) {
                window.TelegramWebviewProxy.postEvent('web_app_back_button_show', {});
            }
        },
        hide: function() {
            if (window.TelegramWebviewProxy) {
                window.TelegramWebviewProxy.postEvent('web_app_back_button_hide', {});
            }
        },
        onClick: function() {}
    },
    onEvent: function() {},
    // Mobile-specific methods based on Context7
    setupSwipeBehavior: function(options) {
        if (window.TelegramWebviewProxy) {
            window.TelegramWebviewProxy.postEvent('web_app_setup_swipe_behavior', options);
        }
    },
    enableVerticalSwipes: function() {
        if (window.TelegramWebviewProxy) {
            window.TelegramWebviewProxy.postEvent('web_app_enable_vertical_swipes', {});
        }
    },
    disableVerticalSwipes: function() {
        if (window.TelegramWebviewProxy) {
            window.TelegramWebviewProxy.postEvent('web_app_disable_vertical_swipes', {});
        }
    }
};

// Global state
let currentUser = null;
let currentGroup = null;
let userRole = 'student'; // student, curator, admin
let fabMenuOpen = false;
let userMenuOpen = false;
let notificationPanelOpen = false;
let currentTheme = 'light';

// Demo data
const demoData = {
    schedule: [
        {
            id: 1,
            title: "Расписание на сегодня",
            time: "Сегодня, 10:30",
            content: "1 пара: Математика (9:00-10:30)\n2 пара: Физика (10:45-12:15)\n3 пара: Химия (13:00-14:30)\n4 пара: Биология (14:45-16:15)",
            hasMedia: false
        },
        {
            id: 2,
            title: "Расписание на завтра",
            time: "Завтра, 09:00",
            content: "1 пара: История (9:00-10:30)\n2 пара: Литература (10:45-12:15)\n3 пара: География (13:00-14:30)",
            hasMedia: false
        }
    ],
    announcements: [
        {
            id: 1,
            title: "Важное объявление",
            time: "Сегодня, 14:20",
            content: "Завтра в 10:00 состоится собрание группы. Присутствие обязательно!",
            important: true,
            read: false
        },
        {
            id: 2,
            title: "Напоминание",
            time: "Вчера, 16:45",
            content: "Не забудьте сдать домашнее задание по математике до пятницы.",
            important: false,
            read: true
        }
    ],
    polls: [
        {
            id: 1,
            title: "Голосование посещаемости",
            status: "active",
            created_time: "Сегодня, 12:00",
            duration: 30,
            options: ["Присутствую", "Отсутствую", "Опоздаю"],
            user_voted: false,
            total_votes: 15,
            results: {
                present: 12,
                absent: 2,
                late: 1
            }
        },
        {
            id: 2,
            title: "Голосование по экскурсии",
            status: "ended",
            created_time: "Вчера, 15:00",
            duration: 60,
            options: ["За экскурсию", "Против экскурсии"],
            user_voted: true,
            total_votes: 18,
            results: {
                present: 15,
                absent: 3,
                late: 0
            }
        }
    ],
    questions: [
        {
            id: 1,
            student_id: 123456789,
            student_name: "Иванов Иван",
            question: "Когда будет экзамен по математике?",
            answer: "",
            time: "Сегодня, 12:15",
            answered: false,
            answered_time: null
        }
    ]
};

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Enhanced mobile optimizations based on Context7 documentation
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Register service worker for offline functionality
        navigator.serviceWorker.register('/sw.js').catch(() => {
            // Service worker registration failed, continue without it
        });
    });
}

// Mobile platform detection based on Context7 User-Agent documentation
function detectMobilePlatform() {
    const userAgent = navigator.userAgent;
    
    // Telegram Android detection (Context7 format)
    if (userAgent.includes('Telegram-Android')) {
        const match = userAgent.match(/Telegram-Android\/([0-9.]+) \(([^;]+); Android ([0-9.]+); SDK ([0-9]+); ([A-Z]+)\)/);
        if (match) {
            return {
                platform: 'telegram-android',
                appVersion: match[1],
                device: match[2],
                androidVersion: match[3],
                sdkVersion: match[4],
                performanceClass: match[5],
                isLowPerformance: match[5] === 'LOW'
            };
        }
    }
    
    // Telegram iOS detection
    if (userAgent.includes('Telegram-iOS')) {
        return {
            platform: 'telegram-ios',
            isLowPerformance: false
        };
    }
    
    // Regular mobile detection
    if (/Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent)) {
        return {
            platform: 'mobile-browser',
            isLowPerformance: /Android [1-4]\.|iPhone OS [1-9]\./i.test(userAgent)
        };
    }
    
    return {
        platform: 'desktop',
        isLowPerformance: false
    };
}

// Initialize mobile platform optimizations
const mobilePlatform = detectMobilePlatform();
console.log('Mobile Platform:', mobilePlatform);

// Apply performance optimizations based on device capabilities
if (mobilePlatform.isLowPerformance) {
    // Reduce animations and effects for low-performance devices
    document.documentElement.style.setProperty('--transition', 'all 0.1s ease');
    document.documentElement.style.setProperty('--shadow-light', 'none');
    document.documentElement.style.setProperty('--shadow-medium', 'none');
    document.documentElement.style.setProperty('--shadow-heavy', 'none');
}

// Prevent zoom on double tap (iOS)
let lastTouchEnd = 0;
document.addEventListener('touchend', function (event) {
    const now = (new Date()).getTime();
    if (now - lastTouchEnd <= 300) {
        event.preventDefault();
    }
    lastTouchEnd = now;
}, false);

// Add pull-to-refresh functionality
let pullToRefresh = {
    startY: 0,
    currentY: 0,
    isPulling: false,
    threshold: 100
};

document.addEventListener('touchstart', (e) => {
    if (window.scrollY === 0) {
        pullToRefresh.startY = e.touches[0].clientY;
        pullToRefresh.isPulling = true;
    }
});

document.addEventListener('touchmove', (e) => {
    if (!pullToRefresh.isPulling) return;
    
    pullToRefresh.currentY = e.touches[0].clientY;
    const pullDistance = pullToRefresh.currentY - pullToRefresh.startY;
    
    if (pullDistance > 0 && pullDistance < pullToRefresh.threshold) {
        // Visual feedback for pull-to-refresh
        document.body.style.transform = `translateY(${pullDistance * 0.5}px)`;
    }
});

document.addEventListener('touchend', (e) => {
    if (!pullToRefresh.isPulling) return;
    
    const pullDistance = pullToRefresh.currentY - pullToRefresh.startY;
    
    if (pullDistance > pullToRefresh.threshold) {
        // Trigger refresh
        showToast('Обновление...', 'info');
        setTimeout(() => {
            loadInitialData();
            showToast('Данные обновлены', 'success');
        }, 1000);
    }
    
    // Reset
    document.body.style.transform = '';
    pullToRefresh.isPulling = false;
    pullToRefresh.startY = 0;
    pullToRefresh.currentY = 0;
});

async function initializeApp() {
    try {
        showLoadingScreen();
        
        // Initialize Telegram Web App with Context7 optimizations
        try {
            tg.ready();
            tg.expand();
            
            // Setup swipe behavior based on Context7 documentation
            if (tg.setupSwipeBehavior) {
                tg.setupSwipeBehavior({
                    allow_vertical_swipe: true
                });
            }
            
            // Enable vertical swipes for mobile
            if (mobilePlatform.platform.includes('telegram') && tg.enableVerticalSwipes) {
                tg.enableVerticalSwipes();
            }
            
        } catch (e) {
            console.log('Telegram WebApp not available, using demo mode');
        }
        
        // Get user data or use demo data
        const user = tg.initDataUnsafe && tg.initDataUnsafe.user;
        if (user && user.id) {
            currentUser = user;
            // Determine user role based on user ID (demo logic)
            if (user.id === 665509323) {
                userRole = 'admin';
            } else if (user.id % 3 === 0) {
                userRole = 'curator';
            } else {
                userRole = 'student';
            }
            updateUserInfo(user);
        } else {
            currentUser = {
                id: 123456789,
                first_name: "Тест",
                last_name: "Пользователь"
            };
            currentGroup = "ж1";
            userRole = 'student'; // Demo: default to student
            updateUserInfo(currentUser);
        }
        
        // Initialize theme
        initializeTheme();
        
        // Initialize tabs
        initializeTabs();
        
        // Initialize search
        initializeSearch();
        
        // Initialize filters
        initializeFilters();
        
        // Hide loading screen
        setTimeout(() => {
            hideLoadingScreen();
        }, 2000);
        
        // Load initial data
        setTimeout(() => {
            loadInitialData();
        }, 2100);
        
    } catch (error) {
        console.error('Error initializing app:', error);
        hideLoadingScreen();
        showToast('Ошибка инициализации приложения', 'error');
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
    const userRoleElement = document.getElementById('user-role');
    
    if (userName) {
        const fullName = window.userInfo?.full_name || `${user.first_name} ${user.last_name || ''}`.trim();
        userName.textContent = fullName;
    }
    
    if (userRoleElement) {
        const roleText = {
            'admin': 'Администратор',
            'curator': 'Куратор',
            'student': 'Студент'
        };
        userRoleElement.textContent = roleText[userRole] || 'Студент';
    }
    
    // Добавляем информацию о группе
    const userGroupElement = document.getElementById('user-group');
    if (userGroupElement) {
        const groupName = window.userInfo?.group_name || currentGroup;
        userGroupElement.textContent = `👥 ${groupName}`;
    }
    
    // Update UI based on role
    updateUIForRole();
}

function updateUIForRole() {
    // Show/hide FAB based on role
    const fabContainer = document.querySelector('.fab-container');
    if (fabContainer) {
        if (userRole === 'admin' || userRole === 'curator') {
            fabContainer.style.display = 'block';
        } else {
            fabContainer.style.display = 'none';
        }
    }
    
    // Update navigation tabs based on role
    updateNavigationForRole();
    
    // Update dashboard content based on role
    updateDashboardForRole();
}

function updateNavigationForRole() {
    const navTabs = document.querySelectorAll('.nav-tab');
    
    // Hide admin-specific tabs for non-admin users
    navTabs.forEach(tab => {
        const tabName = tab.getAttribute('data-tab');
        if (tabName === 'admin' && userRole !== 'admin') {
            tab.style.display = 'none';
        }
    });
}

function updateDashboardForRole() {
    const dashboardTab = document.getElementById('dashboard-tab');
    if (!dashboardTab) return;
    
    // Update quick actions based on role
    const actionsGrid = dashboardTab.querySelector('.actions-grid');
    if (actionsGrid) {
        if (userRole === 'admin') {
            actionsGrid.innerHTML = `
                <button class="action-btn" onclick="manageUsers()">
                    <i class="fas fa-users"></i>
                    <span>Управление пользователями</span>
                </button>
                <button class="action-btn" onclick="manageGroups()">
                    <i class="fas fa-layer-group"></i>
                    <span>Управление группами</span>
                </button>
                <button class="action-btn" onclick="viewStatistics()">
                    <i class="fas fa-chart-pie"></i>
                    <span>Статистика</span>
                </button>
                <button class="action-btn" onclick="systemSettings()">
                    <i class="fas fa-cogs"></i>
                    <span>Настройки системы</span>
                </button>
            `;
        } else if (userRole === 'curator') {
            actionsGrid.innerHTML = `
                <button class="action-btn" onclick="manageStudents()">
                    <i class="fas fa-user-graduate"></i>
                    <span>Управление студентами</span>
                </button>
                <button class="action-btn" onclick="viewAttendance()">
                    <i class="fas fa-user-check"></i>
                    <span>Посещаемость</span>
                </button>
                <button class="action-btn" onclick="viewGrades()">
                    <i class="fas fa-graduation-cap"></i>
                    <span>Оценки</span>
                </button>
                <button class="action-btn" onclick="viewReports()">
                    <i class="fas fa-file-alt"></i>
                    <span>Отчеты</span>
                </button>
            `;
        } else {
            // Student actions (default)
            actionsGrid.innerHTML = `
                <button class="action-btn" onclick="askQuickQuestion()">
                    <i class="fas fa-question"></i>
                    <span>Задать вопрос</span>
                </button>
                <button class="action-btn" onclick="viewAttendance()">
                    <i class="fas fa-user-check"></i>
                    <span>Посещаемость</span>
                </button>
                <button class="action-btn" onclick="viewGrades()">
                    <i class="fas fa-graduation-cap"></i>
                    <span>Оценки</span>
                </button>
                <button class="action-btn" onclick="viewCalendar()">
                    <i class="fas fa-calendar"></i>
                    <span>Календарь</span>
                </button>
            `;
        }
    }
}

function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
}

function setTheme(theme) {
    currentTheme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
        themeIcon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
}

function toggleTheme() {
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    showToast(`Переключено на ${newTheme === 'dark' ? 'темную' : 'светлую'} тему`, 'info');
}

function initializeTabs() {
    const tabs = document.querySelectorAll('.nav-tab');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.getAttribute('data-tab');
            switchToTab(targetTab);
        });
    });
    
    // Initialize mobile navigation
    initializeMobileNavigation();
}

function switchToTab(targetTab) {
    const tabs = document.querySelectorAll('.nav-tab');
    const tabContents = document.querySelectorAll('.tab-content');
    
    // Remove active class from all tabs and contents
    tabs.forEach(t => t.classList.remove('active'));
    tabContents.forEach(tc => tc.classList.remove('active'));
    
    // Add active class to clicked tab and corresponding content
    const activeTab = document.querySelector(`[data-tab="${targetTab}"]`);
    if (activeTab) {
        activeTab.classList.add('active');
    }
    
    const activeContent = document.getElementById(targetTab + '-tab');
    if (activeContent) {
        activeContent.classList.add('active');
    }
    
    // Update mobile navigation indicator
    updateMobileNavIndicator(targetTab);
    
    // Load content for the active tab
    loadTabContent(targetTab);
}

function initializeMobileNavigation() {
    // Enhanced touch/swipe support based on Context7 mobile optimization
    let startX = 0;
    let startY = 0;
    let isScrolling = false;
    let swipeThreshold = 50;
    
    // Adjust swipe threshold based on device performance
    if (mobilePlatform.isLowPerformance) {
        swipeThreshold = 80; // Larger threshold for low-performance devices
    }
    
    const mainContent = document.querySelector('.main-content');
    if (!mainContent) return;
    
    // Prevent default touch behaviors that might interfere
    mainContent.addEventListener('touchstart', (e) => {
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
        isScrolling = false;
        
        // Prevent zoom on double tap
        const now = Date.now();
        if (now - lastTouchEnd <= 300) {
            e.preventDefault();
        }
        lastTouchEnd = now;
    }, { passive: false });
    
    mainContent.addEventListener('touchmove', (e) => {
        if (!startX || !startY) return;
        
        const diffX = startX - e.touches[0].clientX;
        const diffY = startY - e.touches[0].clientY;
        
        // Determine if this is a horizontal swipe
        if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 10) {
            isScrolling = true;
            // Prevent vertical scroll during horizontal swipe
            e.preventDefault();
        }
    }, { passive: false });
    
    mainContent.addEventListener('touchend', (e) => {
        if (!startX || !startY || !isScrolling) return;
        
        const endX = e.changedTouches[0].clientX;
        const diffX = startX - endX;
        
        // Check if swipe distance meets threshold
        if (Math.abs(diffX) > swipeThreshold) {
            const tabs = ['dashboard', 'schedule', 'announcements', 'polls', 'questions'];
            const currentTab = getCurrentActiveTab();
            const currentIndex = tabs.indexOf(currentTab);
            
            if (diffX > 0 && currentIndex < tabs.length - 1) {
                // Swipe left - next tab
                switchToTab(tabs[currentIndex + 1]);
                // Haptic feedback for Telegram apps
                if (mobilePlatform.platform.includes('telegram') && window.TelegramWebviewProxy) {
                    window.TelegramWebviewProxy.postEvent('web_app_haptic_feedback', {type: 'light'});
                }
            } else if (diffX < 0 && currentIndex > 0) {
                // Swipe right - previous tab
                switchToTab(tabs[currentIndex - 1]);
                // Haptic feedback for Telegram apps
                if (mobilePlatform.platform.includes('telegram') && window.TelegramWebviewProxy) {
                    window.TelegramWebviewProxy.postEvent('web_app_haptic_feedback', {type: 'light'});
                }
            }
        }
        
        startX = 0;
        startY = 0;
        isScrolling = false;
    });
}

function getCurrentActiveTab() {
    const activeTab = document.querySelector('.nav-tab.active');
    return activeTab ? activeTab.getAttribute('data-tab') : 'dashboard';
}

function updateMobileNavIndicator(activeTab) {
    const indicator = document.getElementById('mobile-nav-indicator');
    if (!indicator) return;
    
    const tabs = ['dashboard', 'schedule', 'announcements', 'polls', 'questions'];
    const activeIndex = tabs.indexOf(activeTab);
    const progress = (activeIndex + 1) / tabs.length;
    
    indicator.style.transform = `scaleX(${progress})`;
}

function initializeSearch() {
    const searchInput = document.getElementById('search-input');
    const searchClear = document.querySelector('.search-clear');
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();
            if (query) {
                searchClear.style.display = 'block';
                performSearch(query);
            } else {
                searchClear.style.display = 'none';
                clearSearch();
            }
        });
    }
}

function initializeFilters() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    
    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            filterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            const filter = btn.getAttribute('data-filter');
            applyFilter(filter);
        });
    });
}

function performSearch(query) {
    // Simple search implementation
    const allCards = document.querySelectorAll('.content-card, .schedule-item, .announcement-item, .poll-card');
    
    allCards.forEach(card => {
        const text = card.textContent.toLowerCase();
        if (text.includes(query.toLowerCase())) {
            card.style.display = 'block';
            card.style.animation = 'fadeIn 0.3s ease';
        } else {
            card.style.display = 'none';
        }
    });
    
    showToast(`Найдено результатов: ${document.querySelectorAll('.content-card[style*="block"], .schedule-item[style*="block"], .announcement-item[style*="block"], .poll-card[style*="block"]').length}`, 'info');
}

function clearSearch() {
    const searchInput = document.getElementById('search-input');
    const searchClear = document.querySelector('.search-clear');
    
    if (searchInput) {
        searchInput.value = '';
    }
    if (searchClear) {
        searchClear.style.display = 'none';
    }
    
    // Show all cards
    const allCards = document.querySelectorAll('.content-card, .schedule-item, .announcement-item, .poll-card');
    allCards.forEach(card => {
        card.style.display = 'block';
    });
}

function applyFilter(filter) {
    // Filter implementation based on filter type
    showToast(`Применен фильтр: ${filter}`, 'info');
}

async function loadDataFromServer() {
    try {
        console.log('Загрузка персональных данных с сервера...');
        
        // Получаем параметры пользователя из URL
        const urlParams = new URLSearchParams(window.location.search);
        const user_id = urlParams.get('user_id');
        const group = urlParams.get('group');
        const username = urlParams.get('username');
        const full_name = urlParams.get('full_name');
        const is_curator = urlParams.get('is_curator') === 'true';
        
        console.log('Параметры пользователя:', { user_id, group, username, full_name, is_curator });
        
        // Создаем URL с параметрами пользователя
        const apiUrl = `/api/data?user_id=${user_id}&group=${group}&username=${username}&full_name=${encodeURIComponent(full_name)}&is_curator=${is_curator}`;
        
        const response = await fetch(apiUrl, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Персональные данные получены с сервера:', result);
        
        if (result.status === 'success' && result.data) {
            // Обновляем глобальные данные
            window.appData = result.data;
            window.userInfo = result.user_info;
            
            // Обновляем информацию о пользователе
            if (result.user_info) {
                currentUser = {
                    id: result.user_info.user_id,
                    first_name: result.user_info.full_name.split()[0] || result.user_info.username,
                    last_name: result.user_info.full_name.split().slice(1).join(' ') || '',
                    username: result.user_info.username
                };
                currentGroup = result.user_info.group;
                userRole = result.user_info.is_curator ? 'curator' : 'student';
                isCurator = result.user_info.is_curator;
                
                console.log('Обновлена информация о пользователе:', currentUser, userRole);
            }
            
            return result.data;
        } else {
            throw new Error('Неверный формат ответа сервера');
        }
    } catch (error) {
        console.error('Ошибка загрузки данных:', error);
        throw error;
    }
}

function loadInitialData() {
    // Сначала загружаем данные с сервера
    loadDataFromServer().then(() => {
        // Затем обновляем UI
        loadDashboardData();
        loadSchedule();
        loadAnnouncements();
        loadPolls();
        loadQuestions();
    }).catch((error) => {
        console.error('Ошибка загрузки данных с сервера:', error);
        // Fallback на демо-данные
        loadDashboardData();
        loadSchedule();
        loadAnnouncements();
        loadPolls();
        loadQuestions();
    });
}

function loadTabContent(tabName) {
    switch(tabName) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'schedule':
            loadSchedule();
            break;
        case 'announcements':
            loadAnnouncements();
            break;
        case 'polls':
            loadPolls();
            break;
        case 'questions':
            loadQuestions();
            break;
    }
}

// Dashboard functions
function loadDashboardData() {
    // Dashboard data is already loaded in HTML
    // Just update any dynamic content
    updateNotificationCount();
}

function updateNotificationCount() {
    const announcementsData = (window.appData && window.appData.announcements) || demoData.announcements;
    const unreadCount = announcementsData.filter(a => !a.read).length;
    const notificationBadge = document.getElementById('notification-count');
    if (notificationBadge) {
        notificationBadge.textContent = unreadCount;
        notificationBadge.style.display = unreadCount > 0 ? 'flex' : 'none';
    }
}

// Schedule functions
function loadSchedule() {
    const content = document.getElementById('schedule-content');
    if (!content) return;
    
    // Используем данные с сервера или fallback на демо-данные
    const scheduleData = (window.appData && window.appData.schedule) || demoData.schedule;
    
    let html = '';
    scheduleData.forEach(schedule => {
        html += `
            <div class="content-card">
                <div class="card-header">
                    <div class="card-title">📅 ${schedule.title}</div>
                    <div class="card-time">${schedule.time}</div>
                </div>
                <div class="card-content">
                    ${schedule.content.replace(/\n/g, '<br>')}
                </div>
            </div>
        `;
    });
    
    content.innerHTML = html;
}

function refreshSchedule() {
    const refreshBtn = document.querySelector('[onclick="refreshSchedule()"]');
    const icon = refreshBtn.querySelector('i');
    
    icon.style.animation = 'spin 1s linear infinite';
    setTimeout(() => {
        icon.style.animation = '';
        loadSchedule();
        showToast('Расписание обновлено', 'success');
    }, 1000);
}

// Announcements functions
function loadAnnouncements() {
    const content = document.getElementById('announcements-content');
    if (!content) return;
    
    // Используем данные с сервера или fallback на демо-данные
    const announcementsData = (window.appData && window.appData.announcements) || demoData.announcements;
    
    let html = '';
    announcementsData.forEach(announcement => {
        const importantClass = announcement.priority === 'high' ? 'important' : '';
        const readClass = announcement.read ? 'read' : 'unread';
        
        html += `
            <div class="content-card ${importantClass} ${readClass}">
                <div class="card-header">
                    <div class="card-title">📢 ${announcement.title}</div>
                    <div class="card-time">${announcement.time}</div>
                </div>
                <div class="card-content">
                    ${announcement.content}
                </div>
            </div>
        `;
    });
    
    content.innerHTML = html;
}

function refreshAnnouncements() {
    const refreshBtn = document.querySelector('[onclick="refreshAnnouncements()"]');
    const icon = refreshBtn.querySelector('i');
    
    icon.style.animation = 'spin 1s linear infinite';
    setTimeout(() => {
        icon.style.animation = '';
        loadAnnouncements();
        showToast('Объявления обновлены', 'success');
    }, 1000);
}

function markAllRead() {
    demoData.announcements.forEach(a => a.read = true);
    loadAnnouncements();
    updateNotificationCount();
    showToast('Все объявления отмечены как прочитанные', 'success');
}

// Polls functions
function loadPolls() {
    const content = document.getElementById('polls-content');
    if (!content) return;
    
    // Используем данные с сервера или fallback на демо-данные
    const pollsData = (window.appData && window.appData.polls) || demoData.polls;
    
    let html = '';
    pollsData.forEach(poll => {
        html += createPollHTML(poll);
    });
    
    content.innerHTML = html;
}

function createPollHTML(poll) {
    if (poll.status === 'active') {
        return `
            <div class="poll-card">
                <div class="poll-header">
                    <div class="poll-title">
                        <i class="fas fa-poll"></i>
                        ${poll.title}
                    </div>
                    <div class="poll-status active">Активно</div>
                </div>
                <div class="poll-options">
                    <div class="poll-option">
                        <input type="radio" id="present_${poll.id}" name="attendance_${poll.id}" value="present">
                        <label for="present_${poll.id}">Присутствую</label>
                        <i class="fas fa-check-circle option-icon present"></i>
                    </div>
                    <div class="poll-option">
                        <input type="radio" id="absent_${poll.id}" name="attendance_${poll.id}" value="absent">
                        <label for="absent_${poll.id}">Отсутствую</label>
                        <i class="fas fa-times-circle option-icon absent"></i>
                    </div>
                    <div class="poll-option">
                        <input type="radio" id="late_${poll.id}" name="attendance_${poll.id}" value="late">
                        <label for="late_${poll.id}">Опоздаю</label>
                        <i class="fas fa-clock option-icon late"></i>
                    </div>
                </div>
                <button class="poll-button" onclick="submitPollVote(${poll.id})">
                    <i class="fas fa-paper-plane"></i>
                    Отправить ответ
                </button>
            </div>
        `;
    } else {
        const totalVotes = poll.results.present + poll.results.absent + poll.results.late;
        const presentPercent = totalVotes > 0 ? Math.round((poll.results.present / totalVotes) * 100) : 0;
        const absentPercent = totalVotes > 0 ? Math.round((poll.results.absent / totalVotes) * 100) : 0;
        const latePercent = totalVotes > 0 ? Math.round((poll.results.late / totalVotes) * 100) : 0;
        
        return `
            <div class="poll-card">
                <div class="poll-header">
                    <div class="poll-title">
                        <i class="fas fa-poll"></i>
                        ${poll.title}
                    </div>
                    <div class="poll-status ended">Завершено</div>
                </div>
                <div class="poll-results">
                    <h4><i class="fas fa-chart-bar"></i> Результаты голосования</h4>
                    <div class="result-item">
                        <div class="result-label">
                            <i class="fas fa-check-circle" style="color: var(--success-color);"></i>
                            Присутствуют
                        </div>
                        <div class="result-count">${poll.results.present} (${presentPercent}%)</div>
                    </div>
                    <div class="result-bar">
                        <div class="result-progress" style="width: ${presentPercent}%; background: var(--success-color);"></div>
                    </div>
                    
                    <div class="result-item">
                        <div class="result-label">
                            <i class="fas fa-times-circle" style="color: var(--error-color);"></i>
                            Отсутствуют
                        </div>
                        <div class="result-count">${poll.results.absent} (${absentPercent}%)</div>
                    </div>
                    <div class="result-bar">
                        <div class="result-progress" style="width: ${absentPercent}%; background: var(--error-color);"></div>
                    </div>
                    
                    <div class="result-item">
                        <div class="result-label">
                            <i class="fas fa-clock" style="color: var(--warning-color);"></i>
                            Опоздают
                        </div>
                        <div class="result-count">${poll.results.late} (${latePercent}%)</div>
                    </div>
                    <div class="result-bar">
                        <div class="result-progress" style="width: ${latePercent}%; background: var(--warning-color);"></div>
                    </div>
                </div>
                <div class="poll-stats">
                    <div class="stat-card">
                        <div class="stat-number">${totalVotes}</div>
                        <div class="stat-label">Всего голосов</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${presentPercent}%</div>
                        <div class="stat-label">Посещаемость</div>
                    </div>
                </div>
            </div>
        `;
    }
}

function refreshPolls() {
    const refreshBtn = document.querySelector('[onclick="refreshPolls()"]');
    const icon = refreshBtn.querySelector('i');
    
    icon.style.animation = 'spin 1s linear infinite';
    setTimeout(() => {
        icon.style.animation = '';
        loadPolls();
        showToast('Голосования обновлены', 'success');
    }, 1000);
}

function submitPollVote(pollId) {
    const selectedOption = document.querySelector(`input[name="attendance_${pollId}"]:checked`);
    if (selectedOption) {
        showToast('Ваш голос учтен!', 'success');
        selectedOption.checked = false;
        
        // Update poll data
        const poll = demoData.polls.find(p => p.id === pollId);
        if (poll) {
            poll.user_voted = true;
            poll.total_votes++;
            poll.results[selectedOption.value]++;
        }
    } else {
        showToast('Пожалуйста, выберите вариант ответа', 'error');
    }
}

function viewPollHistory() {
    showToast('История голосований', 'info');
}

// Questions functions
function loadQuestions() {
    const content = document.getElementById('questions-content');
    if (!content) return;
    
    if (userRole === 'curator' || userRole === 'admin') {
        loadCuratorQuestions();
    } else {
        loadStudentQuestions();
    }
}

function loadCuratorQuestions() {
    const content = document.getElementById('questions-content');
    const questionsData = (window.appData && window.appData.questions) || demoData.questions;
    const unansweredQuestions = questionsData.filter(q => q.status !== 'answered');
    
    let html = '';
    if (unansweredQuestions.length === 0) {
        html = `
            <div class="content-card">
                <div class="card-content">
                    <p>Все вопросы отвечены! 🎉</p>
                </div>
            </div>
        `;
    } else {
        unansweredQuestions.forEach(question => {
            html += `
                <div class="content-card">
                    <div class="card-header">
                        <div class="card-title">❓ Вопрос от студента</div>
                        <div class="card-time">${question.time}</div>
                    </div>
                    <div class="card-content">
                        <p><strong>Студент:</strong> ${question.student_name}</p>
                        <p><strong>Вопрос:</strong> ${question.question}</p>
                        <div style="margin-top: 1rem;">
                            <button class="btn-primary" onclick="answerQuestion(${question.id})">Ответить</button>
                        </div>
                    </div>
                </div>
            `;
        });
    }
    
    content.innerHTML = html;
}

function loadStudentQuestions() {
    const content = document.getElementById('questions-content');
    
    let html = `
        <div class="content-card">
            <div class="card-header">
                <div class="card-title">❓ Задать вопрос</div>
            </div>
            <div class="card-content">
                <div class="form-group">
                    <textarea class="form-textarea" id="question-text" placeholder="Введите ваш вопрос..."></textarea>
                </div>
                <button class="btn-primary" onclick="submitQuestion()">Отправить вопрос</button>
            </div>
        </div>
    `;
    
    // Add user's questions
    const userQuestions = demoData.questions.filter(q => q.student_id === currentUser.id);
    userQuestions.forEach(question => {
        html += `
            <div class="content-card">
                <div class="card-header">
                    <div class="card-title">❓ Ваш вопрос</div>
                    <div class="card-time">${question.time}</div>
                </div>
                <div class="card-content">
                    <p><strong>Вопрос:</strong> ${question.question}</p>
                    ${question.answered ? 
                        `<p><strong>Ответ:</strong> ${question.answer}</p>` : 
                        '<p><em>Ожидает ответа...</em></p>'
                    }
                </div>
            </div>
        `;
    });
    
    content.innerHTML = html;
}

function refreshQuestions() {
    const refreshBtn = document.querySelector('[onclick="refreshQuestions()"]');
    const icon = refreshBtn.querySelector('i');
    
    icon.style.animation = 'spin 1s linear infinite';
    setTimeout(() => {
        icon.style.animation = '';
        loadQuestions();
        showToast('Вопросы обновлены', 'success');
    }, 1000);
}

function submitQuestion() {
    const questionText = document.getElementById('question-text').value.trim();
    if (questionText) {
        showToast('Вопрос отправлен куратору!', 'success');
        document.getElementById('question-text').value = '';
        
        // Add to demo data
        demoData.questions.push({
            id: Date.now(),
            student_id: currentUser.id,
            student_name: currentUser.first_name + ' ' + (currentUser.last_name || ''),
            question: questionText,
            answer: '',
            time: 'Только что',
            answered: false,
            answered_time: null
        });
    } else {
        showToast('Пожалуйста, введите вопрос', 'error');
    }
}

function answerQuestion(questionId) {
    openModal('Ответить на вопрос', `
        <div class="form-group">
            <label class="form-label">Ваш ответ:</label>
            <textarea class="form-textarea" id="answer-text" placeholder="Введите ответ..."></textarea>
        </div>
        <button class="btn-primary" onclick="submitAnswer(${questionId})">Отправить ответ</button>
    `);
}

function submitAnswer(questionId) {
    const answerText = document.getElementById('answer-text').value.trim();
    if (answerText) {
        showToast('Ответ отправлен студенту!', 'success');
        closeModal();
        
        // Update demo data
        const question = demoData.questions.find(q => q.id === questionId);
        if (question) {
            question.answer = answerText;
            question.answered = true;
            question.answered_time = 'Только что';
        }
        
        loadQuestions();
    } else {
        showToast('Пожалуйста, введите ответ', 'error');
    }
}

function viewQuestionHistory() {
    showToast('История вопросов', 'info');
}

// Admin functions
function manageUsers() {
    showToast('Управление пользователями', 'info');
}

function manageGroups() {
    showToast('Управление группами', 'info');
}

function viewStatistics() {
    showToast('Просмотр статистики', 'info');
}

function systemSettings() {
    showToast('Настройки системы', 'info');
}

// Curator functions
function manageStudents() {
    showToast('Управление студентами', 'info');
}

function viewReports() {
    showToast('Просмотр отчетов', 'info');
}

// UI Functions
function toggleUserMenu() {
    const userMenu = document.getElementById('user-menu');
    userMenuOpen = !userMenuOpen;
    
    if (userMenuOpen) {
        userMenu.style.display = 'block';
    } else {
        userMenu.style.display = 'none';
    }
}

function toggleNotifications() {
    const notificationPanel = document.getElementById('notification-panel');
    notificationPanelOpen = !notificationPanelOpen;
    
    if (notificationPanelOpen) {
        notificationPanel.style.display = 'block';
        notificationPanel.classList.add('active');
    } else {
        notificationPanel.classList.remove('active');
        setTimeout(() => {
            notificationPanel.style.display = 'none';
        }, 300);
    }
}

function toggleFabMenu() {
    const fabMenu = document.getElementById('fab-menu');
    const fabIcon = document.getElementById('fab-icon');
    
    fabMenuOpen = !fabMenuOpen;
    
    if (fabMenuOpen) {
        fabMenu.classList.add('active');
        fabIcon.style.transform = 'rotate(45deg)';
    } else {
        fabMenu.classList.remove('active');
        fabIcon.style.transform = 'rotate(0deg)';
    }
}

function closeFabMenu() {
    if (fabMenuOpen) {
        toggleFabMenu();
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
        <button class="btn-primary" onclick="submitSchedule()">Отправить расписание</button>
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
        <button class="btn-primary" onclick="submitAnnouncement()">Отправить объявление</button>
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
        <button class="btn-primary" onclick="submitPoll()">Создать голосование</button>
    `);
}

function openQuestionForm() {
    closeFabMenu();
    openModal('❓ Задать вопрос', `
        <div class="form-group">
            <label class="form-label">Ваш вопрос:</label>
            <textarea class="form-textarea" id="question-text-modal" placeholder="Введите ваш вопрос..."></textarea>
        </div>
        <button class="btn-primary" onclick="submitQuestionModal()">Отправить вопрос</button>
    `);
}

function submitSchedule() {
    const scheduleText = document.getElementById('schedule-text').value.trim();
    if (scheduleText) {
        showToast('Расписание отправлено!', 'success');
        closeModal();
    } else {
        showToast('Пожалуйста, введите расписание', 'error');
    }
}

function submitAnnouncement() {
    const title = document.getElementById('announcement-title').value.trim();
    const text = document.getElementById('announcement-text').value.trim();
    
    if (title && text) {
        showToast('Объявление отправлено!', 'success');
        closeModal();
    } else {
        showToast('Пожалуйста, заполните все поля', 'error');
    }
}

function submitPoll() {
    const title = document.getElementById('poll-title').value.trim();
    const duration = document.getElementById('poll-duration').value;
    
    if (title && duration) {
        showToast('Голосование создано!', 'success');
        closeModal();
    } else {
        showToast('Пожалуйста, заполните все поля', 'error');
    }
}

function submitQuestionModal() {
    const questionText = document.getElementById('question-text-modal').value.trim();
    if (questionText) {
        showToast('Вопрос отправлен!', 'success');
        closeModal();
    } else {
        showToast('Пожалуйста, введите вопрос', 'error');
    }
}

// Quick actions
function askQuickQuestion() {
    openQuestionForm();
}

function viewAttendance() {
    showToast('Просмотр посещаемости', 'info');
}

function viewGrades() {
    showToast('Просмотр оценок', 'info');
}

function viewCalendar() {
    showToast('Просмотр календаря', 'info');
}

function exportSchedule() {
    showToast('Экспорт расписания', 'info');
}

function refreshTodaySchedule() {
    showToast('Расписание обновлено', 'success');
}

function switchTab(tabName) {
    const tab = document.querySelector(`[data-tab="${tabName}"]`);
    if (tab) {
        tab.click();
    }
}

// Profile and settings
function showProfile() {
    showToast('Профиль пользователя', 'info');
    userMenuOpen = false;
    document.getElementById('user-menu').style.display = 'none';
}

function showSettings() {
    showToast('Настройки приложения', 'info');
    userMenuOpen = false;
    document.getElementById('user-menu').style.display = 'none';
}

function logout() {
    showToast('Выход из приложения', 'info');
    userMenuOpen = false;
    document.getElementById('user-menu').style.display = 'none';
}

// Toast notifications
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = getToastIcon(type);
    toast.innerHTML = `
        <i class="${icon}"></i>
        <span>${message}</span>
    `;
    
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease-out reverse';
        setTimeout(() => {
            toastContainer.removeChild(toast);
        }, 300);
    }, 3000);
}

function getToastIcon(type) {
    switch(type) {
        case 'success': return 'fas fa-check-circle';
        case 'error': return 'fas fa-exclamation-circle';
        case 'warning': return 'fas fa-exclamation-triangle';
        case 'info': return 'fas fa-info-circle';
        default: return 'fas fa-info-circle';
    }
}

// Event listeners
document.addEventListener('click', function(event) {
    // Close modals and menus when clicking outside
    const modal = document.getElementById('modal');
    const userMenu = document.getElementById('user-menu');
    
    if (event.target === modal) {
        closeModal();
    }
    
    if (!event.target.closest('.user-profile') && userMenuOpen) {
        userMenuOpen = false;
        userMenu.style.display = 'none';
    }
});

// Handle back button (safe)
try {
    tg.onEvent('backButtonClicked', function() {
        if (document.getElementById('modal').style.display === 'flex') {
            closeModal();
        } else if (fabMenuOpen) {
            closeFabMenu();
        } else if (notificationPanelOpen) {
            toggleNotifications();
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

// Form styles
const formStyles = `
    .form-group {
        margin-bottom: 1.5rem;
    }
    
    .form-label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 500;
        color: var(--text-primary);
    }
    
    .form-input, .form-textarea {
        width: 100%;
        padding: 0.75rem;
        border: 2px solid var(--border-color);
        border-radius: var(--border-radius);
        background: var(--bg-primary);
        color: var(--text-primary);
        font-size: 1rem;
        transition: var(--transition);
    }
    
    .form-input:focus, .form-textarea:focus {
        outline: none;
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .form-textarea {
        resize: vertical;
        min-height: 100px;
    }
`;

// Add form styles to head
const styleSheet = document.createElement('style');
styleSheet.textContent = formStyles;
document.head.appendChild(styleSheet);
