document.addEventListener('DOMContentLoaded', () => {

    // =========================================================================
    // 1. 常量与配置
    // =========================================================================
    const SLEEP_ONSET_MINS = 15;
    const SLEEP_CYCLE_MINS = 90;
    const sleepTips = [ "For a better night's sleep, avoid caffeine in the afternoon and evening.", "Try to stick to a consistent sleep schedule, even on weekends.", "Create a relaxing bedtime routine, like reading a book or taking a warm bath.", "Ensure your bedroom is dark, quiet, and cool for optimal sleep.", "Avoid heavy meals or excessive fluids right before bed." ];
    let ITEM_HEIGHT = 70; // Default value, will be dynamically calculated.

    // =========================================================================
    // 2. DOM 元素获取
    // =========================================================================
    const modeToggle = document.getElementById('modeToggle');
    const modeLabel = document.getElementById('modeLabel');
    const calculateBtn = document.getElementById('calculateBtn');
    const sleepNowBtn = document.getElementById('sleepNowBtn');
    const resultsDiv = document.getElementById('results');
    const cycleChartContainer = document.getElementById('cycleChartContainer');
    const tipContainer = document.getElementById('tipContainer');

    const hoursList = document.getElementById('hours-list');
    const minutesList = document.getElementById('minutes-list');
    const secondsList = document.getElementById('seconds-list');
    
    // =========================================================================
    // 3. 状态变量
    // =========================================================================
    let isWakeUpMode = false;
    let selectedTime = { hours: 7, minutes: 30, seconds: 0 }; 

    // =========================================================================
    // 4. 核心计算逻辑
    // =========================================================================
    function formatTime(date) {
        let hours = date.getHours();
        let minutes = date.getMinutes();
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12; 
        minutes = minutes < 10 ? '0' + minutes : minutes;
        return `${hours}:${minutes} ${ampm}`;
    }

    function calculateBedtimes(wakeUpTime) {
        const suggestions = [];
        for (let cycles = 6; cycles >= 4; cycles--) {
            const totalSleepMinutes = (cycles * SLEEP_CYCLE_MINS) + SLEEP_ONSET_MINS;
            const bedtime = new Date(wakeUpTime.getTime() - totalSleepMinutes * 60000);
            suggestions.push(formatTime(bedtime));
        }
        return suggestions;
    }

    function calculateWakeUpTimes(bedtime) {
        const suggestions = [];
        const sleepStartTime = new Date(bedtime.getTime() + SLEEP_ONSET_MINS * 60000);
        for (let cycles = 4; cycles <= 6; cycles++) {
            const totalSleepMinutes = cycles * SLEEP_CYCLE_MINS;
            const wakeUpTime = new Date(sleepStartTime.getTime() + totalSleepMinutes * 60000);
            suggestions.push(formatTime(wakeUpTime));
        }
        return suggestions;
    }
    
    // =========================================================================
    // 5. UI 更新与动画函数
    // =========================================================================
    function displayResults(title, suggestions) {
        // Clear previous results
        resultsDiv.innerHTML = '';
        cycleChartContainer.innerHTML = '';

        // Create and animate title
        const titleEl = document.createElement('h3');
        titleEl.innerHTML = title;
        titleEl.className = "text-lg font-bold text-slate-800 mb-3";
        resultsDiv.appendChild(titleEl);
        gsap.from(titleEl, { duration: 0.5, opacity: 0, y: 10 });
        
        // Create and animate result items
        suggestions.forEach((time, index) => {
            const p = document.createElement('p');
            p.textContent = time;
            p.className = "bg-slate-100 p-3 rounded-lg font-bold text-slate-700";
            resultsDiv.appendChild(p);
        });
        gsap.from(".results p", { duration: 0.5, opacity: 0, y: 10, stagger: 0.1, delay: 0.1 });

        // Create and animate cycle chart
        const totalMinutes = SLEEP_ONSET_MINS + 6 * SLEEP_CYCLE_MINS;
        const onsetBar = document.createElement('div');
        onsetBar.className = 'h-full bg-yellow-300 rounded-l-md';
        onsetBar.style.width = `${(SLEEP_ONSET_MINS / totalMinutes) * 100}%`;
        onsetBar.title = `~15 mins to fall asleep`;
        cycleChartContainer.appendChild(onsetBar);
        for (let i = 1; i <= 6; i++) {
            const cycleBar = document.createElement('div');
            cycleBar.className = `h-full ${i % 2 ? 'bg-sky-400' : 'bg-sky-500'}`;
            cycleBar.style.width = `${(SLEEP_CYCLE_MINS / totalMinutes) * 100}%`;
            cycleBar.title = `Sleep Cycle ${i}`;
            cycleChartContainer.appendChild(cycleBar);
        }
        cycleChartContainer.className = 'w-full h-3 flex rounded-md overflow-hidden';
        gsap.from(cycleChartContainer, { duration: 0.5, opacity: 0, scaleX: 0, transformOrigin: 'left', delay: 0.3 });
        
        // Show a random tip
        const randomTip = sleepTips[Math.floor(Math.random() * sleepTips.length)];
        tipContainer.innerHTML = `<div class="bg-violet-100 text-violet-800 p-4 rounded-lg text-sm text-left">💡 <strong>Tip:</strong> ${randomTip}</div>`;
        gsap.from(tipContainer.children[0], { duration: 0.5, opacity: 0, delay: 0.5 });
    }

    // =========================================================================
    // 6. 滚轮选择器逻辑 (已修复)
    // =========================================================================
    function setupPicker(listElement, max, type) {
        const liClasses = 'h-16 sm:h-20 flex items-center justify-center text-4xl sm:text-5xl font-bold text-slate-400 transition-all duration-300 select-none';
        listElement.innerHTML = `<li class="${liClasses}"></li>`;
        for (let i = 0; i < max; i++) {
            const li = document.createElement('li');
            li.textContent = String(i).padStart(2, '0');
            li.className = liClasses;
            listElement.appendChild(li);
        }
        listElement.innerHTML += `<li class="${liClasses}"></li>`;

        let lastWheelTime = 0;
        let isDragging = false;
        let startY = 0;
        let currentY = 0;
        let listY = 0;
        const column = listElement.parentElement;
        
        function updateSelection(animated = false) {
            const selectedIndex = Math.max(0, Math.min(max - 1, Math.round(-listY / ITEM_HEIGHT)));
            listY = -selectedIndex * ITEM_HEIGHT;
            if (type === 'hours') selectedTime.hours = selectedIndex;
            if (type === 'minutes') selectedTime.minutes = selectedIndex;
            if (type === 'seconds') selectedTime.seconds = selectedIndex;
            listElement.querySelectorAll('li').forEach((li, index) => {
                li.classList.toggle('selected', index - 1 === selectedIndex);
            });
            gsap.to(listElement, { y: listY, duration: animated ? 0.2 : 0, ease: 'power1.out' });
        }

        function onStart(e) { isDragging = true; startY = e.clientY || e.touches[0].clientY; currentY = listY; }
        function onMove(e) { if (!isDragging) return; const newY = e.clientY || e.touches[0].clientY; const deltaY = newY - startY; listY = currentY + deltaY; const minTranslateY = -(max - 1) * ITEM_HEIGHT; listY = Math.max(minTranslateY, Math.min(0, listY)); gsap.set(listElement, { y: listY }); }
        function onEnd() { if (!isDragging) return; isDragging = false; updateSelection(true); }
        function onWheel(e) { e.preventDefault(); const now = Date.now(); if (now - lastWheelTime < 50) return; lastWheelTime = now; let currentIndex = Math.round(-listY / ITEM_HEIGHT); if (e.deltaY > 0) { currentIndex++; } else { currentIndex--; } currentIndex = Math.max(0, Math.min(max - 1, currentIndex)); listY = -currentIndex * ITEM_HEIGHT; updateSelection(true); }

        listY = -selectedTime[type] * ITEM_HEIGHT;
        updateSelection();

        column.addEventListener('mousedown', onStart);
        window.addEventListener('mousemove', onMove);
        window.addEventListener('mouseup', onEnd);
        column.addEventListener('touchstart', onStart, { passive: true });
        window.addEventListener('touchmove', onMove, { passive: false });
        window.addEventListener('touchend', onEnd);
        column.addEventListener('wheel', onWheel, { passive: false });
    }

    // =========================================================================
    // 7. 事件监听器 (已增强)
    // =========================================================================
    modeToggle.addEventListener('change', () => {
        isWakeUpMode = modeToggle.checked;
        if (isWakeUpMode) {
            modeLabel.textContent = 'go to bed at';
            calculateBtn.textContent = 'Calculate Wake-up Time';
        } else {
            modeLabel.textContent = 'wake up at';
            calculateBtn.textContent = 'Calculate Bedtime';
        }
    });

    calculateBtn.addEventListener('click', () => {
        const now = new Date();
        const targetTime = new Date(now.getFullYear(), now.getMonth(), now.getDate(), selectedTime.hours, selectedTime.minutes, selectedTime.seconds);
        let suggestions, title;
        if (isWakeUpMode) {
            if (targetTime < now) targetTime.setDate(targetTime.getDate() + 1);
            title = `To go to bed at <strong>${formatTime(targetTime)}</strong>, you should wake up at:`;
            suggestions = calculateWakeUpTimes(targetTime);
        } else {
            if (targetTime < now) targetTime.setDate(targetTime.getDate() + 1);
            title = `To wake up at <strong>${formatTime(targetTime)}</strong>, you should go to bed at:`;
            suggestions = calculateBedtimes(targetTime);
        }
        displayResults(title, suggestions);
    });

    sleepNowBtn.addEventListener('click', () => {
        const now = new Date();
        const title = `If you go to bed <strong>right now</strong>, you should wake up at:`;
        const suggestions = calculateWakeUpTimes(now);
        displayResults(title, suggestions);
        // Optional: Animate scroll to results
        window.scrollTo({ top: resultsDiv.offsetTop - 80, behavior: 'smooth' });
    });
    
    // =========================================================================
    // 8. 初始化 (已修复)
    // =========================================================================
    function initialize() {
        // **FIX:** Dynamically calculate ITEM_HEIGHT from the CSS for perfect accuracy
        const tempLi = document.createElement('li');
        tempLi.className = 'h-16 sm:h-20'; // The same classes used in setupPicker
        tempLi.style.visibility = 'hidden';
        document.body.appendChild(tempLi);
        ITEM_HEIGHT = tempLi.offsetHeight;
        document.body.removeChild(tempLi);

        if (ITEM_HEIGHT === 0) ITEM_HEIGHT = 70; // Fallback just in case

        // Setup all pickers with the correct height
        setupPicker(hoursList, 24, 'hours');
        setupPicker(minutesList, 60, 'minutes');
        setupPicker(secondsList, 60, 'seconds');
    }

    initialize();
});