// Scroll Animation Observer
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    }, { threshold: 0.1 });

    document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));

    // API Analyzer Execution
    async function analyzeReview() {
      const product = document.getElementById('productSelect').value;
      const ownerEmail = document.getElementById('ownerEmail').value.trim();
      const reviewText = document.getElementById('reviewInput').value.trim();

      if (!reviewText || !ownerEmail) return alert("Please fill all required fields!");

      const btn = document.getElementById('analyzeBtn');
      const results = document.getElementById('results');
      const alertBanner = document.getElementById('alertBanner');

      btn.disabled = true;
      btn.textContent = "Analyzing & Checking Alerts...";
      results.style.display = 'none';
      alertBanner.style.display = 'none';

      try {
        const response = await fetch('http://127.0.0.1:8000/api/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ product_name: product, review: reviewText, owner_email: ownerEmail })
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Analysis failed');

        document.getElementById('resProduct').textContent = data.product;
        const overallBadge = document.getElementById('overallBadge');
        overallBadge.textContent = data.overall_sentiment;
        overallBadge.className = `badge ${data.overall_sentiment.toLowerCase().slice(0, 3)}`;
        document.getElementById('overallScore').textContent = `Confidence: ${(data.overall_confidence * 100).toFixed(1)}%`;

        if (data.email_alert_sent) {
          document.getElementById('alertEmail').textContent = ownerEmail;
          alertBanner.style.display = 'block';
        }

        const container = document.getElementById('aspectsContainer');
        container.innerHTML = '';
        if (data.aspects.length === 0) {
          container.innerHTML = '<p style="color: var(--text-muted); grid-column: 1/-1;">No explicit product aspects detected.</p>';
        } else {
          data.aspects.forEach(item => {
            const card = document.createElement('div');
            card.className = 'aspect-card';
            const sentimentClass = item.sentiment.toLowerCase().slice(0, 3);
            card.innerHTML = `
              <div>
                <div style="font-weight:600">${item.aspect}</div>
                <div style="font-size:0.75rem; color:var(--text-muted);">${(item.confidence * 100).toFixed(0)}% Match</div>
              </div>
              <span class="badge ${sentimentClass}">${item.sentiment}</span>
            `;
            container.appendChild(card);
          });
        }

        results.style.display = 'block';
      } catch (err) {
        alert("Error: " + err.message);
      } finally {
        btn.disabled = false;
        btn.textContent = "Submit & Analyze Feedback";
      }
    }