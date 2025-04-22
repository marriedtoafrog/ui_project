// Main JavaScript for Food Labeling application

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Track time spent on each page
    const startTime = new Date();
    const pageType = $('body').data('page-type');
    const pageId = $('body').data('page-id');
    
    // Record visit data to console (in a real app, this would be sent to the server)
    console.log(`User visited ${pageType} page with ID: ${pageId} at ${startTime}`);
    
    // Handle quiz form submissions
    $('#quiz-form').on('submit', function() {
        const selectedOptions = [];
        
        $('input[name="answers"]:checked').each(function() {
            selectedOptions.push($(this).val());
        });
        
        // Simple validation - require at least one answer
        if (selectedOptions.length === 0) {
            alert('Please select at least one option before continuing.');
            return false;
        }
        
        // Store answer data in localStorage for backup
        const questionId = $(this).data('question-id');
        localStorage.setItem(`quiz_answer_${questionId}`, JSON.stringify(selectedOptions));
        
        // Visual feedback on submission
        $('#submit-answer').addClass('pulse').text('Submitting...');
        
        // This form will be submitted normally, the answer will be processed server-side
        return true;
    });
    
    // Add visual feedback when checkboxes are clicked
    $('.form-check-input').on('change', function() {
        if ($(this).is(':checked')) {
            $(this).closest('.form-check').addClass('bg-light');
        } else {
            $(this).closest('.form-check').removeClass('bg-light');
        }
    });
    
    // Record when user leaves the page
    $(window).on('beforeunload', function() {
        const endTime = new Date();
        const timeSpent = Math.round((endTime - startTime) / 1000);
        
        // In a real app, this would be sent to the server
        console.log(`User spent ${timeSpent} seconds on ${pageType} page with ID: ${pageId}`);
    });

    // Home page specific functionality
    if (pageType === 'home') {
        $('#start-button').on('click', function() {
            // Record when the user starts the learning process
            console.log('User started the learning process at ' + new Date());
            
            // Clear any previous quiz data from localStorage
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (key.startsWith('quiz_answer_')) {
                    localStorage.removeItem(key);
                }
            }
        });
    }
    
    // Learning page specific functionality
    if (pageType === 'learn') {
        const labelName = $('body').data('label-name');
        
        // Record specific label visit
        console.log(`User is learning about: ${labelName}`);
        
        // Highlight identifiers on hover
        $('.identifier-item').on('mouseenter', function() {
            const targetSelector = $(this).data('target');
            $(targetSelector).addClass('highlight-feature');
        }).on('mouseleave', function() {
            const targetSelector = $(this).data('target');
            $(targetSelector).removeClass('highlight-feature');
        });
    }
    
    // Quiz results page specific functionality
    if (pageType === 'results') {
        const score = $('body').data('score');
        
        // Record quiz completion
        console.log(`User completed quiz with score: ${score}%`);
        
        // Visual effects based on score
        if (score >= 80) {
            confetti({
                particleCount: 100,
                spread: 70,
                origin: { y: 0.6 }
            });
        }
    }
});

// Function to handle next/previous navigation with keyboard
$(document).keydown(function(e) {
    if (e.keyCode === 39) { // Right arrow key
        const nextButton = $('#next-button:not(:disabled)');
        if (nextButton.length) {
            window.location.href = nextButton.attr('href');
        }
    } else if (e.keyCode === 37) { // Left arrow key
        const prevButton = $('#prev-button:not(:disabled)');
        if (prevButton.length) {
            window.location.href = prevButton.attr('href');
        }
    }
});