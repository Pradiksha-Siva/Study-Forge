// Pomodoro Focus Timer Logic

let timer = null;
let timerSeconds = 25 * 60; // 25 minutes
let currentTotalSeconds = 25 * 60;
let isRunning = false;
let pomoMode = 'study'; // 'study' or 'break'

const display = document.getElementById('pomoTimeDisplay');
const fillCircle = document.getElementById('timerCircleFill');
const playBtn = document.getElementById('btnPomoPlay');
const modeBadge = document.getElementById('pomoModeBadge');

function updateDisplay() {
    if (!display) return;
    const minutes = Math.floor(timerSeconds / 60);
    const seconds = timerSeconds % 60;
    display.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    
    // Calculate circular stroke fill offset (circumference of radius 45 is 282.7)
    if (fillCircle) {
        const percentage = (currentTotalSeconds - timerSeconds) / currentTotalSeconds;
        const offset = 282.7 * percentage;
        fillCircle.style.strokeDashoffset = offset;
    }
}

function togglePomodoro() {
    if (isRunning) {
        // Pause timer
        clearInterval(timer);
        isRunning = false;
        if (playBtn) playBtn.innerHTML = '<i class="fa-solid fa-play"></i>';
    } else {
        // Start timer
        isRunning = true;
        if (playBtn) playBtn.innerHTML = '<i class="fa-solid fa-pause"></i>';
        
        timer = setInterval(() => {
            if (timerSeconds > 0) {
                timerSeconds--;
                updateDisplay();
            } else {
                clearInterval(timer);
                isRunning = false;
                if (playBtn) playBtn.innerHTML = '<i class="fa-solid fa-play"></i>';
                
                // Play completion notification beep
                playSyntheticBeep('success');
                
                // Transition mode
                if (pomoMode === 'study') {
                    alert("Focus session completed! Time for a short break.");
                    pomoMode = 'break';
                    if (modeBadge) {
                        modeBadge.textContent = 'Break Time';
                        modeBadge.className = 'pomo-mode-badge break';
                        document.querySelector('.pomo-timer-circle').classList.add('break-mode');
                    }
                    timerSeconds = 5 * 60; // 5 minute break
                    currentTotalSeconds = 5 * 60;
                } else {
                    alert("Break is over! Time to focus.");
                    pomoMode = 'study';
                    if (modeBadge) {
                        modeBadge.textContent = 'Study Time';
                        modeBadge.className = 'pomo-mode-badge';
                        document.querySelector('.pomo-timer-circle').classList.remove('break-mode');
                    }
                    timerSeconds = 25 * 60; // 25 minute study
                    currentTotalSeconds = 25 * 60;
                }
                updateDisplay();
            }
        }, 1000);
    }
}

function resetPomodoro() {
    clearInterval(timer);
    isRunning = false;
    pomoMode = 'study';
    timerSeconds = 25 * 60;
    currentTotalSeconds = 25 * 60;
    
    if (playBtn) playBtn.innerHTML = '<i class="fa-solid fa-play"></i>';
    if (modeBadge) {
        modeBadge.textContent = 'Study Time';
        modeBadge.className = 'pomo-mode-badge';
        document.querySelector('.pomo-timer-circle').classList.remove('break-mode');
    }
    updateDisplay();
}

// Generate web sound synthesize effects natively
function playSyntheticBeep(type) {
    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioCtx.createOscillator();
        const gainNode = audioCtx.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioCtx.destination);
        
        if (type === 'success') {
            oscillator.type = 'sine';
            oscillator.frequency.setValueAtTime(523.25, audioCtx.currentTime); // C5
            gainNode.gain.setValueAtTime(0.08, audioCtx.currentTime);
            oscillator.start();
            
            setTimeout(() => {
                oscillator.frequency.setValueAtTime(659.25, audioCtx.currentTime); // E5
            }, 150);
            
            setTimeout(() => {
                oscillator.frequency.setValueAtTime(783.99, audioCtx.currentTime); // G5
            }, 300);
            
            setTimeout(() => {
                oscillator.stop();
                audioCtx.close();
            }, 450);
        }
    } catch (e) {
        console.warn("Audio Context playback failed or blocked:", e);
    }
}

// Initialize on page load
if (display) {
    updateDisplay();
}
