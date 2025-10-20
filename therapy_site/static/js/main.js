// Main JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add loading animation to cards
    const cards = document.querySelectorAll('.ai-optimized-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
});

// Communication analysis function
function analyzeCommunication() {
    const challengeText = document.querySelector('textarea').value;
    const feedbackDiv = document.getElementById('communication-feedback');

    if (!challengeText.trim()) {
        feedbackDiv.innerHTML = '<p class="text-warning">Please describe a communication challenge first.</p>';
        feedbackDiv.style.display = 'block';
        return;
    }

    // Simulate AI analysis
    feedbackDiv.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Analyzing...</span>
            </div>
            <p class="mt-2">AI is analyzing your communication pattern...</p>
        </div>
    `;
    feedbackDiv.style.display = 'block';

    // Simulate API call to AI backend
    setTimeout(() => {
        const responses = [
            "Try using 'I feel' statements instead of 'You always' language.",
            "Consider validating their perspective before sharing your own.",
            "Practice the 3-second pause before responding to emotional topics.",
            "Schedule a specific time to discuss this when both are calm.",
            "Focus on the underlying need rather than the surface complaint."
        ];

        const randomResponse = responses[Math.floor(Math.random() * responses.length)];

        feedbackDiv.innerHTML = `
            <h6><i class="fas fa-robot text-primary me-2"></i>AI Communication Coach Says:</h6>
            <p class="mb-2">"${randomResponse}"</p>
            <small class="text-muted">Based on Gottman Method and Nonviolent Communication principles</small>
        `;
    }, 2000);
}