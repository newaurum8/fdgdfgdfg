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
        contestEndDate: new Date(Date.now() + 6 * 24 * 60 * 60 * 1000 + 15 * 60 * 60 * 1000), // 6 дней 15 часов от сейчас
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
    };

    // --- ОБ'ЄКТ З ЕЛЕМЕНТАМИ DOM ---
    const UI = {};

    // --- ФУНКЦІЇ ---

    function showNotification(message) {
        if (!UI.notificationToast) return;
        UI.notificationToast.textContent = message;
        UI.notificationToast.classList.add('visible');

        setTimeout(() => {
            UI.notificationToast.classList.remove('visible');
        }, 2000);
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
        UI.views.forEach(view => view.classList.remove('active'));
        UI.navButtons.forEach(btn => btn.classList.remove('active'));
        
        const viewToShow = document.getElementById(viewId);
        const btnToActivate = document.querySelector(`.nav-btn[data-view="${viewId}"]`);

        if (viewToShow) viewToShow.classList.add('active');
        if (btnToActivate) btnToActivate.classList.add('active');

        if (window.Telegram && window.Telegram.WebApp) {
            const tg = window.Telegram.WebApp;
            if (viewId !== 'game-view') {
                tg.BackButton.show();
                tg.BackButton.onClick(() => switchView('game-view'));
            } else {
                tg.BackButton.hide();
                tg.BackButton.offClick();
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
        
        const itemWidth = 120;
        const itemMargin = 5;
        const totalItemWidth = itemWidth + (itemMargin * 2);
        
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

            const itemHeight = 100;
            const itemMargin = 5;
            const totalItemHeight = itemHeight + (itemMargin * 2);

            const targetPosition = (winnerIndex * totalItemHeight) + (totalItemHeight / 2);

            track.style.transition = 'none';
            track.style.top = '0px';
            track.getBoundingClientRect(); 
            track.style.transition = `top ${5 + Math.random() * 2}s cubic-bezier(0.2, 0.8, 0.2, 1)`;
            track.style.top = `calc(50% - ${targetPosition}px)`;

            track.addEventListener('transitionend', () => {
                animationsFinished++;
                if (animationsFinished === STATE.lastWonItems.length) {
                    showResult();
                }
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
                <button class="secondary-button" id="result-sell-btn">
                    Продати все за ⭐ ${totalValue.toLocaleString('uk-UA')}
                </button>
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

        const closeBtn = modalContent.querySelector('.close-btn');
        const sellBtn = modalContent.querySelector('#result-sell-btn');
        const spinAgainBtn = modalContent.querySelector('#result-spin-again-btn');

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
        const sortedItems = [...STATE.possibleItems].sort((a, b) => b.value - a.value);
        sortedItems.forEach(item => {
            const itemEl = document.createElement('div');
            itemEl.classList.add('preview-item');
            itemEl.innerHTML = `
                <img src="${item.imageSrc}" alt="${item.name}">
                <div class="inventory-item-price">⭐ ${item.value.toLocaleString('uk-UA')}</div>
            `;
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
        const now = new Date();
        const timeLeft = STATE.contestEndDate - now;

        if (timeLeft <= 0) {
            UI.contestTimer.textContent = 'Конкурс завершено';
            // Можно остановить таймер, если нужно
            // clearInterval(timerIntervalId); 
            return;
        }

        const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
        const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);

        const paddedHours = String(hours).padStart(2, '0');
        const paddedMinutes = String(minutes).padStart(2, '0');
        const paddedSeconds = String(seconds).padStart(2, '0');

        UI.contestTimer.textContent = `${days} дней ${paddedHours}:${paddedMinutes}:${paddedSeconds} 🕔`;
    }
    // --- КОНЕЦ ЛОГИКИ КОНКУРСОВ ---

    // --- ЛОГИКА АПГРЕЙДА ---

    function resetUpgradeState(resetRotation = false) {
        STATE.upgradeState.yourItem = null;
        STATE.upgradeState.desiredItem = null;
        STATE.upgradeState.isUpgrading = false;
        
        if (resetRotation) {
            STATE.upgradeState.currentRotation = 0;
            UI.upgradeWheel.style.transition = 'none';
            UI.upgradeWheel.style.transform = `rotate(0deg)`;
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
        const { yourItem, desiredItem, chance, multiplier } = STATE.upgradeState;

        function updateSlot(slot, item) {
            const placeholder = slot.querySelector('.slot-placeholder');
            const content = slot.querySelector('.slot-content');
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
            itemEl.innerHTML = `
                <img src="${item.imageSrc}" alt="${item.name}">
                <div class="picker-item-name">${item.name}</div>
                <div class="picker-item-value">⭐ ${item.value.toLocaleString('uk-UA')}</div>
            `;

            const isSelectedForYour = yourItem && item.uniqueId && yourItem.uniqueId === item.uniqueId;
            const isSelectedForDesired = desiredItem && desiredItem.id === item.id;
            if (isSelectedForYour || isSelectedForDesired) {
                itemEl.classList.add('selected');
            }

            itemEl.addEventListener('click', () => handleItemPick(item));
            UI.itemPickerContent.appendChild(itemEl);
        });
    }

    function handleItemPick(item) {
        if (STATE.upgradeState.isUpgrading) return;
        const { activePicker } = STATE.upgradeState;

        if (activePicker === 'inventory') {
            STATE.upgradeState.yourItem = { ...item }; 
        } else {
            STATE.upgradeState.desiredItem = { ...item };
        }
        
        calculateUpgradeChance();
        renderUpgradeUI();
        renderItemPicker();
    }

    function handleUpgradeClick() {
        const { yourItem, desiredItem, chance, isUpgrading } = STATE.upgradeState;
        if (!yourItem || !desiredItem || isUpgrading) return;

        STATE.upgradeState.isUpgrading = true;
        UI.performUpgradeBtn.disabled = true;

        const roll = Math.random() * 100;
        const isSuccess = roll < chance;

        const chanceAngle = (chance / 100) * 360;
        const randomOffset = Math.random() * 0.9 + 0.05;

        const stopPoint = isSuccess
            ? chanceAngle * randomOffset
            : chanceAngle + (360 - chanceAngle) * randomOffset;
        
        const rotation = (5 * 360) + (360 - stopPoint);
        STATE.upgradeState.currentRotation += rotation;

        UI.upgradeWheel.style.transition = 'transform 3s cubic-bezier(0.2, 0.8, 0.2, 1)';
        
        setTimeout(() => {
            UI.upgradeWheel.style.transform = `rotate(${STATE.upgradeState.currentRotation}deg)`;
        }, 10);

        UI.upgradeWheel.addEventListener('transitionend', () => {
            setTimeout(() => {
                const itemIndex = STATE.inventory.findIndex(invItem => invItem.uniqueId === yourItem.uniqueId);
                if (itemIndex > -1) {
                    STATE.inventory.splice(itemIndex, 1);
                }

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
        
        if (!UI.caseImageBtn) throw new Error('Не вдалося знайти картинку кейса з id="case-image-btn"');

        // Обработчики событий
        UI.caseImageBtn.addEventListener('click', handleCaseClick);
        if(UI.startSpinBtn) UI.startSpinBtn.addEventListener('click', startSpinProcess);
        if (UI.quantitySelector) UI.quantitySelector.addEventListener('click', handleQuantityChange);
        UI.navButtons.forEach(btn => btn.addEventListener('click', () => switchView(btn.dataset.view)));
        if (UI.inviteFriendBtn) UI.inviteFriendBtn.addEventListener('click', inviteFriend);
        if (UI.copyLinkBtn) UI.copyLinkBtn.addEventListener('click', copyInviteLink);
        
        // Обработчики для Конкурсов
        if (UI.buyTicketBtn) UI.buyTicketBtn.addEventListener('click', buyTickets);
        if (UI.ticketQuantityPlus) UI.ticketQuantityPlus.addEventListener('click', () => handleTicketQuantityChange(1));
        if (UI.ticketQuantityMinus) UI.ticketQuantityMinus.addEventListener('click', () => handleTicketQuantityChange(-1));
        
        UI.profileTabs.forEach(tab => tab.addEventListener('click', function() {
            UI.profileTabs.forEach(t => t.classList.remove('active'));
            UI.profileContents.forEach(c => c.classList.remove('active'));
            this.classList.add('active');
            const contentId = this.dataset.tab + '-content';
            const contentEl = document.getElementById(contentId);
            if(contentEl) contentEl.classList.add('active');
        }));
        
        UI.modalOverlay.addEventListener('click', () => {
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
                
                UI.yourItemSlot.classList.toggle('active-selection', STATE.upgradeState.activePicker === 'inventory');
                UI.desiredItemSlot.classList.toggle('active-selection', STATE.upgradeState.activePicker === 'desired');
                
                renderItemPicker();
            });
        });

        if (UI.yourItemSlot) UI.yourItemSlot.addEventListener('click', () => {
            if (!STATE.upgradeState.isUpgrading && document.getElementById('picker-tab-inventory')) {
                 document.getElementById('picker-tab-inventory').click();
            }
        });
        if (UI.desiredItemSlot) UI.desiredItemSlot.addEventListener('click', () => {
             if (!STATE.upgradeState.isUpgrading && document.getElementById('picker-tab-desired')) {
                document.getElementById('picker-tab-desired').click();
             }
        });

        if (UI.performUpgradeBtn) UI.performUpgradeBtn.addEventListener('click', handleUpgradeClick);

        // Начальное состояние
        loadTelegramData();
        updateBalanceDisplay();
        switchView('game-view');
        populateCasePreview();
        setInterval(updateTimer, 1000); // Запускаем таймер
        
    } catch (error) {
        console.error("Помилка під час ініціалізації:", error);
        alert("Сталася критична помилка. Будь ласка, перевірте консоль (F12). Повідомлення: " + error.message);
    }
});