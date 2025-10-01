/**
 * Ancient Greek Translation Evaluation App
 * Clean, no-frills interface for expert ranking of AI translations
 */

class TranslationEvaluator {
    constructor() {
        this.data = null;
        this.currentChunkIndex = 0;
        this.evaluations = [];
        this.sortableInstance = null;
        this.expertCredentials = null;
        this.sessionId = this.generateSessionId();
        
        this.init();
    }

    async init() {
        this.bindEvents();
        await this.loadData();
        this.setupDragAndDrop();
        
        // Don't show content until credentials are submitted
        if (!this.expertCredentials) {
            this.hideLoading();
            return;
        }
        
        this.displayCurrentChunk();
        this.hideLoading();
    }

    bindEvents() {
        document.getElementById('submit-btn').addEventListener('click', () => this.submitRanking());
        document.getElementById('skip-btn').addEventListener('click', () => this.skipChunk());
        document.getElementById('next-chunk-btn').addEventListener('click', () => this.nextChunk());
        document.getElementById('credentials-form').addEventListener('submit', (e) => this.handleCredentialsSubmit(e));
    }

    async loadData() {
        try {
            // Load the test chunk data
            const response = await fetch('data/galen_test_chunk_multi_model_claude_gemini_openai_20250929_150101.json');
            if (!response.ok) {
                throw new Error('Evaluation data not found');
            }
            this.data = await response.json();
            
            // Process the data for easier handling
            this.processData();
        } catch (error) {
            console.error('Error loading data:', error);
            // Fallback to demo data
            this.loadDemoData();
        }
    }

    processData() {
        // Extract paragraphs and ensure they have the required fields
        this.chunks = this.data.paragraphs || [];
        
        // Filter to only include chunks with all three model translations completed
        this.chunks = this.chunks.filter(chunk => {
            return chunk.content && 
                   chunk.openai_translation && chunk.openai_status === 'completed' &&
                   chunk.claude_translation && chunk.claude_status === 'completed' &&
                   chunk.gemini_translation && chunk.gemini_status === 'completed';
        });

        console.log(`Loaded ${this.chunks.length} evaluation chunks (filtered for complete translations from all 3 models)`);
    }

    loadDemoData() {
        // Demo data for testing when real data isn't available
        this.chunks = [
            {
                number: "1.1",
                content: "Ὅτι μὲν οὖν ἐκ θερμοῦ καὶ ψυχροῦ καὶ ξηροῦ καὶ ὑγροῦ τὰ μὲν ζώων σώματα κέκραται. καὶ ὡς οὐκ ἴση πάντων ἐστὶν ἐν τῇ κράσει μοῖρα, παλαιοῖς ἀνδράσιν ἱκανῶς ἀποδέδεικται.",
                source_word_count: 28,
                openai_translation: "That the bodies of animals are compounded from hot, cold, dry, and wet, and that the share of each in the mixture is not equal, has been sufficiently demonstrated by the ancients.",
                openai_status: "completed",
                openai_quality_score: 95,
                claude_translation: "That the bodies of living beings are composed of hot and cold and dry and moist, and that the portion of all these in the mixture is not equal, has been adequately proven by the men of old.",
                claude_status: "completed", 
                claude_quality_score: 92,
                gemini_translation: "That animal bodies are indeed mixed from hot and cold and dry and wet, and that not all have an equal share in the mixture, has been sufficiently demonstrated by ancient men.",
                gemini_status: "completed",
                gemini_quality_score: 88
            },
            {
                number: "1.2", 
                content: "φιλοσόφων τε καὶ ἰατρῶν τοῖς ἀρίστοις εἴρηται. νυνὶ δὲ τῶν κράσεων ἁπάσας ἐξευρεῖν τὰς διαφορὰς ἐν τῷδε τῷ γράμματι δίειμι.",
                source_word_count: 18,
                openai_translation: "This has been stated by the best of both philosophers and physicians. Now I shall go through and discover all the differences of mixtures in this treatise.",
                openai_status: "completed",
                openai_quality_score: 93,
                claude_translation: "It has been said by the finest of both philosophers and doctors. But now I will proceed to find all the distinctions of temperaments in this writing.",
                claude_status: "completed",
                claude_quality_score: 89,
                gemini_translation: "It has been spoken by the best of philosophers and physicians. Now I shall examine all the differences of the mixtures in this work.",
                gemini_status: "completed", 
                gemini_quality_score: 91
            }
        ];
        
        console.log('Loaded demo data');
    }

    setupDragAndDrop() {
        const container = document.getElementById('translations-container');
        
        this.sortableInstance = Sortable.create(container, {
            animation: 150,
            ghostClass: 'sortable-ghost',
            chosenClass: 'sortable-chosen',
            dragClass: 'sortable-drag',
            onEnd: () => {
                this.updateRankingBadges();
            }
        });
    }

    displayCurrentChunk() {
        if (!this.chunks || this.chunks.length === 0) {
            this.showError('No evaluation chunks available');
            return;
        }

        const chunk = this.chunks[this.currentChunkIndex];
        
        // Track time for this chunk
        this.chunkStartTime = Date.now();
        
        // Update progress
        this.updateProgress();
        
        // Display Greek text
        this.displayGreekText(chunk);
        
        // Display translations
        this.displayTranslations(chunk);
        
        // Update stats
        this.updateStats();
    }

    updateProgress() {
        const progressText = document.getElementById('progress-text');
        const progressFill = document.getElementById('progress-fill');
        
        const current = this.currentChunkIndex + 1;
        const total = this.chunks.length;
        const percentage = (current / total) * 100;
        
        progressText.textContent = `Chunk ${current} of ${total}`;
        progressFill.style.width = `${percentage}%`;
    }

    displayGreekText(chunk) {
        const greekText = document.getElementById('greek-text');
        const wordCount = document.getElementById('word-count');
        const chunkInfo = document.getElementById('chunk-info');
        
        greekText.textContent = chunk.content;
        wordCount.textContent = `${chunk.source_word_count || chunk.content.split(' ').length} words`;
        chunkInfo.textContent = `Chunk ${chunk.number}`;
    }

    displayTranslations(chunk) {
        const container = document.getElementById('translations-container');
        container.innerHTML = '';
        
        const models = ['openai', 'claude', 'gemini'];
        const translations = [];
        
        // Collect available translations
        models.forEach(model => {
            const translationKey = `${model}_translation`;
            const statusKey = `${model}_status`;
            const qualityKey = `${model}_quality_score`;
            
            if (chunk[translationKey] && chunk[statusKey] === 'completed') {
                translations.push({
                    model: model,
                    text: chunk[translationKey],
                    quality: chunk[qualityKey] || 0,
                    status: chunk[statusKey]
                });
            }
        });
        
        // Shuffle translations to avoid bias
        this.shuffleArray(translations);
        
        // Create translation cards
        translations.forEach((translation, index) => {
            const card = this.createTranslationCard(translation, index + 1);
            container.appendChild(card);
        });
        
        this.updateRankingBadges();
    }

    createTranslationCard(translation, initialRank) {
        const card = document.createElement('div');
        card.className = 'translation-card';
        card.dataset.model = translation.model;
        
        // Convert newlines to HTML line breaks for proper display
        const displayText = translation.text.replace(/\n/g, '<br>');
        
        card.innerHTML = `
            <div class="ranking-badge">${initialRank}</div>
            <div class="translation-text">${displayText}</div>
            <div class="translation-meta">
                <span class="word-count">${translation.text.split(' ').length} words</span>
            </div>
        `;
        
        return card;
    }

    generateSessionId() {
        return 'eval_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    handleCredentialsSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        this.expertCredentials = {
            name: formData.get('expert-name') || document.getElementById('expert-name').value,
            institution: formData.get('expert-institution') || document.getElementById('expert-institution').value,
            title: formData.get('expert-title') || document.getElementById('expert-title').value,
            specialization: formData.get('expert-specialization') || document.getElementById('expert-specialization').value,
            experience: formData.get('expert-experience') || document.getElementById('expert-experience').value,
            email: formData.get('expert-email') || document.getElementById('expert-email').value,
            sessionId: this.sessionId,
            startedAt: new Date().toISOString()
        };
        
        // Validate required fields
        if (!this.expertCredentials.name || !this.expertCredentials.institution || !this.expertCredentials.title) {
            alert('Please fill in all required fields (marked with *)');
            return;
        }
        
        // Hide credentials modal and show evaluation
        this.hideCredentialsModal();
        this.displayCurrentChunk();
        
        console.log('Expert credentials collected:', this.expertCredentials);
    }

    hideCredentialsModal() {
        const modal = document.getElementById('credentials-modal');
        modal.classList.remove('show');
    }

    updateRankingBadges() {
        const cards = document.querySelectorAll('.translation-card');
        cards.forEach((card, index) => {
            const badge = card.querySelector('.ranking-badge');
            badge.textContent = index + 1;
        });
    }

    shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
    }

    submitRanking() {
        const cards = document.querySelectorAll('.translation-card');
        const ranking = [];
        
        cards.forEach((card, index) => {
            ranking.push({
                model: card.dataset.model,
                rank: index + 1,
                chunk: this.chunks[this.currentChunkIndex].number
            });
        });
        
        // Store the evaluation with expert credentials
        const evaluation = {
            sessionId: this.sessionId,
            expertCredentials: this.expertCredentials,
            chunkIndex: this.currentChunkIndex,
            chunkNumber: this.chunks[this.currentChunkIndex].number,
            chunkContent: this.chunks[this.currentChunkIndex].content,
            ranking: ranking,
            timestamp: new Date().toISOString(),
            timeSpentOnChunk: this.getTimeSpentOnChunk()
        };
        
        this.evaluations.push(evaluation);
        
        // Store in localStorage for persistence
        this.saveToLocalStorage(evaluation);
        
        console.log('Ranking submitted:', evaluation);
        
        // Show success modal
        this.showSuccessModal();
    }

    getTimeSpentOnChunk() {
        // Track time spent on current chunk (basic implementation)
        if (!this.chunkStartTime) {
            this.chunkStartTime = Date.now();
        }
        return Date.now() - this.chunkStartTime;
    }

    saveToLocalStorage(evaluation) {
        try {
            // Get existing evaluations from localStorage
            const existingEvaluations = JSON.parse(localStorage.getItem('translation_evaluations') || '[]');
            
            // Add new evaluation
            existingEvaluations.push(evaluation);
            
            // Store back to localStorage
            localStorage.setItem('translation_evaluations', JSON.stringify(existingEvaluations));
            
            console.log('Evaluation saved to localStorage');
        } catch (error) {
            console.error('Error saving to localStorage:', error);
        }
    }

    skipChunk() {
        console.log(`Skipped chunk ${this.chunks[this.currentChunkIndex].number}`);
        this.nextChunk();
    }

    nextChunk() {
        this.hideSuccessModal();
        
        if (this.currentChunkIndex < this.chunks.length - 1) {
            this.currentChunkIndex++;
            this.displayCurrentChunk();
        } else {
            this.showCompletionMessage();
        }
    }

    showSuccessModal() {
        const modal = document.getElementById('success-modal');
        modal.classList.add('show');
    }

    hideSuccessModal() {
        const modal = document.getElementById('success-modal');
        modal.classList.remove('show');
    }

    showCompletionMessage() {
        const container = document.querySelector('.evaluation-area');
        container.innerHTML = `
            <div style="text-align: center; padding: 60px 20px; grid-column: 1 / -1;">
                <h2 style="font-size: 2rem; margin-bottom: 16px; color: #2d3748;">🎉 Evaluation Complete!</h2>
                <p style="font-size: 1.1rem; color: #718096; margin-bottom: 24px;">
                    Thank you for evaluating ${this.evaluations.length} chunks. 
                    Your expertise helps improve AI translation quality.
                </p>
                <button class="btn btn-primary" onclick="this.downloadResults()">
                    Download Results
                </button>
            </div>
        `;
    }

    downloadResults() {
        // Get all evaluations from localStorage for this session
        const allEvaluations = JSON.parse(localStorage.getItem('translation_evaluations') || '[]');
        const sessionEvaluations = allEvaluations.filter(evaluation => evaluation.sessionId === this.sessionId);
        
        const results = {
            sessionId: this.sessionId,
            expertCredentials: this.expertCredentials,
            completed_at: new Date().toISOString(),
            total_evaluations: sessionEvaluations.length,
            evaluations: sessionEvaluations,
            metadata: {
                chunksAvailable: this.chunks ? this.chunks.length : 0,
                evaluationVersion: '1.0',
                dataSource: 'galen_test_chunk_multi_model_claude_gemini_openai_20250929_150101.json'
            }
        };
        
        const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const expertName = this.expertCredentials.name.replace(/\s+/g, '_').toLowerCase();
        a.download = `evaluation_results_${expertName}_${this.sessionId}_${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }

    updateStats() {
        const completedCount = document.getElementById('completed-count');
        const remainingCount = document.getElementById('remaining-count');
        
        const completed = this.evaluations.length;
        const total = this.chunks.length;
        const remaining = total - this.currentChunkIndex - 1;
        
        completedCount.textContent = `${completed} completed`;
        remainingCount.textContent = `${remaining} remaining`;
    }

    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        overlay.style.display = 'none';
    }

    showError(message) {
        const overlay = document.getElementById('loading-overlay');
        overlay.innerHTML = `
            <div class="loading-spinner" style="border-top-color: #e53e3e;"></div>
            <p style="color: #e53e3e;">${message}</p>
            <button class="btn btn-primary" onclick="location.reload()" style="margin-top: 16px;">
                Retry
            </button>
        `;
    }
}

// Initialize the app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new TranslationEvaluator();
});

// Make downloadResults available globally
window.downloadResults = function() {
    if (window.evaluator) {
        window.evaluator.downloadResults();
    }
};
