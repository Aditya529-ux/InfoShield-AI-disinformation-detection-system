/**
 * InfoShield Client Application
 * Handles auto-hover sidebar, dual inputs, synchronized split-stage sliding drawer,
 * 6-category 2×3 red-teaming arena, majority-vote community feedback, and
 * user_feedback dataset memory management on localhost.
 */

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initTabs();
    initDualInputs();
    initSamplePresets();
    loadStats();
    loadRedTeamCategories();
    setupPredictionHandler();
    setupFeedbackHandler();
});

// Current active prediction state
let currentPredictionState = null;
let allRedTeamCategories = [];
let activeCategory = null;

/* ----------------- 1. Theme Management (Light Base + Dark Mode Switch) ----------------- */
function initTheme() {
    const themeBtn = document.getElementById('theme-toggle-btn');
    const themeIcon = document.getElementById('theme-icon');
    const themeText = document.getElementById('theme-text');

    const savedTheme = localStorage.getItem('infoshield_theme') || 'light';
    applyTheme(savedTheme);

    themeBtn.addEventListener('click', () => {
        const isDark = document.documentElement.classList.contains('dark-theme');
        const newTheme = isDark ? 'light' : 'dark';
        applyTheme(newTheme);
        localStorage.setItem('infoshield_theme', newTheme);
    });

    function applyTheme(theme) {
        if (theme === 'dark') {
            document.documentElement.classList.add('dark-theme');
            themeIcon.textContent = '☀️';
            if (themeText) themeText.textContent = 'Light Mode';
        } else {
            document.documentElement.classList.remove('dark-theme');
            themeIcon.textContent = '🌙';
            if (themeText) themeText.textContent = 'Dark Mode';
        }
    }
}

/* ----------------- 2. Tab Navigation ----------------- */
function initTabs() {
    const tabButtons = document.querySelectorAll('.nav-item-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');

            tabButtons.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            const targetContent = document.getElementById(targetTab);
            if (targetContent) targetContent.classList.add('active');

            if (targetTab === 'stats-tab') {
                loadHistoryAndFeedbacks();
            }
        });
    });
}

/* ----------------- 3. Dual Inputs (Headline + Article Body) ----------------- */
function initDualInputs() {
    const headlineInput = document.getElementById('headline-input');
    const articleInput = document.getElementById('article-input');
    const charCounter = document.getElementById('char-counter');
    const modeBadge = document.getElementById('input-mode-badge');
    const clearBtn = document.getElementById('clear-btn');

    function updateCountersAndMode() {
        const hText = headlineInput.value.trim();
        const aText = articleInput.value.trim();
        const totalChars = (headlineInput.value.length + articleInput.value.length);
        charCounter.textContent = `${totalChars} total chars`;

        if (hText && aText) {
            modeBadge.textContent = '⚡ Ready: Headline + Article';
            modeBadge.style.color = 'var(--primary)';
        } else if (hText) {
            modeBadge.textContent = '📰 Ready: Headline Only';
            modeBadge.style.color = '#8b5cf6';
        } else if (aText) {
            modeBadge.textContent = '📄 Ready: Article Body Only';
            modeBadge.style.color = '#0284c7';
        } else {
            modeBadge.textContent = '⚡ Dual-Input Scanner';
            modeBadge.style.color = 'var(--primary)';
        }
    }

    headlineInput.addEventListener('input', updateCountersAndMode);
    articleInput.addEventListener('input', updateCountersAndMode);

    // Ctrl+Enter shortcut
    [headlineInput, articleInput].forEach(inp => {
        inp.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                document.getElementById('analyze-btn').click();
            }
        });
    });

    // Clear Button: Clears inputs, closes sliding drawer, and centers stage
    clearBtn.addEventListener('click', () => {
        headlineInput.value = '';
        articleInput.value = '';
        updateCountersAndMode();
        closeSlidingDrawer();
        headlineInput.focus();
    });
}

/* ----------------- 4. Sample Presets ----------------- */
const SAMPLE_PRESETS = {
    conspiracy: {
        headline: "Big Pharma Conceals Natural Cancer Cure to Protect Multi-Billion Dollar Profits",
        article: "Whistleblower doctors expose how big pharmaceutical corporations secretly concealed a 100 percent natural herbal cure for cancer to protect billions in chemotherapy revenues."
    },
    official: {
        headline: "Bureau of Labor Statistics Releases Comprehensive December Employment Situation Report",
        article: "Total nonfarm payroll employment increased by 216,000 in December, and the unemployment rate was unchanged at 3.7 percent, the U.S. Bureau of Labor Statistics reported."
    },
    weather: {
        headline: "Secret Military Base Weaponizing 5G Frequencies to Induce Severe Earthquakes and Hurricanes",
        article: "Whistleblower transmissions report that secret military antennas are generating artificial hurricanes and earthquakes using 5G frequencies to manipulate global food supplies."
    },
    space: {
        headline: "NASA's James Webb Space Telescope Delivers Deepest Infrared Image of Distant Early Universe",
        article: "NASA's James Webb Space Telescope has produced the deepest and sharpest infrared image of the distant universe to date, capturing thousands of galaxies formed billions of years ago."
    },
    politics: {
        headline: "Local Taxes Skyrocket to Unprecedented Historic Highs Under Incumbent Administration",
        article: "During my opponent's term in office, local taxes surged by unprecedented historic levels, leaving millions of hardworking families completely bankrupt and destitute."
    }
};

function initSamplePresets() {
    const chips = document.querySelectorAll('.chip-btn[data-preset]');
    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            const key = chip.getAttribute('data-preset');
            const data = SAMPLE_PRESETS[key];
            if (data) {
                document.getElementById('headline-input').value = data.headline;
                document.getElementById('article-input').value = data.article;
                document.getElementById('headline-input').dispatchEvent(new Event('input'));
                document.getElementById('analyze-btn').click();
            }
        });
    });
}

/* ----------------- 5. Synchronized Split Prediction & Sliding Results ----------------- */
function setupPredictionHandler() {
    const analyzeBtn = document.getElementById('analyze-btn');
    const closeDrawerBtn = document.getElementById('close-drawer-btn');
    const emojiElement = document.getElementById('verdict-emoji');

    analyzeBtn.addEventListener('click', triggerAnalysis);
    closeDrawerBtn.addEventListener('click', closeSlidingDrawer);

    // Interactive Emoji Click Reaction
    if (emojiElement) {
        emojiElement.addEventListener('click', () => {
            emojiElement.style.animation = 'none';
            void emojiElement.offsetWidth;
            emojiElement.style.animation = 'emojiPop 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
            const isFake = currentPredictionState && currentPredictionState.prediction === 1;
            showToast(isFake ? '👎 Classified as Disinformation / False News' : '👍 Verified as Reliable / Credible News', isFake ? 'danger' : 'success');
        });
    }

    async function triggerAnalysis() {
        const headline = document.getElementById('headline-input').value.trim();
        const article = document.getElementById('article-input').value.trim();

        if (!headline && !article) {
            showToast('Please enter a headline, an article body, or both.', 'warning');
            return;
        }

        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<span class="pulse-dot"></span> Analyzing & Explaining...';

        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ headline, article })
            });

            if (!response.ok) {
                throw new Error(await response.text());
            }

            const data = await response.json();
            currentPredictionState = data;
            renderSlidingResults(data);
            showToast('Analysis complete: results aligned!', 'success');
        } catch (err) {
            console.error(err);
            showToast(`Analysis Error: ${err.message}`, 'danger');
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = '<span>🔍</span> Analyze Authenticity & Explain';
        }
    }
}

function renderSlidingResults(data) {
    const stage = document.getElementById('scanner-stage');
    // Synchronously shift the input left and slide the analysis drawer in from the right
    stage.classList.add('analyzing');

    const isFake = data.prediction === 1;
    const banner = document.getElementById('verdict-banner');
    banner.className = `verdict-banner ${isFake ? 'fake' : 'reliable'}`;

    // Interactive Hero Emoji: Green Thumbs Up for reliable, Red Thumbs Down for fake
    const emoji = document.getElementById('verdict-emoji');
    emoji.textContent = isFake ? '👎' : '👍';
    emoji.title = isFake ? 'Red Thumbs Down: False / Misleading' : 'Green Thumbs Up: Reliable / Credible';
    emoji.style.animation = 'none';
    void emoji.offsetWidth;
    emoji.style.animation = 'emojiPop 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275)';

    // Verdict label & Confidence
    const label = document.getElementById('verdict-label');
    label.textContent = isFake ? 'Fake / Disinformation' : 'Reliable / Credible News';

    const confBadge = document.getElementById('verdict-confidence-badge');
    const totalVotes = (data.fake_votes || 0) + (data.reliable_votes || 0);
    const isCommunity = data.is_memory_recall && totalVotes > 0;

    if (isCommunity && data.verdict_source === 'majority_user_vote') {
        confBadge.textContent = `🌐 Community Verdict (${totalVotes} real-world vote${totalVotes !== 1 ? 's' : ''})`;
        confBadge.style.background = isFake ? 'rgba(239,68,68,0.12)' : 'rgba(34,197,94,0.12)';
        confBadge.style.color = isFake ? 'var(--danger)' : 'var(--success)';
        confBadge.style.border = `1.5px solid ${isFake ? 'var(--danger)' : 'var(--success)'}`;
        confBadge.style.borderRadius = '8px';
        confBadge.style.padding = '3px 10px';
        confBadge.style.fontWeight = '700';
    } else if (isCommunity && data.verdict_source === 'tie_fallback_ml') {
        confBadge.textContent = `⚖️ Community Tie — ML Fallback (${totalVotes} vote${totalVotes !== 1 ? 's' : ''})`;
        confBadge.style.background = 'rgba(234,179,8,0.12)';
        confBadge.style.color = '#b45309';
        confBadge.style.border = '1.5px solid #fbbf24';
        confBadge.style.borderRadius = '8px';
        confBadge.style.padding = '3px 10px';
        confBadge.style.fontWeight = '700';
    } else {
        confBadge.textContent = `${(data.confidence * 100).toFixed(1)}% Confidence (${data.risk_level})`;
        confBadge.style = '';
    }

    const scopeBadge = document.getElementById('verdict-scope-badge');
    let scopeText = '';
    if (isCommunity && data.verdict_source === 'majority_user_vote') {
        const fv = data.fake_votes || 0;
        const rv = data.reliable_votes || 0;
        scopeText = `👥 Majority Vote: ${fv} Fake vs ${rv} Reliable`;
        scopeBadge.style.color = '#8b5cf6';
        scopeBadge.style.fontWeight = '700';
    } else if (isCommunity && data.verdict_source === 'tie_fallback_ml') {
        scopeText = `⚖️ Tied (${data.fake_votes || 0}–${data.reliable_votes || 0}) — ML decides`;
        scopeBadge.style.color = '#b45309';
        scopeBadge.style.fontWeight = '700';
    } else if (data.is_memory_recall) {
        scopeText = '🧠 Recalled from user_feedback Dataset';
        scopeBadge.style.color = '#8b5cf6';
        scopeBadge.style.fontWeight = '700';
    } else if (data.input_type === 'both') {
        scopeText = 'Evaluated: Headline + Article Body Combined';
        scopeBadge.style.color = 'var(--text-muted)';
        scopeBadge.style.fontWeight = '';
    } else if (data.input_type === 'headline_only') {
        scopeText = 'Evaluated: Headline Only';
        scopeBadge.style.color = 'var(--text-muted)';
        scopeBadge.style.fontWeight = '';
    } else {
        scopeText = 'Evaluated: Article Body Only';
        scopeBadge.style.color = 'var(--text-muted)';
        scopeBadge.style.fontWeight = '';
    }
    scopeBadge.textContent = scopeText;

    // Community Vote Bar (shown only when majority-vote recall active)
    renderCommunityVoteBar(data);

    // Probability Meters
    const relPct = (data.probabilities.reliable * 100).toFixed(1);
    const fakePct = (data.probabilities.fake * 100).toFixed(1);
    document.getElementById('prob-rel-val').textContent = `${relPct}%`;
    document.getElementById('prob-fake-val').textContent = `${fakePct}%`;
    document.getElementById('meter-fill-reliable').style.width = `${relPct}%`;
    document.getElementById('meter-fill-fake').style.width = `${fakePct}%`;

    // Plain-English Rationale
    document.getElementById('rationale-text').textContent = data.explanation.rationale;

    // Token Attribution Visualizer
    const tokenCloud = document.getElementById('token-cloud');
    tokenCloud.innerHTML = '';
    const tokens = data.explanation.all_token_attributions || [];
    if (tokens.length === 0) {
        tokenCloud.innerHTML = '<span style="font-size:12.5px; color:var(--text-muted);">No dominant lexical tokens; classified by baseline linguistic pattern.</span>';
    } else {
        tokens.forEach(tok => {
            const pill = document.createElement('span');
            pill.className = `token-pill ${tok.category === 'fake_signal' ? 'fake' : 'reliable'}`;
            const polaritySymbol = tok.impact > 0 ? '▲ Fake' : '▼ Real';
            pill.innerHTML = `<strong>${escapeHtml(tok.term)}</strong> <span>(${polaritySymbol} ${tok.abs_impact.toFixed(3)})</span>`;
            pill.title = `Weight: ${tok.weight} | TF-IDF: ${tok.tfidf}`;
            tokenCloud.appendChild(pill);
        });
    }

    // Reset Feedback Drawer
    resetFeedbackDrawer(data);
}

function closeSlidingDrawer() {
    const stage = document.getElementById('scanner-stage');
    // Smoothly slides drawer off-screen and shifts input panel back to center
    stage.classList.remove('analyzing');
}

/* ----------------- Community Vote Bar Renderer ----------------- */
function renderCommunityVoteBar(data) {
    // Remove any old vote bar first
    const existing = document.getElementById('community-vote-bar');
    if (existing) existing.remove();

    const fv = data.fake_votes || 0;
    const rv = data.reliable_votes || 0;
    const total = fv + rv;
    const isCommunity = data.is_memory_recall && total > 0;
    if (!isCommunity) return;

    const fakePct = total > 0 ? Math.round((fv / total) * 100) : 0;
    const reliPct = total > 0 ? Math.round((rv / total) * 100) : 0;

    let sourceBadge = '';
    if (data.verdict_source === 'majority_user_vote') {
        const winner = fv > rv ? 'Fake' : 'Reliable';
        sourceBadge = `<span class="vote-source-badge majority">👥 Majority Vote (${fv}–${rv}) → ${winner}</span>`;
    } else if (data.verdict_source === 'tie_fallback_ml') {
        sourceBadge = `<span class="vote-source-badge tie">⚖️ Tied ${fv}–${rv} · ML Model Decides</span>`;
    }

    const bar = document.createElement('div');
    bar.id = 'community-vote-bar';
    bar.className = 'community-vote-bar';
    bar.innerHTML = `
        <div class="cvb-header">
            🗳️ <strong>Real-World Community Feedback</strong> — ${total} user vote${total !== 1 ? 's' : ''} recorded
            ${sourceBadge}
        </div>
        <div class="cvb-tracks">
            <div class="cvb-track">
                <span class="cvb-label fake-label">👎 Fake — ${fv} vote${fv !== 1 ? 's' : ''} (${fakePct}%)</span>
                <div class="cvb-bar-bg">
                    <div class="cvb-bar-fill fake-fill" style="width:${fakePct}%"></div>
                </div>
            </div>
            <div class="cvb-track">
                <span class="cvb-label reliable-label">👍 Reliable — ${rv} vote${rv !== 1 ? 's' : ''} (${reliPct}%)</span>
                <div class="cvb-bar-bg">
                    <div class="cvb-bar-fill reliable-fill" style="width:${reliPct}%"></div>
                </div>
            </div>
        </div>
    `;

    // Insert the bar just above the probability meters section
    const rationale = document.getElementById('rationale-text');
    if (rationale && rationale.parentNode) {
        rationale.parentNode.insertBefore(bar, rationale);
    }
}

/* ----------------- 6. Human-in-the-Loop Feedback & Dataset Memory ----------------- */
let selectedUserLabel = null;
let selectedUserAction = 'agree';

function resetFeedbackDrawer(data) {
    const agreeBtn = document.getElementById('fb-agree-btn');
    const disRealBtn = document.getElementById('fb-disagree-real-btn');
    const disFakeBtn = document.getElementById('fb-disagree-fake-btn');
    const notesInput = document.getElementById('fb-notes');

    notesInput.value = '';
    [agreeBtn, disRealBtn, disFakeBtn].forEach(b => b.classList.remove('selected'));

    agreeBtn.classList.add('selected');
    selectedUserAction = 'agree';
    selectedUserLabel = data.prediction;
}

function setupFeedbackHandler() {
    const agreeBtn = document.getElementById('fb-agree-btn');
    const disRealBtn = document.getElementById('fb-disagree-real-btn');
    const disFakeBtn = document.getElementById('fb-disagree-fake-btn');
    const submitBtn = document.getElementById('fb-submit-btn');
    const notesInput = document.getElementById('fb-notes');

    agreeBtn.addEventListener('click', () => {
        selectFeedbackOption(agreeBtn, 'agree', currentPredictionState.prediction);
    });

    disRealBtn.addEventListener('click', () => {
        selectFeedbackOption(disRealBtn, 'disagree', 0); // Correct to Reliable
    });

    disFakeBtn.addEventListener('click', () => {
        selectFeedbackOption(disFakeBtn, 'disagree', 1); // Correct to Fake
    });

    function selectFeedbackOption(btn, action, label) {
        [agreeBtn, disRealBtn, disFakeBtn].forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        selectedUserAction = action;
        selectedUserLabel = label;
    }

    submitBtn.addEventListener('click', async () => {
        if (!currentPredictionState) return;

        submitBtn.disabled = true;
        submitBtn.innerHTML = 'Updating Localhost Dataset & Memory...';

        try {
            const headline = currentPredictionState.headline || '';
            const article = currentPredictionState.article || '';
            const payload = {
                headline: headline,
                article: article,
                query_id: currentPredictionState.query_id || null,
                user_label: selectedUserLabel,
                user_action: selectedUserAction,
                source_note: notesInput.value.trim()
            };

            const response = await fetch('/api/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(await response.text());
            }

            const result = await response.json();
            const fv = result.fake_votes || 0;
            const rv = result.reliable_votes || 0;
            const total = result.total_votes || fv + rv;
            const mvText = result.majority_verdict || result.remembered_verdict;
            const sourceText = result.verdict_source === 'tie_fallback_ml'
                ? '⚖️ Tied — ML fallback decides'
                : `👥 Majority: ${fv} Fake vs ${rv} Reliable`;

            showToast(`✅ Vote recorded! ${sourceText} → ${mvText}`, 'success');
            loadStats();

            // Update community vote bar in real-time
            const updatedData = Object.assign({}, currentPredictionState, {
                fake_votes: fv,
                reliable_votes: rv,
                is_memory_recall: true,
                verdict_source: result.verdict_source || 'majority_user_vote',
                total_community_feedbacks: total
            });
            renderCommunityVoteBar(updatedData);

            // Show rationale update
            const newReliable = (result.probabilities.reliable * 100).toFixed(1);
            const newFake = (result.probabilities.fake * 100).toFixed(1);
            document.getElementById('rationale-text').innerHTML = `
                ${escapeHtml(currentPredictionState.explanation.rationale)}<br><br>
                <strong style="color:var(--primary);">[Community Vote Saved]:</strong> 
                Your feedback has been permanently recorded on localhost. 
                Community now shows <strong>${fv} Fake vote(s)</strong> vs <strong>${rv} Reliable vote(s)</strong>. 
                Majority verdict: <strong>${escapeHtml(mvText)}</strong>. 
                If queried again, InfoShield will show this community consensus result!
                Model online probabilities: <strong>Reliable: ${newReliable}%</strong>, <strong>Fake: ${newFake}%</strong>.
            `;
        } catch (err) {
            console.error(err);
            showToast(`Feedback failed: ${err.message}`, 'danger');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Teach Model & Save to user_feedback Dataset';
        }
    });
}

/* ----------------- 7. 6-Category Red-Teaming Arena (3x2 Grid) ----------------- */
async function loadRedTeamCategories() {
    const grid = document.getElementById('redteam-category-grid');
    if (!grid) return;

    try {
        const res = await fetch('/api/redteam/categories');
        if (!res.ok) return;
        allRedTeamCategories = await res.json();
        renderCategoryGrid(allRedTeamCategories);
        setupCategoryBackAndFilter();
    } catch (e) {
        console.error("Failed to load redteam categories:", e);
    }
}

function renderCategoryGrid(categories) {
    const grid = document.getElementById('redteam-category-grid');
    const detailView = document.getElementById('redteam-detail-view');
    const breadcrumb = document.getElementById('redteam-breadcrumb');

    grid.style.display = 'grid';
    detailView.style.display = 'none';
    breadcrumb.style.display = 'none';
    grid.innerHTML = '';

    categories.forEach(cat => {
        const card = document.createElement('div');
        card.className = 'category-card';
        card.innerHTML = `
            <div>
                <div class="category-icon">${cat.icon}</div>
                <h3 class="category-card-title">${escapeHtml(cat.title)}</h3>
                <p class="category-card-desc">${escapeHtml(cat.description)}</p>
            </div>
            <div class="category-card-footer">
                <span class="category-case-badge">${cat.examples.length} Verified Cases</span>
                <span class="category-explore-link">Explore Cases ➔</span>
            </div>
        `;

        card.addEventListener('click', () => {
            openCategoryDetail(cat);
        });

        grid.appendChild(card);
    });
}

function openCategoryDetail(category) {
    activeCategory = category;
    const grid = document.getElementById('redteam-category-grid');
    const detailView = document.getElementById('redteam-detail-view');
    const breadcrumb = document.getElementById('redteam-breadcrumb');

    grid.style.display = 'none';
    detailView.style.display = 'block';
    breadcrumb.style.display = 'block';

    document.getElementById('current-category-title').textContent = `${category.icon} ${category.title}`;
    document.getElementById('current-category-desc').textContent = `${category.description} (${category.examples.length} total curated benchmark examples)`;

    // Reset filter
    document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
    document.querySelector('.filter-pill[data-filter="all"]').classList.add('active');

    renderCategoryExamples(category.examples);
}

function renderCategoryExamples(examples) {
    const container = document.getElementById('redteam-examples-container');
    container.innerHTML = '';

    examples.forEach(item => {
        const div = document.createElement('div');
        div.className = 'redteam-item';
        const isFake = item.expected.toLowerCase().includes('fake');
        const badgeClass = isFake ? 'fake' : 'reliable';
        const badgeIcon = isFake ? '👎' : '👍';

        div.innerHTML = `
            <div style="flex: 1;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                    <span class="redteam-tag" style="background:var(--primary-light); color:var(--primary);">${escapeHtml(item.tag)}</span>
                    <span class="badge-groundtruth ${badgeClass}">${badgeIcon} Ground Truth: ${escapeHtml(item.expected)}</span>
                </div>
                <div class="redteam-headline">${escapeHtml(item.headline)}</div>
                <div class="redteam-text">"${escapeHtml(item.article)}"</div>
            </div>
            <button class="chip-btn test-sample-btn" style="white-space: nowrap; font-weight:700; padding:10px 16px; background:var(--primary-light); color:var(--primary); border-color:var(--border-focus);">
                Test in Scanner ➔
            </button>
        `;

        div.querySelector('.test-sample-btn').addEventListener('click', () => {
            document.getElementById('headline-input').value = item.headline;
            document.getElementById('article-input').value = item.article;
            document.getElementById('headline-input').dispatchEvent(new Event('input'));
            document.querySelector('[data-tab="scanner-tab"]').click();
            document.getElementById('analyze-btn').click();
        });

        container.appendChild(div);
    });
}

function setupCategoryBackAndFilter() {
    const backBtn = document.getElementById('back-to-categories-btn');
    backBtn.addEventListener('click', () => {
        renderCategoryGrid(allRedTeamCategories);
    });

    const filterPills = document.querySelectorAll('.filter-pill');
    filterPills.forEach(pill => {
        pill.addEventListener('click', () => {
            filterPills.forEach(p => p.classList.remove('active'));
            pill.classList.add('active');

            const filter = pill.getAttribute('data-filter');
            if (!activeCategory) return;

            if (filter === 'all') {
                renderCategoryExamples(activeCategory.examples);
            } else {
                const filtered = activeCategory.examples.filter(e => e.expected.toLowerCase().includes(filter.toLowerCase()));
                renderCategoryExamples(filtered);
            }
        });
    });
}

/* ----------------- 8. Stats & Localhost Datasets Rendering ----------------- */
async function loadStats() {
    try {
        const res = await fetch('/api/stats');
        if (!res.ok) return;
        const stats = await res.json();

        const badgeText = document.querySelector('.sidebar-stats-text');
        if (badgeText) {
            const acc = (stats.test_accuracy * 100).toFixed(1);
            badgeText.textContent = `Model Active (${acc}%)`;
        }

        const metricAcc = document.getElementById('metric-accuracy');
        const metricSamples = document.getElementById('metric-samples');
        const metricFeedback = document.getElementById('metric-feedback');
        const metricVocab = document.getElementById('metric-vocab');

        if (metricAcc) metricAcc.textContent = `${(stats.test_accuracy * 100).toFixed(1)}%`;
        if (metricSamples) metricSamples.textContent = (stats.base_samples || 31421).toLocaleString();
        if (metricFeedback) metricFeedback.textContent = (stats.user_feedback_stats?.total_queries_in_dataset || stats.feedback_samples_learned || 0);
        if (metricVocab) metricVocab.textContent = (stats.vocabulary_size || 30000).toLocaleString();
    } catch (e) {
        console.error("Failed to load stats:", e);
    }
}

async function loadHistoryAndFeedbacks() {
    const userFeedbackContainer = document.getElementById('user-feedback-table-body');
    const historyContainer = document.getElementById('history-table-body');

    try {
        const [ufRes, histRes] = await Promise.all([
            fetch('/api/dataset/user_feedback'),
            fetch('/api/history?limit=15')
        ]);

        // 1. Render datasets/user_feedback.json table
        if (ufRes.ok && userFeedbackContainer) {
            const dataset = await ufRes.json();
            userFeedbackContainer.innerHTML = dataset.length ? '' : '<tr><td colspan="8" class="table-empty">No entries in datasets/user_feedback.json yet.</td></tr>';
            
            // Show most recent 12 entries
            dataset.slice(-12).reverse().forEach(entry => {
                const tr = document.createElement('tr');
                const isFake = entry.effective_label === 1;
                const fv = entry.fake_votes || 0;
                const rv = entry.reliable_votes || 0;
                const total = fv + rv;

                let sourceBadgeHtml = '';
                if (entry.verdict_source === 'majority_user_vote') {
                    sourceBadgeHtml = `<span class="token-pill fake" style="font-size:11px;">👥 Majority (${fv}F/${rv}R)</span>`;
                } else if (entry.verdict_source === 'tie_fallback_ml') {
                    sourceBadgeHtml = `<span class="token-pill" style="font-size:11px;background:#fef9c3;color:#b45309;">⚖️ Tie (${fv}–${rv})</span>`;
                } else {
                    sourceBadgeHtml = '<span class="token-pill" style="font-size:11px;background:var(--bg-subtle);">🤖 ML Model</span>';
                }

                const voteCell = total > 0
                    ? `<span style="color:var(--danger);font-weight:700;">👎${fv}</span> / <span style="color:var(--success);font-weight:700;">👍${rv}</span>`
                    : '<span style="color:var(--text-muted);font-size:11px;">No votes yet</span>';

                tr.innerHTML = `
                    <td style="font-weight:700;">#${entry.normalized_key ? entry.normalized_key.slice(0,6) : '—'}</td>
                    <td style="max-width:220px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${escapeHtml(entry.headline || entry.text)}</td>
                    <td><span class="token-pill ${entry.model_prediction === 1 ? 'fake' : 'reliable'}">${entry.predicted_verdict || (entry.model_prediction === 1 ? 'Fake' : 'Reliable')}</span></td>
                    <td>${voteCell}</td>
                    <td><span class="token-pill ${isFake ? 'fake' : 'reliable'}" style="font-weight:700;">${entry.effective_verdict}</span></td>
                    <td>${sourceBadgeHtml}</td>
                    <td style="font-size:11.5px; color:var(--text-muted);">${(entry.last_updated || entry.first_seen || '').slice(0, 19).replace('T', ' ')}</td>
                `;
                userFeedbackContainer.appendChild(tr);
            });
        }

        // 2. Render Prediction History Table
        if (histRes.ok && historyContainer) {
            const history = await histRes.json();
            historyContainer.innerHTML = history.length ? '' : '<tr><td colspan="6" class="table-empty">No queries logged yet.</td></tr>';
            history.forEach(h => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td style="max-width:220px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${escapeHtml(h.text)}</td>
                    <td style="max-width:180px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${escapeHtml(h.headline || '—')}</td>
                    <td><span class="token-pill ${h.prediction === 1 ? 'fake' : 'reliable'}">${h.effective_verdict || (h.prediction === 1 ? 'Fake' : 'Reliable')}</span></td>
                    <td>${(h.confidence * 100).toFixed(1)}%</td>
                    <td><span class="token-pill" style="font-size:11px; background:var(--bg-subtle);">${escapeHtml(h.feedback_status || 'Assumed Accurate')}</span></td>
                    <td style="font-size:11.5px; color:var(--text-muted);">${h.timestamp || 'Just now'}</td>
                `;
                historyContainer.appendChild(tr);
            });
        }
    } catch (e) {
        console.error("Failed to load tables:", e);
    }
}

/* ----------------- Toast Utility ----------------- */
function showToast(message, type = 'info') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'toast';
    const icon = type === 'success' ? '✅' : (type === 'danger' ? '❌' : (type === 'warning' ? '⚠️' : 'ℹ️'));
    toast.innerHTML = `<span>${icon}</span> <span>${escapeHtml(message)}</span>`;

    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}
