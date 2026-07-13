// Spaced Repetition Study Engine Controller

let cardsQueue = [];
let currentCardIdx = 0;
let sessionXPGained = 0;
let studyMode = 'due'; // 'due' or 'practice'

// DOM elements
const cardBox = document.getElementById('quizCardBox');
const completedState = document.getElementById('completedState');
const flashcard = document.getElementById('flashcard');

const progressLabel = document.getElementById('currentCardIndex');
const progressFill = document.getElementById('sessionProgressFill');

const cardSubject = document.getElementById('cardSubject');
const cardTopic = document.getElementById('cardTopic');
const cardQuestion = document.getElementById('cardQuestion');

const cardSubjectBack = document.getElementById('cardSubjectBack');
const cardTopicBack = document.getElementById('cardTopicBack');
const cardAnswer = document.getElementById('cardAnswer');

const summaryXP = document.getElementById('summaryXP');
const summaryStreak = document.getElementById('summaryStreak');

document.addEventListener('DOMContentLoaded', () => {
    loadSessionCards();
});

function loadSessionCards() {
    // Reset session trackers
    currentCardIdx = 0;
    cardsQueue = [];
    
    // UI elements update
    if (completedState) completedState.classList.add('hidden');
    if (cardBox) cardBox.classList.remove('hidden');
    if (flashcard) flashcard.classList.remove('flipped');
    
    fetch(`/study/due-cards?mode=${studyMode}`)
        .then(res => res.json())
        .then(data => {
            cardsQueue = data.cards;
            if (cardsQueue.length > 0) {
                renderCurrentCard();
            } else {
                showCompletedState();
            }
        })
        .catch(err => console.error("Error loading session cards:", err));
}

function renderCurrentCard() {
    if (cardsQueue.length === 0) return;
    
    // Close flips
    if (flashcard) flashcard.classList.remove('flipped');
    
    const card = cardsQueue[currentCardIdx];
    
    // Front elements
    if (cardSubject) cardSubject.textContent = card.subject;
    if (cardTopic) cardTopic.textContent = card.topic;
    if (cardQuestion) cardQuestion.textContent = card.question;
    
    // Back elements
    if (cardSubjectBack) cardSubjectBack.textContent = card.subject;
    if (cardTopicBack) cardTopicBack.textContent = card.topic;
    if (cardAnswer) cardAnswer.textContent = card.answer;
    
    // Progress bar calculations
    const displayIndex = currentCardIdx + 1;
    if (progressLabel) progressLabel.textContent = `Card ${displayIndex} of ${cardsQueue.length}`;
    if (progressFill) {
        const percentage = ((displayIndex - 1) / cardsQueue.length) * 100;
        progressFill.style.width = `${percentage}%`;
    }
}

function flipCard() {
    if (flashcard) {
        flashcard.classList.toggle('flipped');
    }
}

function submitRating(ratingText) {
    if (cardsQueue.length === 0) return;
    const card = cardsQueue[currentCardIdx];
    
    fetch(`/study/rate/${card.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rating: ratingText })
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                sessionXPGained += data.xp_gained;
                
                // Trigger Duolingo style popups for achievements
                if (data.unlocked_achievements && data.unlocked_achievements.length > 0) {
                    data.unlocked_achievements.forEach(ach => triggerAchievementPopup(ach));
                }
                
                // Sync Global Header indicators
                updateHeaderGamification(data);
                
                // Move queue forward
                currentCardIdx++;
                if (currentCardIdx < cardsQueue.length) {
                    // Slide transition animation helper
                    setTimeout(() => renderCurrentCard(), 200);
                } else {
                    if (progressFill) progressFill.style.width = '100%';
                    setTimeout(() => showCompletedState(data.streak), 300);
                }
            }
        })
        .catch(err => console.error("Error rating card:", err));
}

function updateHeaderGamification(data) {
    // XP Level progress
    const levelFill = document.querySelector('.level-progress-fill');
    const xpSubText = document.querySelector('.badge-val-sub');
    const levelLabel = document.querySelector('.badge-label');
    const streakVal = document.querySelector('.streak-badge .badge-val');
    const dailyGoalVal = document.getElementById('dailyGoalText');
    const dailyGoalBadge = document.getElementById('dailyGoalBadge');
    
    if (levelFill) levelFill.style.width = `${data.xp_in_level}%`;
    if (xpSubText) xpSubText.textContent = `${data.xp_in_level} / 100 XP`;
    if (levelLabel) levelLabel.textContent = `LEVEL ${data.level}`;
    if (streakVal) streakVal.textContent = `${data.streak} Days`;
    
    // Sync daily goal tracker badge
    if (dailyGoalVal) {
        // Increment count
        const splitText = dailyGoalVal.textContent.split('/');
        const currentGoal = parseInt(splitText[1]) || 10;
        const newTodayCount = parseInt(splitText[0]) + 1;
        dailyGoalVal.textContent = `${newTodayCount} / ${currentGoal}`;
    }
}

function showCompletedState(currentStreak = 0) {
    if (cardBox) cardBox.classList.add('hidden');
    if (completedState) completedState.classList.remove('hidden');
    
    if (summaryXP) summaryXP.textContent = `+${sessionXPGained}`;
    if (summaryStreak) summaryStreak.textContent = `${currentStreak} Days`;
    
    // Customize text based on mode
    const title = completedState.querySelector('h2');
    const desc = document.getElementById('completionMessage');
    
    if (studyMode === 'practice') {
        title.textContent = "Practice Session Finished!";
        desc.textContent = "Great job sharpening your skills with practice reviews!";
    } else {
        title.textContent = "All Caught Up!";
        desc.textContent = "You have completed all scheduled card reviews for now.";
    }
}

function changeMode(modeName) {
    studyMode = modeName;
    sessionXPGained = 0;
    
    const btnDue = document.getElementById('btnModeDue');
    const btnPractice = document.getElementById('btnModePractice');
    const desc = document.getElementById('modeDescription');
    
    if (modeName === 'due') {
        if (btnDue) btnDue.classList.add('active');
        if (btnPractice) btnPractice.classList.remove('active');
        if (desc) desc.textContent = 'Reviewing cards scheduled for spaced repetition.';
    } else {
        if (btnDue) btnDue.classList.remove('active');
        if (btnPractice) btnPractice.classList.add('active');
        if (desc) desc.textContent = 'Reviewing all cards in your decks for practice.';
    }
    
    loadSessionCards();
}

// Gamified dynamic popups
function triggerAchievementPopup(ach) {
    const banner = document.getElementById('achievementBanner');
    const icon = document.getElementById('achBannerIcon');
    const name = document.getElementById('achBannerName');
    const desc = document.getElementById('achBannerDesc');
    
    if (!banner) return;
    
    icon.textContent = ach.badge_icon;
    name.textContent = ach.name.toUpperCase();
    desc.textContent = ach.description;
    
    banner.classList.remove('hidden');
    
    // Play achievement audio effect
    playSyntheticUnlockBeep();
    
    // Auto fadeout after 6 seconds
    setTimeout(() => {
        banner.style.transition = 'opacity 0.5s ease';
        banner.style.opacity = '0';
        setTimeout(() => {
            banner.classList.add('hidden');
            banner.style.opacity = '1';
        }, 500);
    }, 6000);
}

function playSyntheticUnlockBeep() {
    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioCtx.createOscillator();
        const gainNode = audioCtx.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioCtx.destination);
        
        oscillator.type = 'sine';
        gainNode.gain.setValueAtTime(0.08, audioCtx.currentTime);
        
        // Classic retro gamified arpeggio
        oscillator.frequency.setValueAtTime(523.25, audioCtx.currentTime); // C5
        oscillator.start();
        
        setTimeout(() => oscillator.frequency.setValueAtTime(659.25, audioCtx.currentTime), 100); // E5
        setTimeout(() => oscillator.frequency.setValueAtTime(783.99, audioCtx.currentTime), 200); // G5
        setTimeout(() => oscillator.frequency.setValueAtTime(1046.50, audioCtx.currentTime), 300); // C6
        
        setTimeout(() => {
            oscillator.stop();
            audioCtx.close();
        }, 500);
    } catch (e) {
        console.warn("Achievement audio blocked by browser:", e);
    }
}
