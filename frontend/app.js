const API_URL = 'http://localhost:8000';

let selectedFile = null;

// File input change
document.getElementById('fileInput').addEventListener('change', function() {
    if (this.files[0]) {
        selectedFile = this.files[0];
        document.getElementById('fileName').textContent = 'Selected: ' + this.files[0].name;
        document.getElementById('analyseBtn').disabled = false;
    }
});

// Analyse button click
document.getElementById('analyseBtn').addEventListener('click', async function() {
    if (!selectedFile) {
        alert('Pehle PDF select karo!');
        return;
    }

    document.getElementById('loading').hidden = false;
    document.getElementById('results').hidden = true;
    document.getElementById('loadingMsg').textContent = 'AI processing...';

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const response = await fetch('http://localhost:8000/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        console.log('Response:', data);

        if (response.ok) {
            displayResults(data);
        } else {
            alert('Error: ' + JSON.stringify(data.detail));
        }
    } catch (err) {
        console.error(err);
        alert('Error: ' + err.message);
    } finally {
        document.getElementById('loading').hidden = true;
    }
});

function displayResults(data) {
    document.getElementById('results').hidden = false;
    document.getElementById('summaryBox').textContent = data.summary || 'No summary';
    document.getElementById('originalBox').textContent = data.original_text_preview || '';

    // Key points
    const kpEl = document.getElementById('keyPoints');
    kpEl.innerHTML = '';
    (data.key_points || []).forEach(pt => {
        const li = document.createElement('li');
        li.textContent = pt;
        kpEl.appendChild(li);
    });

    // Risk
    const risk = data.risk || {};
    document.getElementById('riskTitle').textContent = 'Risk Level: ' + (risk.level || 'Low');
    document.getElementById('riskDetail').textContent = 'Score: ' + ((risk.score || 0).toFixed(1)) + '%';
    const badge = document.getElementById('riskBadge');
    badge.textContent = risk.level || 'Low';
    badge.className = 'risk-badge ' + (risk.level || 'low').toLowerCase();

    // Entities
    const entRow = document.getElementById('entitiesRow');
    entRow.innerHTML = '';
    const ents = data.entities || {};
    const icons = { parties: '👤', dates: '📅', locations: '📍', organizations: '🏢', money: '💰' };
    Object.keys(ents).forEach(key => {
        if (ents[key] && ents[key].length > 0) {
            entRow.innerHTML += '<div class="entity-card"><span>' + (icons[key] || '📌') + '</span><strong>' + key + '</strong><p>' + ents[key].join(', ') + '</p></div>';
        }
    });

    // Clauses
    const grid = document.getElementById('clausesGrid');
    grid.innerHTML = '';
    (data.clauses || []).forEach(clause => {
        const color = clause.type === 'high_risk' ? '#e74c3c' : clause.type === 'medium_risk' ? '#f39c12' : '#27ae60';
        grid.innerHTML += '<div class="clause-card" style="border-left:4px solid ' + color + '"><span style="color:' + color + '">' + (clause.type || 'normal') + '</span><p>' + (clause.text || '') + '</p></div>';
    });

    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
}

function resetApp() {
    selectedFile = null;
    document.getElementById('fileName').textContent = '';
    document.getElementById('fileInput').value = '';
    document.getElementById('analyseBtn').disabled = true;
    document.getElementById('results').hidden = true;
    document.getElementById('uploadSection').scrollIntoView({ behavior: 'smooth' });
}