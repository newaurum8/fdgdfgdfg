document.addEventListener('DOMContentLoaded', function() {
    // --- ГЛОБАЛЬНИЙ СТАН ---
    const STATE = {
        userBalance: 1250,
        inventory: [],
        gameHistory: [],
        isSpinning: false,
        openQuantity: 1,
        casePrice: 100,
        lastWonItems: [],
        contestTicketPrice: 100,
        ticketQuantity: 1,
        userTickets: 0,
        contestEndDate: new Date(Date.now() + 6 * 24 * 60 * 60 * 1000 + 15 * 60 * 60 * 1000),
        possibleItems: [
            { id: 1, name: 'Cigar', imageSrc: 'item.png', value: 3170 },
            { id: 2, name: 'Bear', imageSrc: 'item1.png', value: 440 },
            { id: 3, name: 'Sigmaboy', imageSrc: 'case.png', value: 50 },
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
                { name: 'Lemon', imageSrc: 'slot_lemon.png' },
                { name: 'Cherry', imageSrc: 'slot_cherry.png' },
                { name: 'Seven', imageSrc: 'slot_7.png' },
            ]
        },
        towerState: {
            isActive: false,
            bet: 100,
            currentLevel: 0,
            grid: [], // 0 for left bomb, 1 for right bomb
            payouts: []
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
        const totalCost = STATE.casePrice * STATE.openQuantity;
        if (STATE.userBalance >= totalCost) {
            UI.priceCheckMessage.innerHTML = `⭐ ${totalCost.toLocaleString('uk-UA')}`;
            UI.priceCheckMessage.classList.remove('error');
        } else {
            UI.priceCheckMessage.innerHTML = `⭐ ${totalCost.toLocaleString('uk-UA')} (не вистачає ${(totalCost - STATE.userBalance).toLocaleString('uk-UA')})`;
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
        const totalCost = STATE.casePrice * STATE.openQuantity;
        if (STATE.userBalance < totalCost) return;

        STATE.isSpinning = true;
        STATE.userBalance -= totalCost;
        updateBalanceDisplay();
        hideModal(UI.preOpenModal);
        
        const wonItems = [];
        for (let i = 0; i < STATE.openQuantity; i++) {
            const winnerData = { ...STATE.possibleItems[Math.floor(Math.random() * STATE.possibleItems.length)], uniqueId: Date.now() + i };
            wonItems.push(winnerData);
        }
        
        STATE.lastWonItems = wonItems;
        STATE.inventory.push(...wonItems);
        STATE.gameHistory.push(...wonItems.map(item => ({ ...item, date: new Date() })));

        UI.caseView.classList.add('hidden');
        UI.spinView.classList.remove('hidden');
        
        if (STATE.openQuantity > 1) {
            startMultiVerticalAnimation();
        } else {
            startHorizontalAnimation();
        }
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
        [...STATE.possibleItems].sort((a, b) => b.value - a.value).forEach(item => {
            const itemEl = document.createElement('div');
            itemEl.classList.add('preview-item');
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
            if (UI.upgradeWheel) {
                UI.upgradeWheel.style.transition = 'none';
                UI.upgradeWheel.style.transform = `rotate(0deg)`;
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
        const chanceAngle = (chance / 100) * 360, randomOffset = Math.random() * 0.9 + 0.05;
        const stopPoint = isSuccess ? chanceAngle * randomOffset : chanceAngle + (360 - chanceAngle) * randomOffset;
        const rotation = (5 * 360) + (360 - stopPoint);
        STATE.upgradeState.currentRotation += rotation;
        UI.upgradeWheel.style.transition = 'transform 3s cubic-bezier(0.2, 0.8, 0.2, 1)';
        setTimeout(() => UI.upgradeWheel.style.transform = `rotate(${STATE.upgradeState.currentRotation}deg)`, 10);
        UI.upgradeWheel.addEventListener('transitionend', () => {
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
                resetUpgradeState(false);
                renderInventory();
                renderHistory();
            }, 1500);
        }, { once: true });
    }
    // --- КОНЕЦ ЛОГИКИ АПГРЕЙДА ---

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
        if (!UI.minerGrid) return;

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
        let completedReels = 0;

        tracks.forEach((track, index) => {
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
            const spinDuration = 4 + index * 0.5; // Each reel spins a bit longer
            
            track.style.transition = `top ${spinDuration}s cubic-bezier(0.25, 1, 0.5, 1)`;
            track.style.top = `-${targetPosition}px`;
            
            track.addEventListener('transitionend', () => {
                completedReels++;
                if (completedReels === tracks.length) {
                    processSlotsResult(results, bet);
                }
            }, { once: true });
        });
    }

    function processSlotsResult(results, bet) {
        let win = 0;
        let message = "Попробуйте еще раз!";

        const [r1, r2, r3] = results;

        if (r1.name === r2.name && r2.name === r3.name) {
            win = bet * 2;
            message = `Победа! Выигрыш x2!`;
        } else if (r1.name === r2.name || r1.name === r3.name || r2.name === r3.name) {
            win = bet * 1.5;
            message = `Неплохо! Выигрыш x1.5!`;
        }
        
        if (win > 0) {
            STATE.userBalance += win;
            updateBalanceDisplay();
            UI.slotsPayline.classList.add('visible');
            showNotification(message + ` (+${win.toFixed(0)} ⭐)`);
        } else {
             showNotification(message);
        }

        STATE.slotsState.isSpinning = false;
        UI.slotsSpinBtn.disabled = false;
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

        STATE.coinflipState.isFlipping = true;
        UI.coinflipResult.textContent = '';
        UI.coin.classList.add('flipping');
        
        const result = Math.random() < 0.5 ? 'heads' : 'tails';
        
        setTimeout(() => {
            if (result === 'heads') {
                 UI.coin.style.transform = 'rotateY(1800deg)';
            } else {
                 UI.coin.style.transform = 'rotateY(1980deg)';
            }
        
            setTimeout(() => {
                if (playerChoice === result) {
                    STATE.userBalance += bet;
                    UI.coinflipResult.textContent = `Вы выиграли ${bet} ⭐!`;
                    showNotification(`Победа!`);
                } else {
                    STATE.userBalance -= bet;
                    UI.coinflipResult.textContent = `Вы проиграли ${bet} ⭐.`;
                    showNotification(`Проигрыш!`);
                }
                updateBalanceDisplay();
                STATE.coinflipState.isFlipping = false;
                 UI.coin.classList.remove('flipping');
                 UI.coin.style.transform = result === 'tails' ? 'rotateY(180deg)' : 'rotateY(0deg)';

            }, 1200);
        }, 100);
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

        STATE.rpsState.isPlaying = true;
        const choices = ['rock', 'paper', 'scissors'];
        const computerChoice = choices[Math.floor(Math.random() * choices.length)];

        const choiceMap = {
            rock: '✊',
            paper: '✋',
            scissors: '✌️'
        };

        UI.rpsPlayerChoice.textContent = choiceMap[playerChoice];
        UI.rpsComputerChoice.textContent = choiceMap[computerChoice];
        
        let resultMessage = '';
        if (playerChoice === computerChoice) {
            resultMessage = "Ничья!";
        } else if (
            (playerChoice === 'rock' && computerChoice === 'scissors') ||
            (playerChoice === 'paper' && computerChoice === 'rock') ||
            (playerChoice === 'scissors' && computerChoice === 'paper')
        ) {
            resultMessage = `Вы выиграли ${bet} ⭐!`;
            STATE.userBalance += bet;
            showNotification(`Победа!`);
        } else {
            resultMessage = `Вы проиграли ${bet} ⭐.`;
            STATE.userBalance -= bet;
            showNotification(`Проигрыш!`);
        }
        
        UI.rpsResultMessage.textContent = resultMessage;
        updateBalanceDisplay();

        setTimeout(() => {
            STATE.rpsState.isPlaying = false;
            UI.rpsResultMessage.textContent = '';
            UI.rpsPlayerChoice.textContent = '?';
            UI.rpsComputerChoice.textContent = '?';
        }, 2000);
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
        UI.upgradeView = document.getElementById('upgrade-view');
        UI.upgradeWheel = document.getElementById('upgrade-wheel');
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

        // Начальное состояние
        loadTelegramData();
        updateBalanceDisplay();
        switchView('game-view');
        populateCasePreview();
        setInterval(updateTimer, 1000);
        
    } catch (error) {
        console.error("Помилка під час ініціалізації:", error);
        alert("Сталася критична помилка. Будь ласка, перевірте консоль (F12). Повідомлення: " + error.message);
    }
});
