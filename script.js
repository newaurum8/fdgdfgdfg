document.addEventListener('DOMContentLoaded', function() {
    // Show loading screen initially
    setTimeout(() => {
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) loadingScreen.classList.add('hidden');
    }, 2000);

    // --- УЛУЧШЕННЫЙ ГЛОБАЛЬНИЙ СТАН ---
    const STATE = {
        userBalance: 1250,
        userGems: 0,
        userLevel: 1,
        userExp: 0,
        userExpMax: 1000,
        inventory: [],
        gameHistory: [],
        isSpinning: false,
        openQuantity: 1,
        currentCaseType: 'common',
        fastOpen: false,
        lastWonItems: [],
        contestTicketPrice: 100,
        ticketQuantity: 1,
        userTickets: 0,
        contestEndDate: new Date(Date.now() + 6 * 24 * 60 * 60 * 1000 + 15 * 60 * 60 * 1000),
        
        // Улучшенные предметы с редкостью
        possibleItems: {
            common: [
                { id: 1, name: 'Stone', imageSrc: 'case.png', value: 50, rarity: 'common' },
                { id: 2, name: 'Wood', imageSrc: 'item1.png', value: 75, rarity: 'common' },
                { id: 3, name: 'Coal', imageSrc: 'coin.png', value: 100, rarity: 'common' },
            ],
            rare: [
                { id: 4, name: 'Iron', imageSrc: 'miner.png', value: 250, rarity: 'rare' },
                { id: 5, name: 'Silver', imageSrc: 'item.png', value: 350, rarity: 'rare' },
                { id: 6, name: 'Emerald', imageSrc: 'diamond.png', value: 500, rarity: 'rare' },
            ],
            epic: [
                { id: 7, name: 'Gold', imageSrc: 'coin.png', value: 1000, rarity: 'epic' },
                { id: 8, name: 'Platinum', imageSrc: 'item1.png', value: 1500, rarity: 'epic' },
                { id: 9, name: 'Ruby', imageSrc: 'diamond.png', value: 2000, rarity: 'epic' },
            ],
            legendary: [
                { id: 10, name: 'Diamond', imageSrc: 'diamond.png', value: 5000, rarity: 'legendary' },
                { id: 11, name: 'Star Crystal', imageSrc: 'item.png', value: 10000, rarity: 'legendary' },
                { id: 12, name: 'Mythril', imageSrc: 'miner.png', value: 15000, rarity: 'legendary' },
            ]
        },

        caseTypes: {
            common: { price: 100, name: 'Обычный' },
            rare: { price: 250, name: 'Редкий' },
            epic: { price: 500, name: 'Эпический' },
            legendary: { price: 1000, name: 'Легендарный' }
        },

        // Статистика игрока
        stats: {
            totalOpened: 0,
            totalWon: 0,
            biggestWin: 0,
            totalGamesPlayed: 0,
            referrals: 0,
            referralBonus: 0
        },

        // Статистика игр
        gameStats: {
            coinflip: { total: 0, wins: 0 },
            rps: { total: 0, wins: 0, draws: 0 },
            slots: { total: 0, wins: 0 },
            crash: { total: 0, wins: 0, bestMultiplier: 1 },
            blackjack: { total: 0, wins: 0 },
            miner: { total: 0, wins: 0 },
            tower: { total: 0, wins: 0 }
        },

        // Достижения
        achievements: [
            { id: 1, name: 'Первый кейс', description: 'Откройте первый кейс', completed: false, reward: 100 },
            { id: 2, name: 'Коллекционер', description: 'Откройте 10 кейсов', completed: false, reward: 500 },
            { id: 3, name: 'Удачливый', description: 'Выиграйте предмет стоимостью более 1000 ⭐', completed: false, reward: 250 },
            { id: 4, name: 'Миллионер', description: 'Накопите 10000 ⭐', completed: false, reward: 1000 },
            { id: 5, name: 'Игроман', description: 'Сыграйте 50 мини-игр', completed: false, reward: 750 },
        ],

        // Ежедневные задания
        dailyTasks: [
            { id: 1, name: 'Открыть 5 кейсов', progress: 0, target: 5, reward: 200, completed: false },
            { id: 2, name: 'Выиграть в любой игре 3 раза', progress: 0, target: 3, reward: 150, completed: false },
            { id: 3, name: 'Пригласить друга', progress: 0, target: 1, reward: 500, completed: false },
        ],
        upgradeState: {
            yourItem: null,
            desiredItem: null,
            chance: 0,
            multiplier: 0,
            isUpgrading: false,
            activePicker: 'inventory',
            maxChance: 95,
            currentRotation: 0,
        },
        minerState: {
            isActive: false,
            bet: 100,
            bombs: 6,
            grid: [],
            openedCrystals: 0,
            currentMultiplier: 1,
            totalWin: 0,
        },
        coinflipState: {
            isFlipping: false,
        },
        rpsState: {
            isPlaying: false,
        },
        slotsState: {
            isSpinning: false,
            symbols: [
                { name: 'Lemon', imageSrc: 'slot_lemon.png', multiplier: 10 },
                { name: 'Cherry', imageSrc: 'slot_cherry.png', multiplier: 5 },
                { name: 'Seven', imageSrc: 'slot_7.png', multiplier: 20 },
            ]
        },
        towerState: {
            isActive: false,
            bet: 100,
            currentLevel: 0,
            grid: [], // 0 for left bomb, 1 for right bomb
            payouts: []
        },
        
        // Новые игры
        crashState: {
            isActive: false,
            bet: 100,
            autoCashout: 2.0,
            currentMultiplier: 1.0,
            hasPlacedBet: false,
            gameStartTime: 0,
            history: []
        },
        
        blackjackState: {
            isActive: false,
            bet: 100,
            playerCards: [],
            dealerCards: [],
            playerScore: 0,
            dealerScore: 0,
            gamePhase: 'betting', // betting, playing, dealer, finished
            canDouble: false,
            deck: []
        }
    };

    // --- ОБ'ЄКТ З ЕЛЕМЕНТАМИ DOM ---
    const UI = {};

    // --- ФУНКЦІЇ ---

    function showNotification(message) {
        if (!UI.notificationToast) return;
        UI.notificationToast.textContent = message;
        UI.notificationToast.classList.add('visible');
        setTimeout(() => UI.notificationToast.classList.remove('visible'), 3000);
    }

    function loadTelegramData() {
        try {
            const tg = window.Telegram.WebApp;
            tg.BackButton.hide();
            const user = tg.initDataUnsafe.user;
            if (user) {
                if (UI.profilePhoto) UI.profilePhoto.src = user.photo_url || '';
                if (UI.profileName) UI.profileName.textContent = `${user.first_name || ''} ${user.last_name || ''}`.trim();
                if (UI.profileId) UI.profileId.textContent = `ID ${user.id}`;
            }
        } catch (error) {
            console.error("Не вдалося завантажити дані Telegram:", error);
            if (UI.profileName) UI.profileName.textContent = "Guest";
            if (UI.profileId) UI.profileId.textContent = "ID 0";
        }
    }

    function inviteFriend() {
        try {
            const tg = window.Telegram.WebApp;
            const user = tg.initDataUnsafe.user;
            const app_url = `https://t.me/qqtest134_bot/website?startapp=${user.id}`;
            const text = `Привіт! Приєднуйся до StarsDrop та отримуй круті подарунки!`;
            tg.openTelegramLink(`https://t.me/share/url?url=${encodeURIComponent(app_url)}&text=${encodeURIComponent(text)}`);
        } catch(e) {
            console.error(e);
            showNotification("Функція доступна лише в Telegram.");
        }
    }

    function copyInviteLink() {
        try {
            const tg = window.Telegram.WebApp;
            const user = tg.initDataUnsafe.user;
            const app_url = `https://t.me/qqtest134_bot/website?startapp=${user.id}`;
            navigator.clipboard.writeText(app_url).then(() => {
                showNotification('Посилання скопійовано!');
            }).catch(err => {
                console.error('Не вдалося скопіювати посилання: ', err);
                showNotification('Помилка копіювання.');
            });
        } catch(e) {
            console.error(e);
            showNotification("Функція доступна лише в Telegram.");
        }
    }

    function updateBalanceDisplay() {
        if (UI.userBalanceElement) UI.userBalanceElement.innerText = Math.round(STATE.userBalance).toLocaleString('uk-UA');
        if (UI.userGemsElement) UI.userGemsElement.innerText = STATE.userGems;
        if (UI.userLevelElement) UI.userLevelElement.innerText = STATE.userLevel;
    }

    function updateProfileStats() {
        if (UI.totalOpenedElement) UI.totalOpenedElement.textContent = STATE.stats.totalOpened;
        if (UI.totalWonElement) UI.totalWonElement.textContent = STATE.stats.totalWon.toLocaleString('uk-UA');
        if (UI.biggestWinElement) UI.biggestWinElement.textContent = STATE.stats.biggestWin.toLocaleString('uk-UA');
        if (UI.profileLevelElement) UI.profileLevelElement.textContent = STATE.userLevel;
        if (UI.profileExpElement) UI.profileExpElement.textContent = STATE.userExp;
        if (UI.profileExpMaxElement) UI.profileExpMaxElement.textContent = STATE.userExpMax;
        if (UI.profileExpBar) {
            const progress = (STATE.userExp / STATE.userExpMax) * 100;
            UI.profileExpBar.style.width = `${progress}%`;
        }
    }

    function addExperience(amount) {
        STATE.userExp += amount;
        while (STATE.userExp >= STATE.userExpMax) {
            STATE.userExp -= STATE.userExpMax;
            STATE.userLevel++;
            STATE.userExpMax = Math.floor(STATE.userExpMax * 1.5);
            showNotification(`🎉 Уровень повышен до ${STATE.userLevel}!`);
            showAchievement(`Новый уровень ${STATE.userLevel}!`, 'Вы получили 100 ⭐');
            STATE.userBalance += 100;
        }
        updateBalanceDisplay();
        updateProfileStats();
    }

    function showAchievement(title, description) {
        const toast = UI.achievementToast;
        if (!toast) return;
        toast.innerHTML = `<div><strong>${title}</strong><br>${description}</div>`;
        toast.classList.add('visible');
        setTimeout(() => toast.classList.remove('visible'), 4000);
    }

    function checkAchievements() {
        STATE.achievements.forEach(achievement => {
            if (achievement.completed) return;
            
            let shouldComplete = false;
            switch (achievement.id) {
                case 1: // Первый кейс
                    shouldComplete = STATE.stats.totalOpened >= 1;
                    break;
                case 2: // 10 кейсов
                    shouldComplete = STATE.stats.totalOpened >= 10;
                    break;
                case 3: // Выигрыш > 1000
                    shouldComplete = STATE.stats.biggestWin >= 1000;
                    break;
                case 4: // 10000 звезд
                    shouldComplete = STATE.userBalance >= 10000;
                    break;
                case 5: // 50 игр
                    shouldComplete = STATE.stats.totalGamesPlayed >= 50;
                    break;
            }
            
            if (shouldComplete) {
                achievement.completed = true;
                STATE.userBalance += achievement.reward;
                showAchievement(`Достижение разблокировано!`, `${achievement.name} (+${achievement.reward} ⭐)`);
                updateBalanceDisplay();
            }
        });
    }

    function updateCaseInfo() {
        const caseType = STATE.currentCaseType;
        const casePrice = STATE.caseTypes[caseType].price;
        const caseName = STATE.caseTypes[caseType].name;
        
        if (UI.caseTitleElement) UI.caseTitleElement.textContent = `${caseName} кейс`;
        if (UI.casePriceElement) UI.casePriceElement.textContent = `⭐ ${casePrice}`;
        if (UI.spinCaseTitleElement) UI.spinCaseTitleElement.textContent = `${caseName} кейс`;
    }

    function switchCaseType(caseType) {
        STATE.currentCaseType = caseType;
        updateCaseInfo();
        updatePriceMessage();
        populateCasePreview();
        
        // Update active button
        document.querySelectorAll('.case-type-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.case === caseType);
        });
    }

    function showModal(modal) {
        if (modal && UI.modalOverlay) {
            modal.classList.add('visible');
            UI.modalOverlay.classList.add('visible');
        }
    }

    function hideModal(modal) {
        if (modal && UI.modalOverlay) {
            modal.classList.remove('visible');
            if (!document.querySelector('.modal.visible')) {
                UI.modalOverlay.classList.remove('visible');
            }
        }
    }

    function switchView(viewId) {
        UI.views.forEach(view => {
            view.style.display = 'none';
            view.classList.remove('active');
        });
        UI.navButtons.forEach(btn => btn.classList.remove('active'));

        const viewToShow = document.getElementById(viewId);
        let btnToActivate;

        if (viewToShow) {
            viewToShow.style.display = 'flex';
            viewToShow.classList.add('active');
            if (['upgrade-view', 'miner-view', 'coinflip-view', 'rps-view', 'slots-view', 'tower-view'].includes(viewId)) {
                btnToActivate = document.querySelector('.nav-btn[data-view="games-menu-view"]');
            } else {
                btnToActivate = document.querySelector(`.nav-btn[data-view="${viewId}"]`);
            }
        } else {
            console.error(`Экран с ID "${viewId}" не найден. Возврат на главный экран.`);
            document.getElementById('game-view').style.display = 'flex';
            document.getElementById('game-view').classList.add('active');
            btnToActivate = document.querySelector('.nav-btn[data-view="game-view"]');
        }

        if (btnToActivate) {
            btnToActivate.classList.add('active');
        }

        if (window.Telegram && window.Telegram.WebApp) {
            const tg = window.Telegram.WebApp;
            if (tg.BackButton.isVisible) {
                tg.BackButton.offClick();
            }

            if (['upgrade-view', 'miner-view', 'coinflip-view', 'rps-view', 'slots-view', 'tower-view'].includes(viewId)) {
                tg.BackButton.show();
                tg.BackButton.onClick(() => switchView('games-menu-view'));
            } else if (['games-menu-view', 'contests-view', 'friends-view', 'profile-view'].includes(viewId)) {
                tg.BackButton.show();
                tg.BackButton.onClick(() => switchView('game-view'));
            } else {
                tg.BackButton.hide();
            }
        }

        if (viewId === 'profile-view') {
            renderInventory();
            renderHistory();
        }
        if (viewId === 'upgrade-view') {
            resetUpgradeState(true);
        }
        if (viewId === 'contests-view') {
            updateContestUI();
        }
        if (viewId === 'miner-view') {
            resetMinerGame();
        }
        if(viewId === 'tower-view') {
            resetTowerGame();
        }
        if(viewId === 'crash-view') {
            initCrashGame();
        }
        if(viewId === 'blackjack-view') {
            resetBlackjackGame();
        }
    }

    function renderInventory() {
        if (!UI.inventoryContent) return;
        UI.inventoryContent.innerHTML = '';
        if (STATE.inventory.length === 0) {
            UI.inventoryContent.innerHTML = `<p class="inventory-empty-msg">Ваш інвентар порожній</p>`;
            return;
        }
        STATE.inventory.forEach((item) => {
            const itemEl = document.createElement('div');
            itemEl.classList.add('inventory-item');
            itemEl.innerHTML = `
                <img src="${item.imageSrc}" alt="${item.name}">
                <div class="inventory-item-name">${item.name}</div>
                <button class="inventory-sell-btn">
                    Продати за <span class="icon">⭐</span> ${item.value.toLocaleString('uk-UA')}
                </button>
            `;
            itemEl.querySelector('.inventory-sell-btn').addEventListener('click', () => sellFromInventory(item.uniqueId));
            UI.inventoryContent.appendChild(itemEl);
        });
    }

    function sellFromInventory(uniqueId) {
        const itemIndex = STATE.inventory.findIndex(item => item.uniqueId === uniqueId);
        if (itemIndex === -1) return;
        const item = STATE.inventory[itemIndex];
        STATE.userBalance += item.value;
        updateBalanceDisplay();
        STATE.inventory.splice(itemIndex, 1);
        renderInventory();
    }

    function renderHistory() {
        if (!UI.historyContent) return;
        UI.historyContent.innerHTML = '';
        if (STATE.gameHistory.length === 0) {
            UI.historyContent.innerHTML = `<p class="inventory-empty-msg">Історія ігор порожня</p>`;
            return;
        }
        [...STATE.gameHistory].reverse().forEach(entry => {
            const itemEl = document.createElement('div');
            itemEl.classList.add('history-item');
            const eventDate = new Date(entry.date);
            itemEl.innerHTML = `
                <img src="${entry.imageSrc}" alt="${entry.name}">
                <div class="history-item-info">
                    <div class="history-item-name">${entry.name}</div>
                    <div class="history-item-date">${eventDate.toLocaleString('uk-UA')}</div>
                </div>
                <div class="history-item-price">+<span class="icon">⭐</span>${entry.value.toLocaleString('uk-UA')}</div>
            `;
            UI.historyContent.appendChild(itemEl);
        });
    }
    
    function handleCaseClick() {
        updatePriceMessage();
        showModal(UI.preOpenModal);
    }

    function updatePriceMessage() {
        const casePrice = STATE.caseTypes[STATE.currentCaseType].price;
        const totalCost = casePrice * STATE.openQuantity;
        if (STATE.userBalance >= totalCost) {
            UI.priceCheckMessage.innerHTML = `⭐ ${totalCost.toLocaleString('uk-UA')}`;
            UI.priceCheckMessage.classList.remove('error');
        } else {
            UI.priceCheckMessage.innerHTML = `⭐ ${totalCost.toLocaleString('uk-UA')} (не хватает ${(totalCost - STATE.userBalance).toLocaleString('uk-UA')})`;
            UI.priceCheckMessage.classList.add('error');
        }
    }

    function handleQuantityChange(event) {
        const target = event.target;
        if (target.classList.contains('quantity-btn')) {
            UI.quantitySelector.querySelector('.active').classList.remove('active');
            target.classList.add('active');
            STATE.openQuantity = parseInt(target.innerText);
            updatePriceMessage();
        }
    }

    function startSpinProcess() {
        if (STATE.isSpinning) return;
        const casePrice = STATE.caseTypes[STATE.currentCaseType].price;
        const totalCost = casePrice * STATE.openQuantity;
        if (STATE.userBalance < totalCost) return;

        STATE.isSpinning = true;
        STATE.userBalance -= totalCost;
        STATE.fastOpen = document.getElementById('fast-open-checkbox')?.checked || false;
        updateBalanceDisplay();
        hideModal(UI.preOpenModal);
        
        const wonItems = [];
        for (let i = 0; i < STATE.openQuantity; i++) {
            const winnerData = getRandomItemByRarity();
            wonItems.push({ ...winnerData, uniqueId: Date.now() + i });
        }
        
        STATE.lastWonItems = wonItems;
        STATE.inventory.push(...wonItems);
        STATE.gameHistory.push(...wonItems.map(item => ({ ...item, date: new Date() })));
        
        // Обновляем статистику
        STATE.stats.totalOpened += STATE.openQuantity;
        const totalValue = wonItems.reduce((sum, item) => sum + item.value, 0);
        STATE.stats.totalWon += totalValue;
        if (totalValue > STATE.stats.biggestWin) {
            STATE.stats.biggestWin = totalValue;
        }
        
        addExperience(STATE.openQuantity * 10);
        checkAchievements();
        updateProfileStats();

        UI.caseView.classList.add('hidden');
        UI.spinView.classList.remove('hidden');
        
        if (STATE.fastOpen) {
            // Мгновенное открытие
            setTimeout(() => showResult(), 500);
        } else if (STATE.openQuantity > 1) {
            startMultiVerticalAnimation();
        } else {
            startHorizontalAnimation();
        }
    }

    function getRandomItemByRarity() {
        const caseType = STATE.currentCaseType;
        let rarityChances = {};
        
        // Настройка шансов в зависимости от типа кейса
        switch (caseType) {
            case 'common':
                rarityChances = { common: 60, rare: 30, epic: 9, legendary: 1 };
                break;
            case 'rare':
                rarityChances = { common: 40, rare: 40, epic: 18, legendary: 2 };
                break;
            case 'epic':
                rarityChances = { common: 20, rare: 35, epic: 35, legendary: 10 };
                break;
            case 'legendary':
                rarityChances = { common: 10, rare: 20, epic: 40, legendary: 30 };
                break;
        }
        
        const random = Math.random() * 100;
        let cumulative = 0;
        
        for (const [rarity, chance] of Object.entries(rarityChances)) {
            cumulative += chance;
            if (random <= cumulative) {
                const items = STATE.possibleItems[rarity];
                return items[Math.floor(Math.random() * items.length)];
            }
        }
        
        // Fallback
        return STATE.possibleItems.common[0];
    }

    function startHorizontalAnimation() {
        UI.spinnerContainer.classList.remove('hidden');
        UI.multiSpinnerContainer.classList.add('hidden');
        
        const winnerItem = STATE.lastWonItems[0];
        const reelLength = 60, winnerIndex = 50;
        const reel = Array.from({ length: reelLength }, (_, i) => i === winnerIndex ? winnerItem : STATE.possibleItems[Math.floor(Math.random() * STATE.possibleItems.length)]);

        UI.rouletteTrack.innerHTML = '';
        reel.forEach(item => {
            const itemEl = document.createElement('div');
            itemEl.classList.add('roulette-item');
            itemEl.innerHTML = `<img src="${item.imageSrc}" alt="${item.name}">`;
            UI.rouletteTrack.appendChild(itemEl);
        });
        
        const itemWidth = 120, itemMargin = 5, totalItemWidth = itemWidth + (itemMargin * 2);
        const targetPosition = (winnerIndex * totalItemWidth) + (totalItemWidth / 2);

        UI.rouletteTrack.style.transition = 'none';
        UI.rouletteTrack.style.left = '0px';
        UI.rouletteTrack.getBoundingClientRect(); 
        UI.rouletteTrack.style.transition = 'left 6s cubic-bezier(0.2, 0.8, 0.2, 1)';
        UI.rouletteTrack.style.left = `calc(50% - ${targetPosition}px)`;
        
        UI.rouletteTrack.addEventListener('transitionend', showResult, { once: true });
    }

    function startMultiVerticalAnimation() {
        UI.spinnerContainer.classList.add('hidden');
        UI.multiSpinnerContainer.classList.remove('hidden');
        UI.multiSpinnerContainer.innerHTML = '';

        let animationsFinished = 0;
        STATE.lastWonItems.forEach((winnerItem) => {
            const spinnerColumn = document.createElement('div');
            spinnerColumn.classList.add('vertical-spinner');
            const track = document.createElement('div');
            track.classList.add('vertical-roulette-track');

            const reelLength = 60, winnerIndex = 50;
            const reel = Array.from({ length: reelLength }, (_, i) => i === winnerIndex ? winnerItem : STATE.possibleItems[Math.floor(Math.random() * STATE.possibleItems.length)]);
            
            reel.forEach(item => {
                const itemEl = document.createElement('div');
                itemEl.classList.add('vertical-roulette-item');
                itemEl.innerHTML = `<img src="${item.imageSrc}" alt="${item.name}">`;
                track.appendChild(itemEl);
            });
            
            spinnerColumn.appendChild(track);
            UI.multiSpinnerContainer.appendChild(spinnerColumn);

            const itemHeight = 100, itemMargin = 5, totalItemHeight = itemHeight + (itemMargin * 2);
            const targetPosition = (winnerIndex * totalItemHeight) + (totalItemHeight / 2);

            track.style.transition = 'none';
            track.style.top = '0px';
            track.getBoundingClientRect(); 
            track.style.transition = `top ${5 + Math.random() * 2}s cubic-bezier(0.2, 0.8, 0.2, 1)`;
            track.style.top = `calc(50% - ${targetPosition}px)`;

            track.addEventListener('transitionend', () => {
                animationsFinished++;
                if (animationsFinished === STATE.lastWonItems.length) showResult();
            }, { once: true });
        });
    }

    function showResult() {
        UI.resultModal.innerHTML = '';
        const totalValue = STATE.lastWonItems.reduce((sum, item) => sum + item.value, 0);
        const modalContent = document.createElement('div');
        modalContent.classList.add('modal-content');
        modalContent.innerHTML = `
            <button class="close-btn">✖</button>
            <h2 class="modal-case-title">Ваш виграш:</h2>
            <div class="result-items-container"></div>
            <div class="result-buttons">
                <button class="secondary-button" id="result-sell-btn">Продати все за ⭐ ${totalValue.toLocaleString('uk-UA')}</button>
                <button class="primary-button" id="result-spin-again-btn">Крутити ще</button>
            </div>
        `;
        const itemsContainer = modalContent.querySelector('.result-items-container');
        STATE.lastWonItems.forEach(item => {
            const itemEl = document.createElement('div');
            itemEl.classList.add('inventory-item');
            itemEl.innerHTML = `
                <img src="${item.imageSrc}" alt="${item.name}">
                <div class="inventory-item-name">${item.name}</div>
                <div class="inventory-item-price">⭐ ${item.value.toLocaleString('uk-UA')}</div>
            `;
            itemsContainer.appendChild(itemEl);
        });
        UI.resultModal.appendChild(modalContent);

        const closeBtn = modalContent.querySelector('.close-btn'), sellBtn = modalContent.querySelector('#result-sell-btn'), spinAgainBtn = modalContent.querySelector('#result-spin-again-btn');
        const finalizeAction = () => {
            hideModal(UI.resultModal);
            UI.spinView.classList.add('hidden');
            UI.caseView.classList.remove('hidden');
            STATE.isSpinning = false;
        };
        closeBtn.addEventListener('click', finalizeAction);
        spinAgainBtn.addEventListener('click', () => {
            finalizeAction();
            setTimeout(handleCaseClick, 100);
        });
        sellBtn.addEventListener('click', () => {
            STATE.userBalance += totalValue;
            updateBalanceDisplay();
            const idsToRemove = new Set(STATE.lastWonItems.map(item => item.uniqueId));
            STATE.inventory = STATE.inventory.filter(invItem => !idsToRemove.has(invItem.uniqueId));
            finalizeAction();
        });
        showModal(UI.resultModal);
    }

    function populateCasePreview() {
        if (!UI.caseContentsPreview) return;
        UI.caseContentsPreview.innerHTML = '';
        
        const allItems = [];
        Object.values(STATE.possibleItems).forEach(rarityItems => {
            allItems.push(...rarityItems);
        });
        
        allItems.sort((a, b) => b.value - a.value).forEach(item => {
            const itemEl = document.createElement('div');
            itemEl.classList.add('preview-item');
            itemEl.classList.add(`rarity-${item.rarity}`);
            itemEl.innerHTML = `<img src="${item.imageSrc}" alt="${item.name}"><div class="inventory-item-price">⭐ ${item.value.toLocaleString('uk-UA')}</div>`;
            UI.caseContentsPreview.appendChild(itemEl);
        });
    }

    // --- ЛОГИКА КОНКУРСОВ ---
    function updateContestUI() {
        if (!UI.buyTicketBtn) return;
        const totalCost = STATE.contestTicketPrice * STATE.ticketQuantity;
        UI.buyTicketBtn.innerHTML = `Купить билет <span class="icon">⭐</span> ${totalCost.toLocaleString('uk-UA')}`;
        UI.ticketQuantityInput.value = STATE.ticketQuantity;
        UI.userTicketsDisplay.textContent = STATE.userTickets;
        UI.buyTicketBtn.disabled = STATE.userBalance < totalCost;
    }

    function handleTicketQuantityChange(amount) {
        const newQuantity = STATE.ticketQuantity + amount;
        if (newQuantity >= 1) {
            STATE.ticketQuantity = newQuantity;
            updateContestUI();
        }
    }

    function buyTickets() {
        const totalCost = STATE.contestTicketPrice * STATE.ticketQuantity;
        if (STATE.userBalance < totalCost) {
            showNotification('Недостатньо коштів.');
            return;
        }
        STATE.userBalance -= totalCost;
        STATE.userTickets += STATE.ticketQuantity;
        showNotification(`Ви успішно придбали ${STATE.ticketQuantity} білет(ів)!`);
        updateBalanceDisplay();
        updateContestUI();
    }

    function updateTimer() {
        if (!UI.contestTimer) return;
        const now = new Date(), timeLeft = STATE.contestEndDate - now;
        if (timeLeft <= 0) {
            UI.contestTimer.textContent = 'Конкурс завершено';
            return;
        }
        const days = Math.floor(timeLeft / 86400000), hours = Math.floor((timeLeft % 86400000) / 3600000), minutes = Math.floor((timeLeft % 3600000) / 60000), seconds = Math.floor((timeLeft % 60000) / 1000);
        UI.contestTimer.textContent = `${days} дней ${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')} 🕔`;
    }
    // --- КОНЕЦ ЛОГИКИ КОНКУРСОВ ---

    // --- ЛОГИКА АПГРЕЙДА ---
    function resetUpgradeState(resetRotation = false) {
        STATE.upgradeState.yourItem = null;
        STATE.upgradeState.desiredItem = null;
        STATE.upgradeState.isUpgrading = false;
        if (resetRotation) {
            STATE.upgradeState.currentRotation = 0;
            if (UI.upgradePointer) {
                UI.upgradePointer.style.transition = 'none';
                UI.upgradePointer.style.transform = `translateX(-50%) rotate(0deg)`;
            }
        }
        calculateUpgradeChance();
        renderUpgradeUI();
        renderItemPicker();
    }

    function calculateUpgradeChance() {
        const { yourItem, desiredItem, maxChance } = STATE.upgradeState;
        if (!yourItem || !desiredItem) {
            STATE.upgradeState.chance = 0;
            STATE.upgradeState.multiplier = 0;
            return;
        }
        if (desiredItem.value <= yourItem.value) {
            STATE.upgradeState.chance = maxChance;
            STATE.upgradeState.multiplier = desiredItem.value / yourItem.value;
            return;
        }
        const chance = (yourItem.value / desiredItem.value) * (maxChance / 100) * 100;
        STATE.upgradeState.chance = Math.min(chance, maxChance);
        STATE.upgradeState.multiplier = desiredItem.value / yourItem.value;
    }

    function renderUpgradeUI() {
        if (!UI.yourItemSlot) return;
        const { yourItem, desiredItem, chance, multiplier } = STATE.upgradeState;
        function updateSlot(slot, item) {
            const placeholder = slot.querySelector('.slot-placeholder'), content = slot.querySelector('.slot-content');
            if (item) {
                placeholder.classList.add('hidden');
                content.classList.remove('hidden');
                content.querySelector('img').src = item.imageSrc;
                content.querySelector('img').alt = item.name;
                content.querySelector('span').textContent = item.name;
            } else {
                placeholder.classList.remove('hidden');
                content.classList.add('hidden');
            }
        }
        updateSlot(UI.yourItemSlot, yourItem);
        updateSlot(UI.desiredItemSlot, desiredItem);
        UI.upgradeChanceDisplay.textContent = `${chance.toFixed(2)}%`;
        UI.upgradeMultiplierDisplay.textContent = `x${multiplier.toFixed(2)}`;
        const angle = (chance / 100) * 360;
        UI.upgradeWheel.style.backgroundImage = `conic-gradient(var(--accent-color) ${angle}deg, var(--card-bg-color) ${angle}deg)`;
        UI.performUpgradeBtn.disabled = !yourItem || !desiredItem || STATE.upgradeState.isUpgrading;
    }

    function renderItemPicker() {
        if (!UI.itemPickerContent) return;
        UI.itemPickerContent.innerHTML = '';
        const { activePicker, yourItem, desiredItem } = STATE.upgradeState;
        const sourceList = activePicker === 'inventory' ? STATE.inventory : STATE.possibleItems;
        if (sourceList.length === 0) {
            UI.itemPickerContent.innerHTML = `<p class="picker-empty-msg">Список порожній</p>`;
            return;
        }
        sourceList.forEach(item => {
            const itemEl = document.createElement('div');
            itemEl.className = 'picker-item';
            itemEl.innerHTML = `<img src="${item.imageSrc}" alt="${item.name}"><div class="picker-item-name">${item.name}</div><div class="picker-item-value">⭐ ${item.value.toLocaleString('uk-UA')}</div>`;
            const isSelectedForYour = yourItem && item.uniqueId && yourItem.uniqueId === item.uniqueId;
            const isSelectedForDesired = desiredItem && desiredItem.id === item.id;
            if (isSelectedForYour || isSelectedForDesired) itemEl.classList.add('selected');
            itemEl.addEventListener('click', () => handleItemPick(item));
            UI.itemPickerContent.appendChild(itemEl);
        });
    }

    function handleItemPick(item) {
        if (STATE.upgradeState.isUpgrading) return;
        const { activePicker } = STATE.upgradeState;
        if (activePicker === 'inventory') STATE.upgradeState.yourItem = { ...item }; 
        else STATE.upgradeState.desiredItem = { ...item };
        calculateUpgradeChance();
        renderUpgradeUI();
        renderItemPicker();
    }

    function handleUpgradeClick() {
        const { yourItem, desiredItem, chance, isUpgrading } = STATE.upgradeState;
        if (!yourItem || !desiredItem || isUpgrading) return;
        STATE.upgradeState.isUpgrading = true;
        UI.performUpgradeBtn.disabled = true;
        const isSuccess = (Math.random() * 100) < chance;
        const chanceAngle = (chance / 100) * 360;
        const randomOffset = Math.random() * 0.9 + 0.05;
        const stopPoint = isSuccess ? chanceAngle * randomOffset : chanceAngle + (360 - chanceAngle) * randomOffset;
        const rotation = (5 * 360) + stopPoint;
        STATE.upgradeState.currentRotation = rotation;

        UI.upgradePointer.style.transition = 'transform 6s cubic-bezier(0.2, 0.8, 0.2, 1)';
        UI.upgradePointer.style.transform = `translateX(-50%) rotate(${STATE.upgradeState.currentRotation}deg)`;

        UI.upgradePointer.addEventListener('transitionend', () => {
            setTimeout(() => {
                const itemIndex = STATE.inventory.findIndex(invItem => invItem.uniqueId === yourItem.uniqueId);
                if (itemIndex > -1) STATE.inventory.splice(itemIndex, 1);
                if (isSuccess) {
                    showNotification(`Апгрейд успішний! Ви отримали ${desiredItem.name}.`);
                    const newItem = { ...desiredItem, uniqueId: Date.now() };
                    STATE.inventory.push(newItem);
                    STATE.gameHistory.push({ ...newItem, date: new Date(), name: `Апгрейд до ${newItem.name}`, value: newItem.value });
                } else {
                    showNotification(`На жаль, апгрейд не вдався. Предмет втрачено.`);
                    STATE.gameHistory.push({ ...yourItem, date: new Date(), name: `Невдалий апгрейд ${yourItem.name}`, value: -yourItem.value });
                }
                resetUpgradeState(true);
                renderInventory();
                renderHistory();
            }, 1500);
        }, { once: true });
    }
    // --- КОНЕЦ ЛОГИКИ АПГРЕЙДА ---

    // --- ЛОГИКА ИГРЫ КРАШ ---
    function initCrashGame() {
        STATE.crashState = {
            isActive: false,
            bet: 100,
            autoCashout: 2.0,
            currentMultiplier: 1.0,
            hasPlacedBet: false,
            gameStartTime: 0,
            history: [...STATE.crashState.history] || []
        };
        
        updateCrashUI();
        renderCrashHistory();
        
        if (!STATE.crashState.isActive && !STATE.crashState.hasPlacedBet) {
            startCrashRound();
        }
    }

    function startCrashRound() {
        STATE.crashState.isActive = true;
        STATE.crashState.currentMultiplier = 1.0;
        STATE.crashState.gameStartTime = Date.now();
        
        const crashMultiplier = generateCrashMultiplier();
        updateCrashStatus('Игра началась!');
        
        const updateInterval = setInterval(() => {
            if (!STATE.crashState.isActive) {
                clearInterval(updateInterval);
                return;
            }
            
            const elapsed = (Date.now() - STATE.crashState.gameStartTime) / 1000;
            STATE.crashState.currentMultiplier = 1 + elapsed * 0.1;
            
            updateCrashMultiplier();
            
            // Проверяем автовывод
            if (STATE.crashState.hasPlacedBet && 
                STATE.crashState.currentMultiplier >= STATE.crashState.autoCashout) {
                cashoutCrash();
            }
            
            // Проверяем краш
            if (STATE.crashState.currentMultiplier >= crashMultiplier) {
                endCrashRound(crashMultiplier);
                clearInterval(updateInterval);
            }
        }, 100);
    }

    function generateCrashMultiplier() {
        // Используем экспоненциальное распределение для реалистичных результатов
        const random = Math.random();
        if (random < 0.5) return 1.0 + Math.random() * 1.0; // 1.0-2.0 (50%)
        if (random < 0.8) return 2.0 + Math.random() * 3.0; // 2.0-5.0 (30%)
        if (random < 0.95) return 5.0 + Math.random() * 10.0; // 5.0-15.0 (15%)
        return 15.0 + Math.random() * 85.0; // 15.0-100.0 (5%)
    }

    function placeCrashBet() {
        const bet = parseInt(document.getElementById('crash-bet-input')?.value || 100);
        const autoCashout = parseFloat(document.getElementById('crash-auto-cashout')?.value || 2.0);
        
        if (STATE.userBalance < bet) {
            showNotification('Недостаточно средств!');
            return;
        }
        
        if (STATE.crashState.hasPlacedBet) {
            showNotification('Ставка уже сделана!');
            return;
        }
        
        STATE.userBalance -= bet;
        STATE.crashState.bet = bet;
        STATE.crashState.autoCashout = autoCashout;
        STATE.crashState.hasPlacedBet = true;
        
        updateBalanceDisplay();
        updateCrashUI();
        showNotification(`Ставка ${bet} ⭐ принята!`);
    }

    function cashoutCrash() {
        if (!STATE.crashState.hasPlacedBet || !STATE.crashState.isActive) return;
        
        const winAmount = Math.floor(STATE.crashState.bet * STATE.crashState.currentMultiplier);
        STATE.userBalance += winAmount;
        STATE.crashState.hasPlacedBet = false;
        
        updateBalanceDisplay();
        updateCrashUI();
        showNotification(`Выигрыш: ${winAmount} ⭐ (x${STATE.crashState.currentMultiplier.toFixed(2)})`);
        
        STATE.gameStats.crash.total++;
        STATE.gameStats.crash.wins++;
        if (STATE.crashState.currentMultiplier > STATE.gameStats.crash.bestMultiplier) {
            STATE.gameStats.crash.bestMultiplier = STATE.crashState.currentMultiplier;
        }
        STATE.stats.totalGamesPlayed++;
        addExperience(10);
    }

    function endCrashRound(crashPoint) {
        STATE.crashState.isActive = false;
        STATE.crashState.history.unshift(crashPoint);
        if (STATE.crashState.history.length > 10) {
            STATE.crashState.history.pop();
        }
        
        updateCrashStatus(`Краш на x${crashPoint.toFixed(2)}!`);
        updateCrashMultiplier();
        renderCrashHistory();
        
        if (STATE.crashState.hasPlacedBet) {
            showNotification(`Краш! Ставка потеряна на x${crashPoint.toFixed(2)}`);
            STATE.crashState.hasPlacedBet = false;
            STATE.gameStats.crash.total++;
            STATE.stats.totalGamesPlayed++;
            addExperience(5);
        }
        
        updateCrashUI();
        
        // Начать новый раунд через 3 секунды
        setTimeout(() => {
            if (document.getElementById('crash-view')?.classList.contains('active')) {
                startCrashRound();
            }
        }, 3000);
    }

    function updateCrashMultiplier() {
        const element = document.getElementById('crash-multiplier');
        if (element) {
            element.textContent = `${STATE.crashState.currentMultiplier.toFixed(2)}x`;
            element.style.color = STATE.crashState.currentMultiplier > 2 ? '#22c55e' : '#6366f1';
        }
    }

    function updateCrashStatus(message) {
        const element = document.getElementById('crash-status');
        if (element) element.textContent = message;
    }

    function updateCrashUI() {
        const betBtn = document.getElementById('crash-bet-btn');
        const cashoutBtn = document.getElementById('crash-cashout-btn');
        
        if (betBtn) {
            betBtn.disabled = STATE.crashState.hasPlacedBet || !STATE.crashState.isActive;
            betBtn.textContent = STATE.crashState.hasPlacedBet ? 'Ставка сделана' : 'Сделать ставку';
        }
        
        if (cashoutBtn) {
            cashoutBtn.classList.toggle('hidden', !STATE.crashState.hasPlacedBet);
            if (STATE.crashState.hasPlacedBet) {
                const winAmount = Math.floor(STATE.crashState.bet * STATE.crashState.currentMultiplier);
                cashoutBtn.textContent = `Вывести ${winAmount} ⭐`;
            }
        }
    }

    function renderCrashHistory() {
        const container = document.getElementById('crash-history-list');
        if (!container) return;
        
        container.innerHTML = '';
        STATE.crashState.history.forEach(multiplier => {
            const item = document.createElement('div');
            item.className = 'crash-history-item';
            item.textContent = `${multiplier.toFixed(2)}x`;
            
            if (multiplier < 2) item.classList.add('low');
            else if (multiplier < 5) item.classList.add('medium');
            else if (multiplier < 10) item.classList.add('high');
            else item.classList.add('jackpot');
            
            container.appendChild(item);
        });
    }
    // --- КОНЕЦ ЛОГИКИ КРАШ ---

    // --- ЛОГИКА БЛЭКДЖЕКА ---
    function resetBlackjackGame() {
        STATE.blackjackState = {
            isActive: false,
            bet: 100,
            playerCards: [],
            dealerCards: [],
            playerScore: 0,
            dealerScore: 0,
            gamePhase: 'betting',
            canDouble: false,
            deck: []
        };
        updateBlackjackUI();
    }

    function createDeck() {
        const suits = ['♠', '♥', '♦', '♣'];
        const values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'];
        const deck = [];
        
        for (const suit of suits) {
            for (const value of values) {
                deck.push({ suit, value, numericValue: getCardValue(value) });
            }
        }
        
        // Перемешиваем колоду
        for (let i = deck.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [deck[i], deck[j]] = [deck[j], deck[i]];
        }
        
        return deck;
    }

    function getCardValue(value) {
        if (value === 'A') return 11;
        if (['K', 'Q', 'J'].includes(value)) return 10;
        return parseInt(value);
    }

    function calculateScore(cards) {
        let score = 0;
        let aces = 0;
        
        for (const card of cards) {
            if (card.value === 'A') {
                aces++;
                score += 11;
            } else {
                score += card.numericValue;
            }
        }
        
        // Обрабатываем тузы
        while (score > 21 && aces > 0) {
            score -= 10;
            aces--;
        }
        
        return score;
    }

    function startBlackjackGame() {
        const bet = parseInt(document.getElementById('blackjack-bet-input')?.value || 100);
        
        if (STATE.userBalance < bet) {
            showNotification('Недостаточно средств!');
            return;
        }
        
        STATE.userBalance -= bet;
        STATE.blackjackState.bet = bet;
        STATE.blackjackState.deck = createDeck();
        STATE.blackjackState.playerCards = [];
        STATE.blackjackState.dealerCards = [];
        STATE.blackjackState.gamePhase = 'playing';
        STATE.blackjackState.canDouble = true;
        
        // Раздаем карты
        dealCard('player');
        dealCard('dealer');
        dealCard('player');
        dealCard('dealer', true); // Вторая карта дилера скрыта
        
        updateBalanceDisplay();
        updateBlackjackUI();
        renderBlackjackCards();
        
        // Проверяем блэкджек
        if (STATE.blackjackState.playerScore === 21) {
            endBlackjackGame('blackjack');
        }
    }

    function dealCard(target, hidden = false) {
        const card = STATE.blackjackState.deck.pop();
        card.hidden = hidden;
        
        if (target === 'player') {
            STATE.blackjackState.playerCards.push(card);
            STATE.blackjackState.playerScore = calculateScore(STATE.blackjackState.playerCards);
        } else {
            STATE.blackjackState.dealerCards.push(card);
            // Считаем только видимые карты дилера
            const visibleCards = STATE.blackjackState.dealerCards.filter(c => !c.hidden);
            STATE.blackjackState.dealerScore = calculateScore(visibleCards);
        }
    }

    function hitBlackjack() {
        if (STATE.blackjackState.gamePhase !== 'playing') return;
        
        dealCard('player');
        STATE.blackjackState.canDouble = false;
        renderBlackjackCards();
        updateBlackjackUI();
        
        if (STATE.blackjackState.playerScore > 21) {
            endBlackjackGame('bust');
        }
    }

    function standBlackjack() {
        if (STATE.blackjackState.gamePhase !== 'playing') return;
        
        STATE.blackjackState.gamePhase = 'dealer';
        
        // Открываем скрытую карту дилера
        STATE.blackjackState.dealerCards.forEach(card => card.hidden = false);
        STATE.blackjackState.dealerScore = calculateScore(STATE.blackjackState.dealerCards);
        
        // Дилер добирает карты
        while (STATE.blackjackState.dealerScore < 17) {
            dealCard('dealer');
        }
        
        renderBlackjackCards();
        
        // Определяем результат
        if (STATE.blackjackState.dealerScore > 21) {
            endBlackjackGame('dealer-bust');
        } else if (STATE.blackjackState.dealerScore > STATE.blackjackState.playerScore) {
            endBlackjackGame('dealer-win');
        } else if (STATE.blackjackState.dealerScore < STATE.blackjackState.playerScore) {
            endBlackjackGame('player-win');
        } else {
            endBlackjackGame('push');
        }
    }

    function doubleBlackjack() {
        if (!STATE.blackjackState.canDouble || STATE.userBalance < STATE.blackjackState.bet) {
            showNotification('Нельзя удвоить ставку!');
            return;
        }
        
        STATE.userBalance -= STATE.blackjackState.bet;
        STATE.blackjackState.bet *= 2;
        updateBalanceDisplay();
        
        dealCard('player');
        renderBlackjackCards();
        
        if (STATE.blackjackState.playerScore > 21) {
            endBlackjackGame('bust');
        } else {
            standBlackjack();
        }
    }

    function endBlackjackGame(result) {
        STATE.blackjackState.gamePhase = 'finished';
        let message = '';
        let winAmount = 0;
        
        switch (result) {
            case 'blackjack':
                winAmount = Math.floor(STATE.blackjackState.bet * 2.5);
                message = 'Блэкджек! Поздравляем!';
                STATE.gameStats.blackjack.wins++;
                break;
            case 'player-win':
                winAmount = STATE.blackjackState.bet * 2;
                message = 'Вы выиграли!';
                STATE.gameStats.blackjack.wins++;
                break;
            case 'dealer-bust':
                winAmount = STATE.blackjackState.bet * 2;
                message = 'Дилер перебрал! Вы выиграли!';
                STATE.gameStats.blackjack.wins++;
                break;
            case 'push':
                winAmount = STATE.blackjackState.bet;
                message = 'Ничья!';
                break;
            case 'dealer-win':
                message = 'Дилер выиграл!';
                break;
            case 'bust':
                message = 'Перебор! Вы проиграли!';
                break;
        }
        
        if (winAmount > 0) {
            STATE.userBalance += winAmount;
            updateBalanceDisplay();
        }
        
        STATE.gameStats.blackjack.total++;
        STATE.stats.totalGamesPlayed++;
        addExperience(15);
        
        const resultElement = document.getElementById('blackjack-result');
        if (resultElement) {
            resultElement.textContent = message;
            resultElement.className = 'game-result';
            if (winAmount > STATE.blackjackState.bet) resultElement.classList.add('win');
            else if (winAmount === STATE.blackjackState.bet) resultElement.classList.add('draw');
            else resultElement.classList.add('lose');
        }
        
        updateBlackjackUI();
        showNotification(message);
    }

    function renderBlackjackCards() {
        renderCards('dealer-cards', STATE.blackjackState.dealerCards);
        renderCards('player-cards', STATE.blackjackState.playerCards);
        
        const dealerScoreElement = document.getElementById('dealer-score');
        const playerScoreElement = document.getElementById('player-score');
        
        if (dealerScoreElement) dealerScoreElement.textContent = STATE.blackjackState.dealerScore;
        if (playerScoreElement) playerScoreElement.textContent = STATE.blackjackState.playerScore;
    }

    function renderCards(containerId, cards) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = '';
        cards.forEach(card => {
            const cardElement = document.createElement('div');
            cardElement.className = `card ${card.hidden ? 'hidden' : (card.suit === '♥' || card.suit === '♦' ? 'red' : 'black')}`;
            cardElement.textContent = card.hidden ? '' : `${card.value}${card.suit}`;
            container.appendChild(cardElement);
        });
    }

    function updateBlackjackUI() {
        const dealBtn = document.getElementById('blackjack-deal-btn');
        const hitBtn = document.getElementById('blackjack-hit-btn');
        const standBtn = document.getElementById('blackjack-stand-btn');
        const doubleBtn = document.getElementById('blackjack-double-btn');
        
        const isPlaying = STATE.blackjackState.gamePhase === 'playing';
        const isBetting = STATE.blackjackState.gamePhase === 'betting';
        
        if (dealBtn) {
            dealBtn.classList.toggle('hidden', !isBetting);
        }
        if (hitBtn) {
            hitBtn.classList.toggle('hidden', !isPlaying);
        }
        if (standBtn) {
            standBtn.classList.toggle('hidden', !isPlaying);
        }
        if (doubleBtn) {
            doubleBtn.classList.toggle('hidden', !isPlaying || !STATE.blackjackState.canDouble);
        }
    }
    // --- КОНЕЦ ЛОГИКИ БЛЭКДЖЕКА ---

    // --- ЛОГИКА МИНЕРА ---
    function resetMinerGame() {
        STATE.minerState.isActive = false;
        STATE.minerState.openedCrystals = 0;
        STATE.minerState.totalWin = 0;
        renderMinerGrid();
        updateMinerUI();
        if (UI.minerBetInput) UI.minerBetInput.disabled = false;
        if (UI.minerStartBtn) UI.minerStartBtn.classList.remove('hidden');
        if (UI.minerCashoutBtn) UI.minerCashoutBtn.classList.add('hidden');
        if (UI.minerInfoWrapper) UI.minerInfoWrapper.classList.add('hidden');
    }

    function startMinerGame() {
        const bet = parseInt(UI.minerBetInput.value);
        if (isNaN(bet) || bet <= 0) {
            showNotification("Некорректная ставка");
            return;
        }
        if (STATE.userBalance < bet) {
            showNotification("Недостаточно средств");
            return;
        }

        STATE.userBalance -= bet;
        updateBalanceDisplay();

        STATE.minerState.isActive = true;
        STATE.minerState.bet = bet;
        STATE.minerState.openedCrystals = 0;
        STATE.minerState.totalWin = 0;
        
        const totalCells = 12;
        const bombIndices = new Set();
        while (bombIndices.size < STATE.minerState.bombs) {
            bombIndices.add(Math.floor(Math.random() * totalCells));
        }

        STATE.minerState.grid = Array.from({ length: totalCells }, (_, i) => ({
            isBomb: bombIndices.has(i),
            isOpened: false,
        }));

        renderMinerGrid(true);
        updateMinerUI();
        UI.minerBetInput.disabled = true;
        UI.minerStartBtn.classList.add('hidden');
        UI.minerCashoutBtn.classList.remove('hidden');
        UI.minerCashoutBtn.disabled = true;
        UI.minerInfoWrapper.classList.remove('hidden');
    }

    function renderMinerGrid(isGameActive = false) {
        if (!UI.minerGrid) return;
        UI.minerGrid.innerHTML = '';
        STATE.minerState.grid.forEach((cell, index) => {
            const cellEl = document.createElement('div');
            cellEl.classList.add('miner-cell');
            if (cell.isOpened) {
                cellEl.classList.add('opened');
                const img = document.createElement('img');
                img.src = cell.isBomb ? 'bomb.png' : 'diamond.png';
                cellEl.appendChild(img);
                if (cell.isBomb) cellEl.classList.add('bomb');
            }
            if (isGameActive && !cell.isOpened) {
                cellEl.addEventListener('click', () => handleMinerCellClick(index), { once: true });
            }
            UI.minerGrid.appendChild(cellEl);
        });
    }

    function handleMinerCellClick(index) {
        if (!STATE.minerState.isActive) return;

        const cell = STATE.minerState.grid[index];
        cell.isOpened = true;

        if (cell.isBomb) {
            endMinerGame(false);
        } else {
            STATE.minerState.openedCrystals++;
            updateMinerMultiplierAndWin();
            renderMinerGrid(true);
            updateMinerUI();
            UI.minerCashoutBtn.disabled = false;
            
            const totalCrystals = 12 - STATE.minerState.bombs;
            if (STATE.minerState.openedCrystals === totalCrystals) {
                endMinerGame(true);
            }
        }
    }

    function updateMinerMultiplierAndWin() {
        const { bet, openedCrystals } = STATE.minerState;
        if (openedCrystals === 0) {
            STATE.minerState.currentMultiplier = 1;
        } else {
            STATE.minerState.currentMultiplier = Math.pow(1.4, openedCrystals);
        }
        STATE.minerState.totalWin = bet * STATE.minerState.currentMultiplier;
    }
    
    function getNextWin() {
        const { bet, openedCrystals } = STATE.minerState;
        const nextMultiplier = Math.pow(1.4, openedCrystals + 1);
        return bet * nextMultiplier;
    }

    function updateMinerUI() {
        if (!UI.minerNextWin || !UI.minerTotalWin) return;

        if (STATE.minerState.isActive) {
            UI.minerNextWin.textContent = getNextWin().toFixed(2);
            if (STATE.minerState.openedCrystals > 0) {
                UI.minerTotalWin.textContent = STATE.minerState.totalWin.toFixed(2);
            } else {
                UI.minerTotalWin.textContent = '0';
            }
        } else {
            UI.minerTotalWin.textContent = '0';
            UI.minerNextWin.textContent = '0';
        }
    }

    function endMinerGame(isWin) {
        STATE.minerState.isActive = false;

        if (isWin) {
            showNotification(`Выигрыш ${STATE.minerState.totalWin.toFixed(2)} ⭐ зачислен!`);
            STATE.userBalance += STATE.minerState.totalWin;
            updateBalanceDisplay();
        } else {
            showNotification("Вы проиграли! Ставка сгорела.");
        }
        
        STATE.minerState.grid.forEach(cell => {
            if (cell.isBomb) cell.isOpened = true;
        });
        
        renderMinerGrid(false);
        setTimeout(resetMinerGame, 2000);
    }

    function cashoutMiner() {
        if (!STATE.minerState.isActive || STATE.minerState.openedCrystals === 0) return;
        endMinerGame(true);
    }
    // --- КОНЕЦ ЛОГИКИ МИНЕРА ---

    // --- ОБНОВЛЕННАЯ ЛОГИКА СЛОТОВ ---
    function handleSlotsSpin() {
        if (STATE.slotsState.isSpinning) return;

        const bet = parseInt(UI.slotsBetInput.value);
        if (isNaN(bet) || bet <= 0) {
            showNotification("Некорректная ставка");
            return;
        }
        if (STATE.userBalance < bet) {
            showNotification("Недостаточно средств");
            return;
        }

        STATE.slotsState.isSpinning = true;
        UI.slotsSpinBtn.disabled = true;
        STATE.userBalance -= bet;
        updateBalanceDisplay();
        UI.slotsPayline.classList.remove('visible');

        const results = [];
        const tracks = [UI.slotsTrack1, UI.slotsTrack2, UI.slotsTrack3];
        
        function spinReel(index) {
            if (index >= tracks.length) {
                processSlotsResult(results, bet);
                return;
            }
        
            const track = tracks[index];
            const symbols = STATE.slotsState.symbols;
            const reelLength = 30;
            const finalSymbol = symbols[Math.floor(Math.random() * symbols.length)];
            results.push(finalSymbol);

            let reelHtml = '';
            for (let i = 0; i < reelLength; i++) {
                const symbol = i === reelLength - 2 
                    ? finalSymbol 
                    : symbols[Math.floor(Math.random() * symbols.length)];
                reelHtml += `<div class="slots-item"><img src="${symbol.imageSrc}" alt="${symbol.name}"></div>`;
            }
            track.innerHTML = reelHtml;
            
            track.style.transition = 'none';
            track.style.top = '0px';
            track.offsetHeight;

            const itemHeight = 90; // 80px height + 10px margin
            const targetPosition = (reelLength - 2) * itemHeight;
            const spinDuration = 2 + index * 0.5;
            
            track.style.transition = `top ${spinDuration}s cubic-bezier(0.25, 1, 0.5, 1)`;
            track.style.top = `-${targetPosition}px`;
            
            track.addEventListener('transitionend', () => {
                setTimeout(() => spinReel(index + 1), 300); // Задержка между остановками
            }, { once: true });
        }

        spinReel(0);
    }

    function processSlotsResult(results, bet) {
        let win = 0;
        let message = "Попробуйте еще раз!";
        let multiplier = 0;

        const [r1, r2, r3] = results;

        // Обновляем статистику
        STATE.gameStats.slots.total++;
        STATE.stats.totalGamesPlayed++;

        // Проверяем комбинации
        if (r1.name === r2.name && r2.name === r3.name) {
            // Все три одинаковые
            multiplier = r1.multiplier;
            win = bet * multiplier;
            message = `ДЖЕКПОТ! ${r1.name} x${multiplier}!`;
            STATE.gameStats.slots.wins++;
            addExperience(25);
        } else if (r1.name === r2.name || r1.name === r3.name || r2.name === r3.name) {
            // Две одинаковые
            multiplier = 1.5;
            win = Math.floor(bet * multiplier);
            message = `Хорошо! Выигрыш x${multiplier}!`;
            STATE.gameStats.slots.wins++;
            addExperience(15);
        } else {
            addExperience(5);
        }
        
        if (win > 0) {
            STATE.userBalance += win;
            updateBalanceDisplay();
            UI.slotsPayline.classList.add('visible');
            showNotification(message + ` (+${win} ⭐)`);
        } else {
             showNotification(message);
        }

        STATE.slotsState.isSpinning = false;
        UI.slotsSpinBtn.disabled = false;
    }

    function handleSlotsMaxBet() {
        const maxBet = Math.min(STATE.userBalance, 1000);
        UI.slotsBetInput.value = maxBet;
    }
    // --- КОНЕЦ ЛОГИКИ СЛОТОВ ---

    // --- ОБНОВЛЕННАЯ ЛОГИКА ВЕЖИ (TOWER) ---
    function resetTowerGame() {
        STATE.towerState.isActive = false;
        STATE.towerState.currentLevel = 0;
        STATE.towerState.grid = [];
        STATE.towerState.payouts = [];

        UI.towerPreGameControls.classList.remove('hidden');
        UI.towerInGameControls.classList.add('hidden');
        if (UI.towerBetInput) UI.towerBetInput.disabled = false;

        renderTower();
        renderTowerPayouts();
    }

    function startTowerGame() {
        const bet = parseInt(UI.towerBetInput.value);
        if (isNaN(bet) || bet <= 0) {
            showNotification("Некорректная ставка");
            return;
        }
        if (STATE.userBalance < bet) {
            showNotification("Недостаточно средств");
            return;
        }

        STATE.userBalance -= bet;
        updateBalanceDisplay();

        STATE.towerState.isActive = true;
        STATE.towerState.bet = bet;
        STATE.towerState.currentLevel = 0;
        STATE.towerState.grid = Array.from({ length: 5 }, () => Math.floor(Math.random() * 2));

        const multipliers = [2, 4, 8, 16, 32];
        STATE.towerState.payouts = multipliers.map(m => bet * m);
        
        UI.towerPreGameControls.classList.add('hidden');
        UI.towerInGameControls.classList.remove('hidden');
        UI.towerBetInput.disabled = true;


        renderTower();
        renderTowerPayouts();
        updateTowerCashoutButton();
    }

    function renderTower() {
        UI.towerGrid.innerHTML = '';
        const pastRows = document.createDocumentFragment();
        
        for (let i = 0; i < 5; i++) {
            const rowEl = document.createElement('div');
            rowEl.classList.add('tower-row');

            if (STATE.towerState.isActive && i < STATE.towerState.currentLevel) {
                rowEl.classList.add('passed');
            }

            if (STATE.towerState.isActive && i === STATE.towerState.currentLevel) {
                rowEl.classList.add('active');
            }

            for (let j = 0; j < 2; j++) {
                const cellEl = document.createElement('div');
                cellEl.classList.add('tower-cell');
                
                if (STATE.towerState.isActive && i === STATE.towerState.currentLevel) {
                     cellEl.addEventListener('click', () => handleTowerCellClick(i, j));
                }

                if (STATE.towerState.isActive && i < STATE.towerState.currentLevel) {
                    const bombCol = STATE.towerState.grid[i];
                    if (j !== bombCol) {
                        cellEl.classList.add('safe');
                        cellEl.innerHTML = `<img src="diamond.png">`;
                    }
                }
               
                rowEl.appendChild(cellEl);
            }
            pastRows.appendChild(rowEl);
        }
        UI.towerGrid.appendChild(pastRows);
    }

    function renderTowerPayouts() {
        UI.towerPayouts.innerHTML = '';
        const payouts = STATE.towerState.payouts;
        for (let i = 0; i < 5; i++) {
            const payoutEl = document.createElement('div');
            payoutEl.classList.add('tower-payout-item');
            if (STATE.towerState.isActive && i === STATE.towerState.currentLevel) {
                payoutEl.classList.add('active');
            }
            payoutEl.textContent = `${(payouts[i] || 0).toFixed(0)} ⭐`;
            UI.towerPayouts.appendChild(payoutEl);
        }
    }

    function handleTowerCellClick(row, col) {
        if (!STATE.towerState.isActive || row !== STATE.towerState.currentLevel) return;

        STATE.towerState.isActive = false;

        const bombCol = STATE.towerState.grid[row];
        const safeCol = bombCol === 0 ? 1 : 0;
        const rows = UI.towerGrid.children;
        const clickedRow = rows[row];
        
        clickedRow.classList.remove('active');
        
        clickedRow.children[bombCol].classList.add('danger');
        clickedRow.children[bombCol].innerHTML = `<img src="bomb.png">`;
        clickedRow.children[safeCol].classList.add('safe');
        clickedRow.children[safeCol].innerHTML = `<img src="diamond.png">`;

        if (col === bombCol) {
            setTimeout(() => endTowerGame(false), 500);
        } else {
            STATE.towerState.currentLevel++;
            
            if (STATE.towerState.currentLevel === 5) {
                setTimeout(() => endTowerGame(true), 500);
            } else {
                setTimeout(() => {
                    STATE.towerState.isActive = true;
                    renderTower();
                    renderTowerPayouts();
                    updateTowerCashoutButton();
                }, 800);
            }
        }
    }

    function updateTowerCashoutButton() {
        const level = STATE.towerState.currentLevel;
        if (level > 0) {
            const amount = STATE.towerState.payouts[level - 1];
            UI.towerCashoutAmount.textContent = amount.toFixed(0);
            UI.towerCashoutBtn.disabled = false;
        } else {
             UI.towerCashoutAmount.textContent = '0';
             UI.towerCashoutBtn.disabled = true;
        }
    }
    
    function cashoutTower() {
        if (!STATE.towerState.isActive || STATE.towerState.currentLevel === 0) return;
        endTowerGame(true);
    }

    function endTowerGame(isWin) {
        if (STATE.towerState.isActive === false && !isWin) {
             // Already lost, do nothing
        } else {
            STATE.towerState.isActive = false;
        }
        
        let winAmount = 0;
        if (isWin) {
            const level = STATE.towerState.currentLevel;
            if (level > 0) {
                 winAmount = STATE.towerState.payouts[level - 1];
                 STATE.userBalance += winAmount;
                 updateBalanceDisplay();
                 showNotification(`Выигрыш ${winAmount.toFixed(0)} ⭐ зачислен!`);
            }
        } else {
            showNotification("Вы проиграли! Ставка сгорела.");
        }

        const rows = UI.towerGrid.children;
        for(let i = STATE.towerState.currentLevel; i < STATE.towerState.grid.length; i++) {
            if (rows[i]) {
                const bombCol = STATE.towerState.grid[i];
                const cell = rows[i].children[bombCol];
                if(cell) {
                   cell.classList.add('danger');
                   cell.innerHTML = `<img src="bomb.png">`;
                }
            }
        }

        setTimeout(resetTowerGame, 2000);
    }
    // --- КОНЕЦ ЛОГИКИ ВЕЖИ ---

    // --- ЛОГИКА ОРЛА И РЕШКИ ---
    function handleCoinflip(playerChoice) {
        if (STATE.coinflipState.isFlipping) return;

        const bet = parseInt(UI.coinflipBetInput.value);
        if (isNaN(bet) || bet <= 0) {
            showNotification("Некорректная ставка");
            return;
        }
        if (STATE.userBalance < bet) {
            showNotification("Недостаточно средств");
            return;
        }

        STATE.userBalance -= bet;
        updateBalanceDisplay();

        STATE.coinflipState.isFlipping = true;
        UI.coinflipResult.textContent = '';
        
        const result = Math.random() < 0.485 ? playerChoice : (playerChoice === 'heads' ? 'tails' : 'heads');

        const handleFlipEnd = () => {
            // Обновляем статистику
            STATE.gameStats.coinflip.total++;
            STATE.stats.totalGamesPlayed++;
            
            // Показать результат
            if (playerChoice === result) {
                const winAmount = Math.floor(bet * 1.9);
                STATE.userBalance += winAmount;
                STATE.gameStats.coinflip.wins++;
                UI.coinflipResult.textContent = `Вы выиграли ${winAmount} ⭐!`;
                showNotification(`Победа! +${winAmount} ⭐`);
                addExperience(10);
            } else {
                UI.coinflipResult.textContent = `Вы проиграли ${bet} ⭐.`;
                showNotification(`Проигрыш! -${bet} ⭐`);
                addExperience(5);
            }
            updateBalanceDisplay();
            updateCoinflipStats();
            STATE.coinflipState.isFlipping = false;

            // Мгновенно сбросить transform для следующей анимации без видимого перехода
            UI.coin.style.transition = 'none';
            if (result === 'tails') {
                UI.coin.style.transform = 'rotateY(180deg)';
            } else {
                UI.coin.style.transform = 'rotateY(0deg)';
            }
        };

    function updateCoinflipStats() {
        const totalElement = document.getElementById('coinflip-total-games');
        const winsElement = document.getElementById('coinflip-wins');
        const winRateElement = document.getElementById('coinflip-win-rate');
        
        if (totalElement) totalElement.textContent = STATE.gameStats.coinflip.total;
        if (winsElement) winsElement.textContent = STATE.gameStats.coinflip.wins;
        if (winRateElement) {
            const winRate = STATE.gameStats.coinflip.total > 0 
                ? ((STATE.gameStats.coinflip.wins / STATE.gameStats.coinflip.total) * 100).toFixed(1)
                : '0';
            winRateElement.textContent = `${winRate}%`;
        }
    }

        UI.coin.addEventListener('transitionend', handleFlipEnd, { once: true });

        // Восстановить transition для анимации вращения
        UI.coin.style.transition = 'transform 1s cubic-bezier(0.5, 1.3, 0.5, 1.3)';
        
        // Начать анимацию
        if (result === 'heads') {
             // 5 полных оборотов, заканчивается на той же стороне
             UI.coin.style.transform = 'rotateY(1800deg)';
        } else {
             // 5.5 оборотов, заканчивается на противоположной стороне
             UI.coin.style.transform = 'rotateY(1980deg)';
        }
    }
    // --- КОНЕЦ ЛОГИКИ ОРЛА И РЕШКИ ---

    // --- ЛОГИКА КАМЕНЬ-НОЖНИЦЫ-БУМАГА ---
    function handleRps(playerChoice) {
        if (STATE.rpsState.isPlaying) return;
        
        const bet = parseInt(UI.rpsBetInput.value);
        if (isNaN(bet) || bet <= 0) {
            showNotification("Некорректная ставка");
            return;
        }
        if (STATE.userBalance < bet) {
            showNotification("Недостаточно средств");
            return;
        }

        STATE.userBalance -= bet;
        updateBalanceDisplay();

        STATE.rpsState.isPlaying = true;
        UI.rpsButtons.forEach(button => button.disabled = true);

        const choices = ['rock', 'paper', 'scissors'];
        const computerChoice = choices[Math.floor(Math.random() * choices.length)];

        const choiceMap = {
            rock: '🗿',
            paper: '📄',
            scissors: '✂️'
        };

        UI.rpsPlayerChoice.textContent = choiceMap[playerChoice];
        UI.rpsComputerChoice.classList.add('spinning');
        
        let spinInterval = setInterval(() => {
            const randomChoice = choices[Math.floor(Math.random() * choices.length)];
            UI.rpsComputerChoice.textContent = choiceMap[randomChoice];
        }, 100);

        setTimeout(() => {
            clearInterval(spinInterval);
            UI.rpsComputerChoice.classList.remove('spinning');
            UI.rpsComputerChoice.textContent = choiceMap[computerChoice];
            
            // Обновляем статистику
            STATE.gameStats.rps.total++;
            STATE.stats.totalGamesPlayed++;
            
            let resultMessage = '';
            if (playerChoice === computerChoice) {
                resultMessage = "Ничья!";
                STATE.userBalance += bet; // Возвращаем ставку
                STATE.gameStats.rps.draws++;
                showNotification(`Ничья! Ставка возвращена`);
                addExperience(5);
            } else if (
                (playerChoice === 'rock' && computerChoice === 'scissors') ||
                (playerChoice === 'paper' && computerChoice === 'rock') ||
                (playerChoice === 'scissors' && computerChoice === 'paper')
            ) {
                const winAmount = Math.floor(bet * 1.8);
                resultMessage = `Вы выиграли ${winAmount} ⭐!`;
                STATE.userBalance += winAmount;
                STATE.gameStats.rps.wins++;
                showNotification(`Победа! +${winAmount} ⭐`);
                addExperience(15);
            } else {
                resultMessage = `Вы проиграли ${bet} ⭐.`;
                showNotification(`Проигрыш! -${bet} ⭐`);
                addExperience(5);
            }
            
            updateBalanceDisplay();
            updateRpsStats();
            UI.rpsResultMessage.textContent = resultMessage;
            updateBalanceDisplay();

            setTimeout(() => {
                STATE.rpsState.isPlaying = false;
                UI.rpsResultMessage.textContent = '';
                UI.rpsPlayerChoice.textContent = '?';
                UI.rpsComputerChoice.textContent = '?';
                UI.rpsButtons.forEach(button => button.disabled = false); // Re-enable buttons
            }, 2000);
        }, 4500); // Spin for 2 seconds
    }

    function updateRpsStats() {
        const totalElement = document.getElementById('rps-total-games');
        const winsElement = document.getElementById('rps-wins');
        const drawsElement = document.getElementById('rps-draws');
        
        if (totalElement) totalElement.textContent = STATE.gameStats.rps.total;
        if (winsElement) winsElement.textContent = STATE.gameStats.rps.wins;
        if (drawsElement) drawsElement.textContent = STATE.gameStats.rps.draws;
    }
    // --- КОНЕЦ ЛОГИКИ КАМЕНЬ-НОЖНИЦЫ-БУМАГА ---


    // --- ИНИЦИАЛИЗАЦИЯ ---
    try {
        // Поиск элементов
        UI.notificationToast = document.getElementById('notification-toast');
        UI.userBalanceElement = document.getElementById('user-balance');
        UI.views = document.querySelectorAll('.view');
        UI.navButtons = document.querySelectorAll('.nav-btn');
        UI.caseView = document.getElementById('case-view');
        UI.spinView = document.getElementById('spin-view');
        UI.rouletteTrack = document.getElementById('roulette');
        UI.spinnerContainer = document.getElementById('spinner-container');
        UI.multiSpinnerContainer = document.getElementById('multi-spinner-container');
        UI.caseImageBtn = document.getElementById('case-image-btn');
        UI.modalOverlay = document.getElementById('modal-overlay');
        UI.preOpenModal = document.getElementById('pre-open-modal');
        UI.priceCheckMessage = document.getElementById('price-check-message');
        UI.quantitySelector = document.getElementById('quantity-selector');
        UI.caseContentsPreview = document.getElementById('case-contents-preview');
        UI.startSpinBtn = document.getElementById('start-spin-btn');
        UI.resultModal = document.getElementById('result-modal');
        UI.inventoryContent = document.getElementById('inventory-content');
        UI.historyContent = document.getElementById('history-content');
        UI.profileTabs = document.querySelectorAll('.profile-tabs:not(.upgrade-picker-container) .profile-tab-btn');
        UI.profileContents = document.querySelectorAll('.profile-tab-content');
        UI.profilePhoto = document.getElementById('profile-photo');
        UI.profileName = document.getElementById('profile-name');
        UI.profileId = document.getElementById('profile-id');
        UI.inviteFriendBtn = document.getElementById('invite-friend-btn');
        UI.copyLinkBtn = document.getElementById('copy-link-btn');

        // Элементы для Конкурсов
        UI.contestTimer = document.getElementById('contest-timer');
        UI.buyTicketBtn = document.getElementById('buy-ticket-btn');
        UI.ticketQuantityInput = document.getElementById('ticket-quantity-input');
        UI.ticketQuantityPlus = document.getElementById('ticket-quantity-plus');
        UI.ticketQuantityMinus = document.getElementById('ticket-quantity-minus');
        UI.userTicketsDisplay = document.getElementById('user-tickets-display');

        // Элементы для Апгрейда
        UI.upgradeWheel = document.getElementById('upgrade-wheel');
        UI.upgradePointer = document.getElementById('upgrade-pointer');
        UI.upgradeChanceDisplay = document.getElementById('upgrade-chance-display');
        UI.upgradeMultiplierDisplay = document.getElementById('upgrade-multiplier-display');
        UI.yourItemSlot = document.getElementById('your-item-slot');
        UI.desiredItemSlot = document.getElementById('desired-item-slot');
        UI.performUpgradeBtn = document.getElementById('perform-upgrade-btn');
        UI.pickerTabs = document.querySelectorAll('.upgrade-picker-container .profile-tab-btn');
        UI.itemPickerContent = document.getElementById('item-picker-content');

        // Элементы меню игр
        UI.gameMenuBtns = document.querySelectorAll('.game-menu-btn');

        // Элементы для Минера
        UI.minerGrid = document.getElementById('miner-grid');
        UI.minerStartBtn = document.getElementById('miner-start-btn');
        UI.minerCashoutBtn = document.getElementById('miner-cashout-btn');
        UI.minerBetInput = document.getElementById('miner-bet-input');
        UI.minerNextWin = document.getElementById('miner-next-win');
        UI.minerTotalWin = document.getElementById('miner-total-win');
        UI.minerInfoWrapper = document.querySelector('.miner-info-wrapper');
        
        // Элементы для Орел и Решка
        UI.coin = document.getElementById('coin');
        UI.coinflipResult = document.getElementById('coinflip-result-message');
        UI.coinflipBetInput = document.getElementById('coinflip-bet-input');
        UI.coinflipHeadsBtn = document.getElementById('coinflip-heads-btn');
        UI.coinflipTailsBtn = document.getElementById('coinflip-tails-btn');
        
        // Элементы для Камень-Ножницы-Бумага
        UI.rpsPlayerChoice = document.getElementById('rps-player-choice');
        UI.rpsComputerChoice = document.getElementById('rps-computer-choice');
        UI.rpsResultMessage = document.getElementById('rps-result-message');
        UI.rpsBetInput = document.getElementById('rps-bet-input');
        UI.rpsButtons = document.querySelectorAll('.rps-buttons .primary-button');

        // Элементы для Слотов
        UI.slotsTrack1 = document.getElementById('slots-track-1');
        UI.slotsTrack2 = document.getElementById('slots-track-2');
        UI.slotsTrack3 = document.getElementById('slots-track-3');
        UI.slotsSpinBtn = document.getElementById('slots-spin-btn');
        UI.slotsBetInput = document.getElementById('slots-bet-input');
        UI.slotsPayline = document.querySelector('.slots-payline');

        // Элементы для Вежи
        UI.towerGrid = document.getElementById('tower-grid');
        UI.towerPayouts = document.getElementById('tower-payouts');
        UI.towerBetInput = document.getElementById('tower-bet-input');
        UI.towerStartBtn = document.getElementById('tower-start-btn');
        UI.towerCashoutBtn = document.getElementById('tower-cashout-btn');
        UI.towerCashoutAmount = document.getElementById('tower-cashout-amount');
        UI.towerPreGameControls = document.getElementById('tower-pre-game-controls');
        UI.towerInGameControls = document.getElementById('tower-in-game-controls');

        if (!UI.caseImageBtn) throw new Error('Не вдалося знайти картинку кейса з id="case-image-btn"');

        // Обработчики событий
        if(UI.caseImageBtn) UI.caseImageBtn.addEventListener('click', handleCaseClick);
        if(UI.startSpinBtn) UI.startSpinBtn.addEventListener('click', startSpinProcess);
        if (UI.quantitySelector) UI.quantitySelector.addEventListener('click', handleQuantityChange);
        UI.navButtons.forEach(btn => btn.addEventListener('click', () => switchView(btn.dataset.view)));
        if (UI.inviteFriendBtn) UI.inviteFriendBtn.addEventListener('click', inviteFriend);
        if (UI.copyLinkBtn) UI.copyLinkBtn.addEventListener('click', copyInviteLink);
        
        // Обработчики для Конкурсов
        if (UI.buyTicketBtn) UI.buyTicketBtn.addEventListener('click', buyTickets);
        if (UI.ticketQuantityPlus) UI.ticketQuantityPlus.addEventListener('click', () => handleTicketQuantityChange(1));
        if (UI.ticketQuantityMinus) UI.ticketQuantityMinus.addEventListener('click', () => handleTicketQuantityChange(-1));
        
        if(UI.profileTabs) UI.profileTabs.forEach(tab => tab.addEventListener('click', function() {
            UI.profileTabs.forEach(t => t.classList.remove('active'));
            UI.profileContents.forEach(c => c.classList.remove('active'));
            this.classList.add('active');
            const contentId = this.dataset.tab + '-content';
            const contentEl = document.getElementById(contentId);
            if(contentEl) contentEl.classList.add('active');
        }));
        
        if(UI.modalOverlay) UI.modalOverlay.addEventListener('click', () => {
            document.querySelectorAll('.modal.visible').forEach(modal => hideModal(modal));
        });
        const preOpenModalCloseBtn = document.querySelector('[data-close-modal="pre-open-modal"]');
        if (preOpenModalCloseBtn) preOpenModalCloseBtn.addEventListener('click', () => hideModal(UI.preOpenModal));

        // --- ОБРАБОТЧИКИ ДЛЯ АПГРЕЙДА ---
        if (UI.pickerTabs) UI.pickerTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                if (STATE.upgradeState.isUpgrading) return;
                UI.pickerTabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                STATE.upgradeState.activePicker = tab.dataset.picker;
                if(UI.yourItemSlot) UI.yourItemSlot.classList.toggle('active-selection', STATE.upgradeState.activePicker === 'inventory');
                if(UI.desiredItemSlot) UI.desiredItemSlot.classList.toggle('active-selection', STATE.upgradeState.activePicker === 'desired');
                renderItemPicker();
            });
        });

        if (UI.yourItemSlot) UI.yourItemSlot.addEventListener('click', () => {
            if (!STATE.upgradeState.isUpgrading && document.getElementById('picker-tab-inventory')) document.getElementById('picker-tab-inventory').click();
        });
        if (UI.desiredItemSlot) UI.desiredItemSlot.addEventListener('click', () => {
             if (!STATE.upgradeState.isUpgrading && document.getElementById('picker-tab-desired')) document.getElementById('picker-tab-desired').click();
        });
        if (UI.performUpgradeBtn) UI.performUpgradeBtn.addEventListener('click', handleUpgradeClick);

        // --- ОБРАБОТЧИКИ ДЛЯ МЕНЮ ИГР ---
        if(UI.gameMenuBtns) {
            UI.gameMenuBtns.forEach(btn => {
                const view = btn.dataset.view, game = btn.dataset.game;
                if (view) btn.addEventListener('click', () => switchView(view));
                else if (game) btn.addEventListener('click', () => showNotification('Игра скоро будет доступна!'));
            });
        }

        // --- ОБРАБОТЧИКИ ДЛЯ МИНЕРА ---
        if(UI.minerStartBtn) UI.minerStartBtn.addEventListener('click', startMinerGame);
        if(UI.minerCashoutBtn) UI.minerCashoutBtn.addEventListener('click', cashoutMiner);

        // --- ОБРАБОТЧИКИ ДЛЯ СЛОТОВ ---
        if (UI.slotsSpinBtn) UI.slotsSpinBtn.addEventListener('click', handleSlotsSpin);
        const slotsMaxBetBtn = document.getElementById('slots-max-bet-btn');
        if (slotsMaxBetBtn) slotsMaxBetBtn.addEventListener('click', handleSlotsMaxBet);

        // --- ОБРАБОТЧИКИ ДЛЯ ВЕЖИ ---
        if (UI.towerStartBtn) UI.towerStartBtn.addEventListener('click', startTowerGame);
        if (UI.towerCashoutBtn) UI.towerCashoutBtn.addEventListener('click', cashoutTower);

        // --- ОБРАБОТЧИКИ ДЛЯ ОРЛА И РЕШКИ ---
        if (UI.coinflipHeadsBtn) UI.coinflipHeadsBtn.addEventListener('click', () => handleCoinflip('heads'));
        if (UI.coinflipTailsBtn) UI.coinflipTailsBtn.addEventListener('click', () => handleCoinflip('tails'));

        // --- ОБРАБОТЧИКИ ДЛЯ КАМЕНЬ-НОЖНИЦЫ-БУМАГА ---
        if (UI.rpsButtons) UI.rpsButtons.forEach(button => {
            button.addEventListener('click', () => handleRps(button.dataset.choice));
        });

        // --- ОБРАБОТЧИКИ ДЛЯ КРАШ ---
        const crashBetBtn = document.getElementById('crash-bet-btn');
        const crashCashoutBtn = document.getElementById('crash-cashout-btn');
        if (crashBetBtn) crashBetBtn.addEventListener('click', placeCrashBet);
        if (crashCashoutBtn) crashCashoutBtn.addEventListener('click', cashoutCrash);

        // --- ОБРАБОТЧИКИ ДЛЯ БЛЭКДЖЕКА ---
        const blackjackDealBtn = document.getElementById('blackjack-deal-btn');
        const blackjackHitBtn = document.getElementById('blackjack-hit-btn');
        const blackjackStandBtn = document.getElementById('blackjack-stand-btn');
        const blackjackDoubleBtn = document.getElementById('blackjack-double-btn');
        
        if (blackjackDealBtn) blackjackDealBtn.addEventListener('click', startBlackjackGame);
        if (blackjackHitBtn) blackjackHitBtn.addEventListener('click', hitBlackjack);
        if (blackjackStandBtn) blackjackStandBtn.addEventListener('click', standBlackjack);
        if (blackjackDoubleBtn) blackjackDoubleBtn.addEventListener('click', doubleBlackjack);

        // Инициализация элементов UI
        UI.userBalanceElement = document.getElementById('user-balance');
        UI.userGemsElement = document.getElementById('user-gems');
        UI.userLevelElement = document.getElementById('user-level');
        UI.caseTitleElement = document.getElementById('case-title');
        UI.casePriceElement = document.getElementById('case-price');
        UI.spinCaseTitleElement = document.getElementById('spin-case-title');
        UI.achievementToast = document.getElementById('achievement-toast');
        UI.totalOpenedElement = document.getElementById('total-opened');
        UI.totalWonElement = document.getElementById('total-won');
        UI.biggestWinElement = document.getElementById('biggest-win');
        UI.profileLevelElement = document.getElementById('profile-level');
        UI.profileExpElement = document.getElementById('profile-exp');
        UI.profileExpMaxElement = document.getElementById('profile-exp-max');
        UI.profileExpBar = document.getElementById('profile-exp-bar');

        // Обработчики для переключения типов кейсов
        document.querySelectorAll('.case-type-btn').forEach(btn => {
            btn.addEventListener('click', () => switchCaseType(btn.dataset.case));
        });

        // === ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ ===
        
        // Функции для магазина
        function initShop() {
            const shopItems = {
                boosters: [
                    { id: 1, name: 'Удачливый час', price: 500, currency: 'stars', description: 'Увеличивает шанс редких предметов на 1 час' },
                    { id: 2, name: 'Двойной XP', price: 300, currency: 'stars', description: 'Удваивает получаемый опыт на 30 минут' },
                    { id: 3, name: 'Магнит монет', price: 10, currency: 'gems', description: 'Увеличивает выигрыши на 25% на 1 час' }
                ],
                cosmetics: [
                    { id: 4, name: 'Золотая рамка', price: 1000, currency: 'stars', description: 'Украшает ваш профиль' },
                    { id: 5, name: 'Премиум аватар', price: 50, currency: 'gems', description: 'Эксклюзивная рамка аватара' }
                ],
                premium: [
                    { id: 6, name: 'VIP статус (7 дней)', price: 100, currency: 'gems', description: 'Все бонусы + эксклюзивные кейсы' },
                    { id: 7, name: 'Премиум пропуск', price: 2000, currency: 'stars', description: 'Дополнительные ежедневные награды' }
                ]
            };
            
            renderShopTab('boosters', shopItems.boosters);
        }
        
        function renderShopTab(tabName, items) {
            const content = document.getElementById('shop-content');
            if (!content) return;
            
            content.innerHTML = '';
            items.forEach(item => {
                const itemEl = document.createElement('div');
                itemEl.className = 'shop-item';
                itemEl.innerHTML = `
                    <img src="diamond.png" alt="${item.name}">
                    <div class="shop-item-name">${item.name}</div>
                    <div class="shop-item-description">${item.description}</div>
                    <div class="shop-item-price">${item.currency === 'gems' ? '💎' : '⭐'} ${item.price}</div>
                    <button class="primary-button" onclick="buyShopItem(${item.id}, ${item.price}, '${item.currency}')">Купить</button>
                `;
                content.appendChild(itemEl);
            });
        }
        
        window.buyShopItem = function(itemId, price, currency) {
            const canAfford = currency === 'gems' ? STATE.userGems >= price : STATE.userBalance >= price;
            
            if (!canAfford) {
                showNotification(`Недостаточно ${currency === 'gems' ? 'гемов' : 'звезд'}!`);
                return;
            }
            
            if (currency === 'gems') {
                STATE.userGems -= price;
            } else {
                STATE.userBalance -= price;
            }
            
            updateBalanceDisplay();
            showNotification('Покупка совершена!');
        };
        
        // Функции для достижений
        function renderAchievements() {
            const container = document.getElementById('achievements-list');
            if (!container) return;
            
            container.innerHTML = '';
            STATE.achievements.forEach(achievement => {
                const achEl = document.createElement('div');
                achEl.className = `achievement ${achievement.completed ? 'completed' : ''}`;
                achEl.innerHTML = `
                    <div class="achievement-icon">${achievement.completed ? '🏆' : '🔒'}</div>
                    <div class="achievement-info">
                        <div class="achievement-name">${achievement.name}</div>
                        <div class="achievement-description">${achievement.description}</div>
                        <div class="achievement-reward">Награда: ${achievement.reward} ⭐</div>
                    </div>
                `;
                container.appendChild(achEl);
            });
        }
        
        // Функции для ежедневных заданий
        function renderDailyTasks() {
            const container = document.getElementById('daily-tasks-list');
            if (!container) return;
            
            container.innerHTML = '';
            STATE.dailyTasks.forEach(task => {
                const taskEl = document.createElement('div');
                taskEl.className = `daily-task ${task.completed ? 'completed' : ''}`;
                taskEl.innerHTML = `
                    <div class="task-info">
                        <div class="task-name">${task.name}</div>
                        <div class="task-progress">${task.progress}/${task.target}</div>
                        <div class="task-reward">Награда: ${task.reward} ⭐</div>
                    </div>
                    <div class="task-progress-bar">
                        <div class="task-progress-fill" style="width: ${(task.progress / task.target * 100)}%"></div>
                    </div>
                    ${task.completed ? '<button class="secondary-button" disabled>Выполнено</button>' : 
                        task.progress >= task.target ? '<button class="primary-button" onclick="claimTask(' + task.id + ')">Забрать</button>' : 
                        '<button class="secondary-button" disabled>В процессе</button>'}
                `;
                container.appendChild(taskEl);
            });
        }
        
        window.claimTask = function(taskId) {
            const task = STATE.dailyTasks.find(t => t.id === taskId);
            if (!task || task.completed || task.progress < task.target) return;
            
            task.completed = true;
            STATE.userBalance += task.reward;
            updateBalanceDisplay();
            showNotification(`Задание выполнено! +${task.reward} ⭐`);
            renderDailyTasks();
        };
        
        // Обработчики для табов магазина
        document.querySelectorAll('.shop-tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.shop-tab-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                const tab = btn.dataset.tab;
                // Здесь можно добавить логику переключения контента магазина
            });
        });

        // Начальное состояние
        loadTelegramData();
        updateBalanceDisplay();
        updateCaseInfo();
        updateProfileStats();
        switchView('game-view');
        populateCasePreview();
        initShop();
        renderAchievements();
        renderDailyTasks();
        updateCoinflipStats();
        updateRpsStats();
        setInterval(updateTimer, 1000);
        
    } catch (error) {
        console.error("Помилка під час ініціалізації:", error);
        alert("Сталася критична помилка. Будь ласка, перевірте консоль (F12). Повідомлення: " + error.message);
    }
});