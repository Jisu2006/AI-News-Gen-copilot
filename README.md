# AI-NewsGen Copilot

## AI-Powered Digital Newspaper and News Drafting Platform

AI-NewsGen Copilot is a web-based digital newspaper platform that allows users to submit news incidents and uses Large Language Model (LLM) technology to generate a structured news draft.

The generated news is not published directly. It goes through an admin review and approval process before becoming publicly available.

The system is designed to support a complete workflow from news submission to AI-assisted drafting, admin verification, editing, approval, and publication.

---

## Project Overview

The main purpose of AI-NewsGen Copilot is to make the process of creating and managing digital news faster and more structured.

A user can submit information about an incident in the form of:

- Category
- Location
- Incident date and time
- Bullet points
- Additional description
- Image
- Video
- Source URL
- Supporting information

The AI system uses the submitted information to generate:

- News headline
- Subheading
- Summary
- Full news article
- Key facts
- Tags

The AI-generated content is stored as a draft and sent to the administrator for review.

The administrator can:

- Review the news
- Edit the AI-generated content
- Request additional information
- Approve the news
- Reject the news
- Publish the news

Only approved and published news becomes available on the public newspaper website.

---

## Main Objective

The objective of this project is to develop an AI-assisted digital news platform that combines:

- Web application development
- Database management
- AI/LLM-based content generation
- Role-based access control
- Admin moderation
- Secure news publishing workflow

## Key Features

### 1. User Authentication

- User registration with name, email, and password
- Secure password hashing
- User login and logout
- Session-based authentication
- Role-based access control

### 2. News Submission

Registered users can submit news incidents with:

- News category
- News title
- Location
- Incident date and time
- Bullet points
- Additional description
- Image upload
- Video upload
- Source URL
- Supporting information

### 3. AI-Powered News Generation

The system uses an LLM to generate a structured news draft from the information submitted by the user.

AI-generated content includes:

- Headline
- Subheading
- Summary
- News article
- Key facts
- Tags

The AI is instructed to use only the information provided by the user and avoid inventing unsupported facts.

### 4. Admin Review System

Administrators can manage submitted news through an admin dashboard.

Admin capabilities include:

- View submitted news
- Review AI-generated drafts
- Edit news content
- Request additional information
- Approve news
- Reject news
- Publish approved news
- Mark news as breaking
- Mark news as featured

### 5. Information Request & Regeneration

If the submitted information is insufficient, the administrator can request additional information from the user.

The user can provide the requested information, after which the AI can regenerate the news draft.

### 6. Public Digital Newspaper

Published news is available to public visitors without requiring login.

Public users can:

- Browse latest news
- View breaking news
- View featured news
- Browse news by category
- Search news
- Filter news
- View complete news articles

### 7. Audit Trail

Administrative actions are recorded in the database.

The audit trail helps track actions such as:

- News editing
- Information requests
- Approval
- Rejection
- Publication

### 8. Security Features

The application includes security measures such as:

- Password hashing
- Session-based authentication
- Role-based access control
- CSRF protection
- Input validation
- File upload validation
- SQLAlchemy-based database queries
- XSS protection through template auto-escaping
- Environment variables for sensitive configuration

## User & Admin Workflow

### User Workflow

The user workflow follows these steps:

1. User opens the public newspaper homepage.
2. User selects **Submit News**.
3. If the user is not logged in, the system redirects the user to the User Login page.
4. User registers an account if they do not already have one.
5. User logs into the system.
6. User opens the User Dashboard.
7. User submits news information through the news submission form.
8. The submitted information is stored in the database.
9. The system sends the submitted information to the AI/LLM service.
10. The AI generates a structured news draft.
11. The AI-generated draft is stored separately from the original user submission.
12. The news is sent to the administrator for review.
13. The user can track the current status of their submitted news.
14. If the administrator requests additional information, the user provides the required information.
15. The AI can regenerate the news draft using the updated information.
16. After administrator approval and publication, the news becomes available on the public newspaper website.

---

### Admin Workflow

The administrator workflow follows these steps:

1. Administrator opens the Admin Login page.
2. Administrator logs into the system using admin credentials.
3. Administrator opens the Admin Dashboard.
4. Administrator views news submitted by users.
5. Administrator reviews the AI-generated news draft.
6. Administrator can edit the generated content if required.
7. Administrator can request additional information from the user.
8. Administrator can approve the news.
9. Administrator can reject the news.
10. Approved news can be published by the administrator.
11. Published news becomes visible on the public newspaper website.
12. Administrative actions are recorded in the audit trail.

---

### News Status Workflow

The news submission follows a controlled status workflow:

```text
DRAFT
  ↓
SUBMITTED
  ↓
AI_PROCESSING
  ↓
AI_DRAFT
  ↓
PENDING_REVIEW
  ↓
┌───────────────────────┐
│                       │
↓                       ↓
APPROVED          NEEDS_INFORMATION
  ↓                       ↓
PUBLISHED          User Provides Information
                          ↓
                    AI Regeneration
                          ↓
                    PENDING_REVIEW

PENDING_REVIEW
  ↓
REJECTED

## AI / LLM Integration

AI-NewsGen Copilot uses a Large Language Model (LLM) to assist in generating structured news drafts from user-submitted information.

### AI Generation Process

The AI workflow is:

1. User submits news information.
2. The submitted information is collected by the Flask backend.
3. The backend prepares the information using a predefined news-generation prompt.
4. The information is sent to the configured LLM service.
5. The LLM generates a structured news draft.
6. The generated content is parsed by the application.
7. The AI-generated content is stored in the database.
8. The generated draft is sent to the administrator for review.
9. The administrator can edit, approve, reject, or request additional information.
10. Only approved content can be published.

### AI-Generated Fields

The LLM generates the following fields:

- Headline
- Subheading
- Summary
- News Article
- Key Facts
- Tags

### AI Content Safety Rules

The news-generation system is designed to generate content only from the information provided by the user.

The AI should not:

- Invent names or people
- Invent numbers or statistics
- Invent quotes
- Invent witnesses
- Invent locations
- Invent dates or times
- Invent causes or explanations
- Add unsupported official statements
- Add information that is not present in the submitted content

If important information is not provided, the AI should omit it instead of making assumptions.

The AI is used for **news drafting and content structuring**, not for independently verifying whether a news report is true or false.

### AI Failure Handling

If the LLM service fails or does not return a usable response, the system handles the failure using the status:

`AI_PROCESSING_FAILED`

This prevents an AI failure from being treated as a successful news generation.

The original user-submitted information is preserved separately from the AI-generated draft so that the original data is not lost.

## Technology Stack

### Frontend

- HTML5
- CSS3
- JavaScript
- Bootstrap 5
- Bootstrap Icons

### Backend

- Python
- Flask
- Flask-SQLAlchemy
- Jinja2 Templates

### Database

- MySQL
- SQLAlchemy ORM
- PyMySQL

### Artificial Intelligence

- Large Language Model (LLM)
- Gemini API
- AI-based news draft generation

### Authentication & Security

- Werkzeug Password Hashing
- Flask Session
- Flask-WTF / CSRF Protection
- Role-Based Access Control (RBAC)
- Input Validation
- File Upload Validation
- Environment Variables using `.env`

### Development Tools

- Visual Studio Code
- Python Virtual Environment (`venv`)
- Git & GitHub

## Project Structure

```text
AI-NewsGen Copilot/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── .env
├── .gitignore
│
├── database/
│   └── db.py
│
├── models/
│   └── database_models.py
│
├── routes/
│   ├── auth.py
│   ├── user.py
│   ├── news.py
│   └── admin.py
│
├── llm/
│   ├── llm_service.py
│   ├── news_generator.py
│   └── prompts.py
│
├── templates/
│   ├── auth/
│   │   ├── user_login.html
│   │   └── admin_login.html
│   │
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── review_news.html
│   │   └── edit_news.html
│   │
│   ├── home.html
│   ├── latest_news.html
│   ├── breaking_news.html
│   ├── featured_news.html
│   ├── categories.html
│   ├── about.html
│   ├── user_dashboard.html
│   ├── submit_news.html
│   ├── my_news.html
│   ├── provide_information.html
│   └── news_detail.html
│
├── static/
│   ├── css/
│   │   └── app.css
│   │
│   └── uploads/
│
└── utils/
    └── ...

## Database Structure

AI-NewsGen Copilot uses **MySQL** as the relational database and **SQLAlchemy ORM** for database operations.

### Main Database Tables

The application currently uses the following main tables:

- `users`
- `news`
- `admin_actions`

### 1. Users Table

The `users` table stores user and administrator account information.

Main fields include:

- `id` — Unique user ID
- `name` — User name
- `email` — User email address
- `password_hash` — Securely hashed password
- `role` — User role (`user` or `admin`)
- `created_at` — Account creation timestamp
- `updated_at` — Last update timestamp

### 2. News Table

The `news` table stores the complete news submission and generation workflow.

It contains:

#### Original User Submission

- User ID
- Category
- Title
- Location
- Incident date
- Incident time
- Bullet points
- Additional description
- Image path
- Video path
- Source URL
- Supporting information

#### AI-Generated Content

- AI headline
- AI subheading
- AI summary
- AI article
- Key facts
- Tags

#### Final/Administrative Content

- Final headline
- Final subheading
- Final summary
- Final article
- News status
- Admin comment
- Breaking news flag
- Featured news flag
- Published timestamp
- Created timestamp
- Updated timestamp

The original user submission and AI-generated content are maintained separately so that the original information is preserved.

### 3. Admin Actions Table

The `admin_actions` table stores administrative activities performed on news articles.

Main fields include:

- `id` — Unique action ID
- `admin_id` — Administrator who performed the action
- `news_id` — Related news ID
- `action` — Action performed
- `comment` — Optional administrative comment
- `created_at` — Action timestamp

### Database Relationships

```text
User
 │
 └───< News
        │
        └───< AdminAction

User
 │
 └───< AdminAction

## Installation & Setup

Follow the steps below to set up AI-NewsGen Copilot on a local system.

### Prerequisites

Make sure the following software is installed:

- Python 3.10.7
- MySQL
- Git
- Visual Studio Code

---

### 1. Clone the Project

Clone the project repository:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>

## Environment Variables & Configuration

AI-NewsGen Copilot uses environment variables to keep sensitive configuration separate from the source code.

### Environment Variables

The project uses the following environment variables:

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Secures Flask sessions and application security |
| `DATABASE_URL` | MySQL database connection |
| `GEMINI_API_KEY` | Authentication for the Gemini LLM service |
| `GEMINI_MODEL` | Configured Gemini model used for AI generation |

### Example `.env` Configuration

```env
SECRET_KEY=your_secret_key

DATABASE_URL=mysql+pymysql://USERNAME:PASSWORD@localhost/ai_newsgen

GEMINI_API_KEY=your_gemini_api_key

GEMINI_MODEL=your_configured_gemini_model

## Application Features & User Roles

AI-NewsGen Copilot provides different features based on the role of the user.

### Public Visitor

A public visitor can access the newspaper without logging in.

Features include:

- View homepage
- View latest news
- View breaking news
- View featured news
- Browse news categories
- Search news
- Filter news
- Read published news articles
- Access About page
- Access Submit News
- Access Admin Login

To submit news, a visitor must first log in as a registered user.

---

### Registered User

A registered user can:

- Register an account
- Login and logout
- Access the User Dashboard
- Submit news
- Upload supporting media
- View submitted news
- Track news status
- View AI-generated drafts
- Provide additional information when requested
- Trigger AI regeneration after providing requested information

Users cannot directly publish news.

---

### Administrator

An administrator has access to the Admin Dashboard.

Admin features include:

- View submitted news
- Review AI-generated drafts
- Edit news
- Request additional information
- Approve news
- Reject news
- Publish approved news
- Mark news as breaking
- Mark news as featured
- View administrative actions through the audit trail

Administrators are responsible for reviewing AI-generated content before publication.

---

### Role-Based Access Control

The application uses role-based access control to restrict protected features.

```text
Public Visitor
      │
      ├── Public News
      ├── Search & Filters
      └── Submit News → User Login
                         │
                         ↓
                    User Dashboard
                         │
                         └── News Submission


Administrator
      │
      └── Admin Login
              │
              ↓
        Admin Dashboard
              │
              ├── Review
              ├── Edit
              ├── Request Information
              ├── Approve
              ├── Reject
              └── Publish

## Testing & Security Status

The application has been tested across the major user, admin, news submission, AI generation, and public news workflows.

### Functional Testing

The following areas have been tested:

- Public homepage and navigation
- User registration and login
- User logout
- Admin login
- News submission
- AI-based news generation
- Admin news review
- Admin news editing
- Request for additional information
- User information submission
- AI news regeneration
- News approval
- News rejection
- News publication
- My News and status tracking
- Public news detail pages
- Search functionality
- Category and news filters
- Breaking news
- Featured news
- Protected page access
- Invalid news ID handling
- Invalid source URL handling
- File upload validation
- Long input handling
- XSS/HTML input handling

### Security Testing

Security-related checks include:

- Password hashing
- Authentication and session management
- Role-based access control
- CSRF protection
- Input validation
- File upload validation
- SQLAlchemy ORM usage
- XSS protection through template auto-escaping
- Sensitive configuration stored using environment variables
- Protected user and administrator routes

### Access Control Testing

The following access-control scenarios have been verified:

- Users cannot access administrator dashboard pages.
- Administrators cannot access user dashboard pages.
- Logged-out visitors cannot access protected user pages.
- Public visitors can access published news without authentication.

### AI Reliability

The AI generation workflow includes failure handling.

If the LLM service fails or returns an unusable response, the news can be marked with:

```text
AI_PROCESSING_FAILED

## Security Features

AI-NewsGen Copilot includes multiple security measures to protect user data, application functionality, and administrative operations.

### Authentication

- User authentication using email and password
- Administrator authentication using a separate admin login
- Secure password hashing using Werkzeug
- Session-based authentication
- Session clearing during logout

### Authorization

The application uses Role-Based Access Control (RBAC).

Two primary roles are supported:

- `user`
- `admin`

Protected routes verify the user's role before allowing access.

### CSRF Protection

Cross-Site Request Forgery (CSRF) protection is implemented using Flask-WTF.

CSRF tokens are included in protected forms such as:

- User registration
- User login
- Admin login
- News submission
- Information submission
- Admin review
- Admin editing
- News publication

### Input Validation

User-provided data is validated before processing.

Validation includes:

- Required field validation
- Password length validation
- Duplicate email validation
- URL validation
- File upload validation
- Appropriate handling of invalid input

### XSS Protection

The application uses Jinja2 template auto-escaping to help prevent Cross-Site Scripting (XSS) attacks.

User-submitted HTML or JavaScript is not intentionally rendered as executable HTML.

### Database Security

The application uses SQLAlchemy ORM for database operations.

This reduces the need to construct raw SQL queries from user-provided input and helps protect against SQL injection vulnerabilities.

### File Upload Security

Uploaded images and videos are validated before being accepted by the application.

Uploaded files are stored separately from the application's source code.

### Sensitive Configuration

Sensitive information such as:

- Secret keys
- Database credentials
- Gemini API credentials

is stored in the `.env` file rather than directly in application source code.

The `.env` file is excluded from version control using `.gitignore`.

### News Content Protection

The original user-submitted information is preserved separately from AI-generated and administrator-edited content.

This helps maintain the integrity of the original submission throughout the news review process.

## Future Scope

AI-NewsGen Copilot can be further enhanced with additional AI-powered and platform-level capabilities.

Possible future enhancements include:

- Automatic news category detection
- Duplicate news detection
- Fake news detection
- Advanced misinformation analysis
- News credibility and source analysis
- Automated fact-checking
- Multi-language news generation
- Advanced AI-based news summarization
- Personalized news recommendations
- Real-time breaking news notifications
- Mobile application
- Cloud deployment and scalable infrastructure
- Advanced analytics and reporting dashboard

These features are considered future enhancements and are not part of the current core implementation.

---

## Current Limitations

The current version of AI-NewsGen Copilot has the following limitations:

- AI-generated content still requires human administrator review.
- The AI system does not independently verify whether submitted information is true or false.
- Automatic fake-news detection is not currently implemented.
- Automatic duplicate-news detection is not currently implemented.
- Automatic category detection is not currently implemented.
- The application currently focuses on AI-assisted news drafting rather than fully autonomous news publishing.
- Deployment and production-level infrastructure configuration are outside the current local development setup.

The administrator remains responsible for reviewing and approving news before publication.

## How to Use the Application

### For Public Visitors

1. Open the AI-NewsGen Copilot homepage.
2. Browse published news from the homepage.
3. Use the navigation menu to access:
   - Latest News
   - Breaking News
   - Featured News
   - Categories
   - About
4. Use the search and filter options to find specific news.
5. Open a published article to read the complete news.
6. To submit news, select **Submit News**.
7. If not logged in, the system redirects to the User Login page.

---

### For Registered Users

1. Register a new account.
2. Login using your registered email and password.
3. Open the **User Dashboard**.
4. Select **Submit News**.
5. Enter the incident and supporting information.
6. Upload an image or video if required.
7. Submit the news.
8. Wait for AI processing.
9. View the generated draft and current status from **My News**.
10. If the administrator requests additional information, open the relevant news.
11. Provide the requested information.
12. Submit the additional information for AI regeneration.
13. Track the updated status until the administrator completes the review.

---

### For Administrators

1. Open the **Admin Login** page.
2. Login using administrator credentials.
3. Open the **Admin Dashboard**.
4. Select a submitted news article.
5. Review the original submission and AI-generated draft.
6. Edit the generated content if necessary.
7. If information is insufficient, request additional information.
8. Approve or reject the news.
9. Publish approved news when it is ready.
10. Optionally mark published news as:
    - Breaking News
    - Featured News
11. Administrative actions are recorded in the audit trail.

---

### News Publication Process

```text
User Submission
      ↓
AI Processing
      ↓
AI Draft
      ↓
Admin Review
      ↓
┌───────────────┬────────────────────┐
│               │                    │
Approve       Request Info         Reject
│               │                    │
↓               ↓                    ↓
Publish      User Response        Rejected
│               │
↓               ↓
Public News   AI Regeneration
                  │
                  ↓
             Admin Review

## Project Status

AI-NewsGen Copilot has completed the core application development and major testing phases.

### Completed Components

- Public digital newspaper interface
- User registration and authentication
- Administrator authentication
- Role-based access control
- User dashboard
- News submission system
- Image and video upload
- AI-powered news generation
- AI-generated headline, subheading, summary, article, key facts, and tags
- User news status tracking
- Additional information request workflow
- AI news regeneration
- Admin review system
- Admin news editing
- News approval and rejection
- News publication
- Breaking news functionality
- Featured news functionality
- News search and filtering
- Category-based news browsing
- Audit trail
- CSRF protection
- Input validation
- File upload validation
- XSS protection
- Responsive user interface
- Error and edge-case handling
- MySQL database integration

---

## Conclusion

AI-NewsGen Copilot demonstrates how Artificial Intelligence can be integrated with a web-based digital newspaper platform to assist in the news drafting process.

The system provides a controlled workflow where users submit incident information, the LLM generates a structured draft, and administrators review and manage the content before publication.

The project combines web development, database management, AI/LLM integration, authentication, security, and administrative moderation into a single application.

The human-in-the-loop approach ensures that AI-generated content is not automatically published without administrative review.

---

## Author

**AI-NewsGen Copilot**

Developed as an academic/final-year project demonstrating the integration of Artificial Intelligence with a digital news management platform.