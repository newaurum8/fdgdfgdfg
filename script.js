document.addEventListener('DOMContentLoaded', function() {
    // --- ГЛОБАЛЬНИЙ СТАН ---
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
            targetItem: null,
            chance: 0,
            isUpgrading: false,
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
    function handleCoinflip(playerChoice) {
        if (STATE.coinflipState.isFlipping) return;

        const bet = parseInt(UI.coinflipBetInput.value);
        if (isNaN(bet) || bet <= 0 || bet > STATE.userBalance) {
            showNotification('Неверная ставка!');
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
            if (result === 'heads') {
                UI.coin.style.transform = 'rotateY(0deg)';
            } else {
                UI.coin.style.transform = 'rotateY(180deg)';
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
    }

    function handleRps(playerChoice) {
        if (STATE.rpsState.isPlaying) return;

        const bet = parseInt(UI.rpsBetInput.value);
        if (isNaN(bet) || bet <= 0 || bet > STATE.userBalance) {
            showNotification('Неверная ставка!');
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

        const spinInterval = setInterval(() => {
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

            // Reset after a delay
            setTimeout(() => {
                UI.rpsResultMessage.textContent = 'Сделайте выбор';
                UI.rpsPlayerChoice.textContent = '🤔';
                UI.rpsComputerChoice.textContent = '🤔';
                STATE.rpsState.isPlaying = false;
                UI.rpsButtons.forEach(button => button.disabled = false);
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
    // --- ОБРАБОТЧИКИ ДЛЯ СЛОТОВ ---
    if (UI.slotsSpinBtn) UI.slotsSpinBtn.addEventListener('click', handleSlotsSpin);
    const slotsMaxBetBtn = document.getElementById('slots-max-bet-btn');
    if (slotsMaxBetBtn) slotsMaxBetBtn.addEventListener('click', handleSlotsMaxBet);

    // --- ОБРАБОТЧИКИ ДЛЯ ВЕЖИ ---
    if (UI.towerStartBtn) UI.towerStartBtn.addEventListener('click', startTowerGame);

    UI.rpsButtons.forEach(button => {
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
});