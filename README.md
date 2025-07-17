# School Management System (SMS)

A comprehensive solution for managing educational institutions, providing tools for administrators, teachers, students, and parents.

## Overview

The School Management System is a full-stack web application designed to streamline the administrative and academic processes of educational institutions. It offers a suite of modules for managing users, students, classes, attendance, examinations, and more.

## Architecture

The system follows a modular architecture with three primary components:
- **User Module** - Authentication and user management
- **Admin Module** - Administrative functions and school operations
- **Student Module** - Student-related data and activities

Each module connects to a centralized database service layer.

## Features

- **User Management**: Authentication, authorization, and role-based access control
- **Admin Dashboard**: School settings, teacher management, and class configuration
- **Student Management**: Profiles, attendance, grades, and performance tracking
- **Course Management**: Curriculum planning, timetable creation, and resource allocation
- **Communication**: Parent-teacher communication and notifications
- **Reporting**: Comprehensive reporting and analytics

## Technology Stack

### Backend
- Python 3.11+
- FastAPI
- PostgreSQL
- SQLAlchemy ORM
- JWT Authentication

### Frontend
- React with TypeScript
- Material-UI
- Redux for state management
- Axios for API communication

### DevOps
- Docker and Docker Compose
- GitHub Actions for CI/CD
- Pytest and Jest for testing

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Git
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/sms.git
   cd sms
   ```

2. Create an environment file:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. Start the development environment:
   ```bash
   docker-compose up -d
   ```

4. Access the application:
   - Backend API: http://localhost:8000
   - Frontend: http://localhost:3000
   - API Documentation: http://localhost:8000/docs

### Without Docker

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## Development

### Project Structure
For detailed information about the project structure and architecture, please refer to the [PLANNING.md](./PLANNING.md) file.

### Task Tracking
For current sprint tasks and backlog, please refer to the [TASK.md](./TASK.md) file.

## Testing

### Running Backend Tests
```bash
cd backend
pytest
```

### Running Frontend Tests
```bash
cd frontend
npm test
```

## Deployment

### Staging Environment
```bash
docker-compose -f docker-compose.staging.yml up -d
```

### Production Environment
Please refer to the deployment documentation in the `docs/deployment.md` file.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FastAPI for the amazing backend framework
- React community for the frontend tools and libraries
- All contributors who have helped shape this project 