# Campus Copilot

Campus Copilot is a comprehensive web-based platform designed to streamline campus event management and user administration. Built with Flask and integrated with modern cloud and AI services, it empowers students and administrators to efficiently organize, approve, and manage campus events, sync with Google Calendar, send email notifications, and handle user authentication and roles.

## Table of Contents
- [Project Title](#project-title)
- [Project Description](#project-description)
- [Technical Details](#technical-details)
- [Tech Stack Used](#tech-stack-used)
- [Key Features](#key-features)
- [Challenges Faced](#challenges-faced)
- [Future Scope](#future-scope)
- [Setup Instructions](#setup-instructions)
- [License](#license)

---

## Project Title
Campus Copilot

## Project Description
Campus Copilot is a campus event management system that allows users to create, approve, and manage events, sync with Google Calendar, send email notifications, and handle user authentication and roles. The platform integrates with Supabase for event storage and provides dashboards, notice boards, and admin tools for bulk actions and analytics. It also features an AI-powered assistant for answering campus-related queries.

## Technical Details

### Tech Stack Used
- **Backend:** Python (Flask)
- **Database:** SQLite (via SQLAlchemy), Supabase (cloud database)
- **Authentication:** Flask-Login
- **Scheduling:** APScheduler
- **Email:** SMTP integration
- **Calendar Sync:** Google Calendar API
- **Frontend:** HTML, CSS, JavaScript
- **AI Assistant:** Custom integration

_Add technology (e.g., React, Node.js) as needed._

## Key Features
- User authentication and role management (student/admin)
- Event creation, approval, and management
- Google Calendar sync for events
- Email notifications for upcoming events
- Notice board for campus updates
- Admin dashboard for bulk actions and analytics
- Export events and users as CSV
- AI-powered assistant for campus queries

_Add key feature as needed._

## Additional Information

### Challenges Faced
- Integrating multiple services (Supabase, Google Calendar, email)
- Ensuring secure authentication and role-based access
- Handling bulk operations and data export
- Managing asynchronous tasks (email scheduling)

_What challenges did you face during development?_

### Future Scope
- Mobile app integration
- Real-time notifications
- Advanced analytics and reporting
- More AI-powered features
- Integration with other campus systems

_What are your plans for future enhancements?_

## Setup Instructions

1. **Clone the repository:**
   ```sh
   git clone https://github.com/YOUR_USERNAME/campus-copilot.git
   cd campus-copilot
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Set up environment variables:**
   - Configure your Google Calendar API credentials.
   - Set your Flask secret key.
4. **Run the application:**
   ```sh
   python app.py
   ```
5. **Access the app:**
   - Open your browser and go to `http://localhost:5000`

## License
This project is licensed under the MIT License.

---

For more details, see the code and documentation in this repository. Contributions and suggestions are welcome!
