document.addEventListener('DOMContentLoaded', function() {
    const eventForm = document.getElementById('event-form');
    const calendarElement = document.getElementById('calendar');

    const calendar = new FullCalendar.Calendar(calendarElement, {
        initialView: 'dayGridMonth',
        events: '/api/events',
        dateClick: function(info) {
            openEventModal(info.dateStr);
        }
    });

    calendar.render();

    if (eventForm) {
        eventForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(eventForm);
            submitEvent(formData);
        });
    }

    function openEventModal(date) {
        const modal = document.getElementById('event-modal');
        modal.style.display = 'block';
        document.getElementById('event-date').value = date;
    }

    function submitEvent(formData) {
        fetch('/api/events', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            calendar.addEvent(data);
            closeEventModal();
        })
        .catch(error => console.error('Error:', error));
    }

    function closeEventModal() {
        const modal = document.getElementById('event-modal');
        modal.style.display = 'none';
        eventForm.reset();
    }
});
