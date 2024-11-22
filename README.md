# DevCanvas - An Automated Software Analysis & Documentation Generator Tool

An innovative tool designed to streamline the process of generating software documentation. The application leverages modern web technologies to provide an intuitive user experience, offering automated generation of summaries, flowcharts, class diagrams, and sequence diagrams based on user-uploaded codebases.

---

## Features

- **User Authentication**
  - Secure registration, login, and logout functionalities.
  - Email-based account activation for enhanced security.
  
- **Documentation Generation**
  - Upload codebase directories and choose the required programming language and documentation type.
  - Generate and download documentation in PDF format.
  
- **History Management**
  - View and manage previously generated documentation for each user.

---

## Tech Stack

- **Backend**: Django  
- **Frontend**: React  

---

## Application Workflow

1. **User Registration**  
   - New users register by providing a unique username, email, and password.  
   - Upon registration, an activation email is sent to the user's email with a link to activate the account.  

2. **Login**  
   - Registered users log in using their credentials to access the dashboard.  

3. **Dashboard**  
   - **Home**: Overview and quick actions.  
   - **Upload**: Upload project directories, select programming language and documentation type, and generate documentation.  
   - **History**: View and download previously generated documentation.  

4. **Documentation Generation**  
   - Once documentation is generated, it is immediately available for download as a PDF.  
   - Uploaded codebases are automatically deleted after processing to ensure privacy.
  
  ---


## How to Run Locally

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/AnaghaARao/DevCanvas.git
   cd DevCanvas

## Setup Instructions

### Backend Setup

Follow these steps to set up and run the backend server:

1. **Install Dependencies**  
   Install the required Python packages by running:  
   ```bash
   cd backend
   pip install -r requirements.txt

2. **Apply Migrations**
   Set up the database schema by applying the migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
3. **Run the Server**
   Start the Django development server:
   ```bash
   Copy code
   python manage.py runserver

### Frontend Setup

Follow these steps to set up and run the frontend server for the project:

1. **Navigate to the Frontend Directory**  
   Open a terminal and move into the `frontend` folder:  
   ```bash
   cd frontend
2. **Install Dependencies**  
   Install the required npm packages:  
   ```bash
   npm install
3. **Run the Frontend Server**  
   Start the React development server with the following command:  
   ```bash
   npm run dev

---

## Access the Application

1. The backend API will be available at http://localhost:8000.
2. The frontend application will run at http://localhost:5173. Open this in your browser to use the application.
