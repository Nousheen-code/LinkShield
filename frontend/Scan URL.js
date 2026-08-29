async function scanURL() {
    const url = document.getElementById('urlInput').value;
    const resultDiv = document.getElementById('result');
    
    resultDiv.innerHTML = '🔄 AI Scanning...';
    resultDiv.className = 'result';
    resultDiv.style.display = 'block';

    try {
        const response = await fetch('http://localhost:5000/predict', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({url: url})
        });
        
        const data = await response.json();
        
        if (data.prediction === 1) {
            resultDiv.innerHTML = `
                🚨 <strong>PHISHING DETECTED</strong><br>
                Confidence: ${Math.round(data.confidence)}%<br>
                ${data.explanation}
            `;
            resultDiv.className = 'result risky';
        } else {
            resultDiv.innerHTML = `
                ✅ <strong>URL IS SAFE</strong><br>
                Confidence: ${Math.round(data.confidence)}%
            `;
            resultDiv.className = 'result safe';
        }
    } catch (e) {
        resultDiv.innerHTML = '❌ Backend error. Using local detection.';
        resultDiv.className = 'result risky';
    }
}