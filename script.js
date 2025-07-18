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
        possibleItems: [
            { id: 1, name: 'Cigar', imageSrc: 'item.png', value: 3170 },
            { id: 2, name: 'Bear', imageSrc: 'item1.png', value: 440 },
            { id: 3, name: 'Sigma', imageSrc: 'case.png', value: 50 },
        ]
    };

    // --- ОБ'ЄКТ З ЕЛЕМЕНТАМИ DOM ---
    const UI = {};

    // --- ФУНКЦІЇ ---

    function loadTelegramData() {
        try {
            const tg = window.Telegram.WebApp;
            // Робимо кнопку "назад" видимою, якщо це доречно
            tg.BackButton.show();
            tg.BackButton.onClick(() => {
                // Повертаємо користувача на головний екран при кліку
                switchView('game-view');
            });

            const user = tg.initDataUnsafe.user;
            
            if (user) {
                if (UI.profilePhoto) {
                    UI.profilePhoto.src = user.photo_url || ''; // Показуємо фото або нічого
                }
                if (UI.profileName) {
                    UI.profileName.textContent = `${user.first_name || ''} ${user.last_name || ''}`.trim();
                }
                if (UI.profileId) {
                    UI.profileId.textContent = `User ID ${user.id}`;
                }
            }
        } catch (error) {
            console.error("Не вдалося завантажити дані Telegram:", error);
            // Запасний варіант, якщо додаток відкрито не в Telegram
            if (UI.profileName) UI.profileName.textContent = "Guest";
            if (UI.profileId) UI.profileId.textContent = "User ID 0";
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

        // Керування кнопкою "назад" в Telegram
        if (viewId !== 'game-view' && window.Telegram && window.Telegram.WebApp) {
            window.Telegram.WebApp.BackButton.show();
        } else if (window.Telegram && window.Telegram.WebApp) {
            window.Telegram.WebApp.BackButton.hide();
        }

        if (viewId === 'profile-view') {
            renderInventory();
            renderHistory();
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

        const itemWidth = 120 + 10;
        const randomOffset = Math.random() * 100 - 50;
        const targetPosition = (winnerIndex * itemWidth) + randomOffset;

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

            const itemHeight = 100 + 10;
            const randomOffset = Math.random() * 80 - 40;
            const targetPosition = (winnerIndex * itemHeight) + randomOffset;

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

    // --- ІНІЦІАЛІЗАЦІЯ ---
    try {
        // Пошук елементів
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
        UI.profileTabs = document.querySelectorAll('.profile-tab-btn');
        UI.profileContents = document.querySelectorAll('.profile-tab-content');
        UI.profilePhoto = document.getElementById('profile-photo');
        UI.profileName = document.getElementById('profile-name');
        UI.profileId = document.getElementById('profile-id');
        
        if (!UI.caseImageBtn) throw new Error('Не вдалося знайти картинку кейса з id="case-image-btn"');

        // Обробники подій
        UI.caseImageBtn.addEventListener('click', handleCaseClick);
        UI.startSpinBtn.addEventListener('click', startSpinProcess);
        UI.quantitySelector.addEventListener('click', handleQuantityChange);
        UI.navButtons.forEach(btn => btn.addEventListener('click', () => switchView(btn.dataset.view)));
        UI.profileTabs.forEach(tab => tab.addEventListener('click', function() {
            UI.profileTabs.forEach(t => t.classList.remove('active'));
            UI.profileContents.forEach(c => c.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById(tab.dataset.tab + '-content').classList.add('active');
        }));
        UI.modalOverlay.addEventListener('click', () => {
            document.querySelectorAll('.modal.visible').forEach(modal => hideModal(modal));
        });
        document.querySelector('[data-close-modal="pre-open-modal"]').addEventListener('click', () => hideModal(UI.preOpenModal));

        // Початковий стан
        loadTelegramData(); // Завантажуємо дані Telegram
        updateBalanceDisplay();
        switchView('game-view');
        populateCasePreview();
        
    } catch (error) {
        console.error("Помилка під час ініціалізації:", error);
        alert("Сталася критична помилка. Будь ласка, перевірте консоль (F12). Повідомлення: " + error.message);
    }
});
