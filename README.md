# AI-NewsGen Copilot

## AI-Powered Digital Newspaper and News Drafting Platform

**AI-NewsGen Copilot** is a Flask-based digital news management platform that combines community-driven news reporting with Google Gemini-powered drafting and human-in-the-loop editorial moderation.

Public visitors can read published news, browse categories, search and filter stories, and open individual articles. Registered users can submit incident details with supporting media. Gemini converts the submitted information into a structured news draft, while administrators review, edit, approve, request additional information, reject, and publish stories.

> **Important:** AI-generated content is not published automatically. Every story goes through administrator/editorial review before it becomes public.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Key Features](#2-key-features)
3. [Technology Stack](#3-technology-stack)
4. [Project Architecture](#4-project-architecture)
5. [Folder Structure](#5-folder-structure)
6. [Installation & Setup](#6-installation--setup)
7. [Environment Variables](#7-environment-variables)
8. [MongoDB Atlas Setup](#8-mongodb-atlas-setup)
9. [How to Run](#9-how-to-run)
10. [Application Workflows](#10-application-workflows)
11. [AI Drafting Workflow](#11-ai-drafting-workflow)
12. [Security Implementations](#12-security-implementations)
13. [Testing & Verification](#13-testing--verification)
14. [Deployment](#14-deployment)
15. [Limitations](#15-limitations)
16. [Future Scope](#16-future-scope)
17. [Project Status](#17-project-status)
18. [Repository](#18-repository)
19. [License](#19-license)

---

## 1. Project Overview

Digital news platforms need a way to transform raw incident reports into structured news content quickly while keeping editorial control and reducing the risk of unsupported information.

**AI-NewsGen Copilot** addresses this workflow through four main layers:

- **Public Audience:** Read published, latest, breaking, featured, and categorized news.
- **User Contributors:** Submit incident reports, descriptions, source links, supporting evidence, images, and videos.
- **AI Copilot (Gemini):** Converts submitted information into a structured draft while being instructed to stay within the supplied facts.
- **Editorial Administration:** Review, request additional information, edit, approve, reject, and publish submitted stories.

The backend uses **MongoDB Atlas** as the primary database.

---

## 2. Key Features

### 📰 Public Newspaper

- **Homepage:** Latest published stories with category and location information.
- **Search:** Search across available news fields such as headline, article content, tags, location, and category.
- **Category Pages:** Browse news by categories such as Local News, Accidents, Crime, Sports, Technology, Business, Politics, Education, Weather, Events, and related topics.
- **Latest News:** Chronological feed of published stories.
- **Breaking News:** Dedicated feed for stories marked as breaking news.
- **Featured News:** Dedicated feed for stories selected as featured.
- **News Details:** Individual article pages with headline, summary, article body, key facts, tags, media, and related information.
- **View Counter:** Published stories track article views.
- **Reader Engagement:** Logged-in users can like/unlike articles and add comments.

### 👤 User Portal & Authentication

- **Registration:** Name, email, and password based account creation.
- **Password Hashing:** Passwords are stored using secure password hashing utilities.
- **OTP Verification:** Six-digit email OTP verification through Gmail SMTP.
- **OTP Protection:** OTP expiry, verification attempts, and resend cooldown are enforced.
- **Session Authentication:** Server-side session-based authentication.
- **Role Separation:** User routes and admin routes are protected separately.
- **User Dashboard:** Submission statistics and account activity.
- **News Submission:** Incident details, category, incident date/time, bullet points, description, source link, supporting evidence, image, and video.
- **Draft Mode:** Save a news submission as a draft before sending it for processing.
- **Submission Tracking:** Users can track statuses such as:
  - `DRAFT`
  - `AI_PROCESSING`
  - `PENDING_REVIEW`
  - `NEEDS_INFORMATION`
  - `APPROVED`
  - `PUBLISHED`
  - `REJECTED`
  - `AI_PROCESSING_FAILED`
- **Additional Information:** Users can respond when an administrator requests clarification or more evidence.

### 🛡️ Administrator Editorial Desk

- **Admin Login:** Dedicated administrator authentication and protected admin routes.
- **Admin Dashboard:** Overview of pending, approved, and published stories.
- **Editorial Review:** Inspect submitted content and AI-generated drafts.
- **Request Information:** Send a clarification/evidence request back to the contributor.
- **Approve:** Approve a story for publication and configure relevant editorial flags.
- **Reject:** Reject submissions with an explanation.
- **Edit Content:** Modify headline, subheading, summary, article, key facts, tags, and supported editorial fields.
- **Publish:** Publish approved stories to the public newspaper.
- **Audit Trail:** Administrative actions are stored for traceability.
- **Three-Way Review:** Compare original user input, AI-generated content, and edited/final content where available.

### 🤖 AI News Drafting

- **Google Gemini Integration:** Uses the Google GenAI SDK.
- **Structured Drafting:** Generates headline, subheading, executive summary, article body, key facts, and search tags.
- **Fact-Constrained Prompting:** Prompts instruct the model to remain within the information supplied by the contributor.
- **Date Safety:** The generation flow is designed to avoid inventing incident dates when a date was not supplied.
- **Retry Handling:** Transient Gemini/API failures can be retried.
- **Failure State:** A failed generation can be represented using `AI_PROCESSING_FAILED` without discarding the original submission.

### 📁 Media Uploads

- Image uploads are supported.
- Video uploads are supported.
- File extensions are validated.
- Generated/normalized filenames are used for uploaded files.
- Upload size limits are enforced by the application.
- The current implementation stores media under the application's local `static/uploads/` directory.

---

## 3. Technology Stack

### Backend

- **Python:** 3.13-compatible project environment
- **Web Framework:** Flask 3.1.3
- **Production Server:** Gunicorn
- **Database Driver:** PyMongo
- **Database:** MongoDB Atlas

### AI / LLM

- **Google GenAI SDK:** `google-genai`
- **Model:** Configured through `GEMINI_MODEL` (currently `gemini-3.6-flash` in the project environment)

### Security & Forms

- **Werkzeug:** Password hashing and Flask security utilities
- **Flask-WTF:** CSRF protection
- **Session-Based Authentication:** Flask session handling
- **OTP:** Hashed OTP storage, expiry, attempt limits, and resend cooldown

### Email

- **Python SMTP:** `smtplib`
- **Email Format:** `email.mime`
- **Provider:** Gmail SMTP over TLS on port 587

### Frontend

- HTML5
- Jinja2 templates
- Custom CSS
- Bootstrap 5.3.3
- Bootstrap Icons 1.11.3

### Deployment

- **Render:** Flask web-service deployment
- **MongoDB Atlas:** Cloud database
- **Gunicorn:** Production WSGI server

---

## 4. Project Architecture

```text
                           +----------------------+
                           |    Public Visitor    |
                           +----------+-----------+
                                      |
                      +---------------+---------------+
                      |                               |
               Read / Search / Filter            Submit News
                      |                               |
                      v                               v
             +------------------+            +-------------------+
             | Published News   |            | User Login / Reg  |
             +------------------+            +---------+---------+
                                                        |
                                                        v
                                               +-------------------+
                                               |  User Dashboard   |
                                               +---------+---------+
                                                        |
                                                        v
                                               +-------------------+
                                               | Submit Incident   |
                                               +---------+---------+
                                                        |
                                                        v
                                               +-------------------+
                                               |  Gemini AI Draft  |
                                               +---------+---------+
                                                        |
                                                        v
                                               +-------------------+
                                               |   Admin Review    |
                                               +----+---------+----+
                                                    |         |
                                      Request Info  |         |  Approve
                                                    |         |
                                                    v         v
                                             +-----------+  +---------+
                                             |User Reply |  | Publish |
                                             +-----+-----+  +----+----+
                                                   |             |
                                                   v             v
                                            AI Regenerates   Public Site
                                                   |
                                                   +-----> Admin Review

                         +--------------------------------------+
                         |             MongoDB Atlas             |
                         | users / news / OTP / comments /      |
                         | likes / admin actions / counters     |
                         +--------------------------------------+
```

---

## 5. Folder Structure

The project follows a Flask application structure with MongoDB repositories:

```text
AI-News-Gen-copilot/
│
├── app.py                              # Flask application entry point
├── config.py                           # Environment/application configuration
├── create_admin_mongodb.py             # Admin account creation/setup utility
├── requirements.txt                    # Python dependencies
├── Procfile                            # Production start command for Render
├── .python-version                     # Python version used for deployment
├── .env                                # Local secrets (not committed)
├── .gitignore                          # Ignored files and folders
│
├── database/
│   ├── __init__.py
│   └── mongo.py                        # MongoDB Atlas connection and database helpers
│
├── repositories/
│   ├── __init__.py
│   ├── user_repository.py              # User data access
│   ├── news_repository.py              # News data access
│   ├── admin_repository.py             # Admin/editorial data access
│   └── engagement_repository.py        # Likes, comments, and engagement data access
│
├── llm/
│   ├── __init__.py
│   ├── llm_service.py                  # Gemini client and retry handling
│   ├── news_generator.py               # News drafting orchestration
│   └── prompts.py                      # News-generation prompts
│
├── routes/
│   ├── __init__.py
│   ├── auth.py                         # Registration, OTP, login, logout
│   ├── user.py                         # User dashboard and submissions
│   ├── admin.py                        # Admin dashboard, review, edit, publish
│   └── news.py                         # Public news, categories, search, details
│
├── services/
│   ├── __init__.py
│   ├── email_service.py                # Gmail SMTP email delivery
│   └── otp_service.py                  # OTP generation and verification
│
├── static/
│   ├── css/
│   │   └── app.css                     # Application styling
│   └── uploads/                         # Local uploaded images/videos
│
├── templates/
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── review_news.html
│   │   └── edit_news.html
│   │
│   ├── auth/
│   │   ├── user_login.html
│   │   ├── admin_login.html
│   │   └── verify_otp.html
│   │
│   ├── errors/
│   │   └── error.html
│   │
│   ├── news/
│   │   ├── home.html
│   │   ├── detail.html
│   │   ├── latest_news.html
│   │   ├── breaking_news.html
│   │   ├── featured_news.html
│   │   ├── categories.html
│   │   └── about.html
│   │
│   ├── login.html
│   ├── register.html
│   ├── user_dashboard.html
│   ├── submit_news.html
│   ├── my_news.html
│   └── provide_information.html
│
└── tests/
    └── test_llm.py                     # LLM + MongoDB integration test
```

> Some local development/test helper files may also exist in the repository root. The structure above reflects the current application architecture rather than the old SQLAlchemy-based structure.

---

## 6. Installation & Setup

### Prerequisites

- Python 3.13 recommended for the current project environment
- A MongoDB Atlas account and cluster
- A Google Gemini API key
- A Gmail account with an App Password for OTP email delivery
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/ankitprajapati8235/AI-News-Gen-copilot.git
cd AI-News-Gen-copilot
```

### Step 2: Create a Virtual Environment

#### Windows

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root and add the variables described below.

---

## 7. Environment Variables

Create a `.env` file:

```env
# Flask
SECRET_KEY=your-super-secret-flask-key

# MongoDB Atlas
MONGO_URI=your-mongodb-atlas-connection-string
MONGO_DB_NAME=ai_newsgen

# Gmail SMTP / OTP
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Google Gemini
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-3.6-flash
```

### Security Notes

- Never commit `.env` to Git.
- Never place API keys, Gmail App Passwords, MongoDB passwords, or administrator passwords in this README.
- `.env` should remain ignored through `.gitignore`.
- For Render, add the same variables in the service's environment-variable settings instead of uploading the `.env` file.

---

## 8. MongoDB Atlas Setup

The project uses **MongoDB Atlas**, not MySQL or SQLAlchemy.

### Step 1: Create a MongoDB Atlas Cluster

Create or use a MongoDB Atlas cluster.

### Step 2: Create a Database User

Create a database user with the permissions required by the application.

### Step 3: Configure Network Access

Allow the application server's network/IP range to connect to the Atlas cluster.

For local development, use the IP access configuration appropriate for your own development environment.

For Render deployment, configure the Atlas Network Access list to allow the Render service's outbound IP/CIDR ranges.

### Step 4: Configure the Connection String

Set:

```env
MONGO_URI=your-mongodb-atlas-connection-string
MONGO_DB_NAME=ai_newsgen
```

The application connects to the database through `database/mongo.py`.

### Collections Used by the Application

The application currently uses MongoDB collections including:

```text
users
news
admin_actions
otp_verifications
news_comments
news_likes
counters
```

MongoDB indexes and collection setup are handled by the application's database initialization/helpers.

### Admin Account

An administrator account is created/configured through the project's admin setup utility.

**Administrator email addresses and passwords are intentionally not documented in this README.**

---

## 9. How to Run

### Start the Development Server

With the virtual environment activated:

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

### Health Check

The application exposes:

```text
GET /health
```

Expected response:

```json
{
  "status": "ok",
  "service": "AI-News-Gen-copilot"
}
```

This endpoint is also suitable for deployment health checks.

---

## 10. Application Workflows

### User Workflow

```text
Visitor
  |
  v
Homepage
  |
  +--> Browse/Search/Filter News
  |
  +--> Submit News
          |
          v
       Register
          |
          v
      Email OTP
          |
          v
     Verify Account
          |
          v
     User Dashboard
          |
          v
     Submit Incident
          |
          v
      Gemini Draft
          |
          v
     Pending Review
          |
          +--> Needs Information --> User Responds --> AI Regeneration
          |
          +--> Approved --> Published
          |
          +--> Rejected
```

### Admin Workflow

```text
Admin Login
    |
    v
Admin Dashboard
    |
    v
Review Submission
    |
    +--> Approve
    |
    +--> Request Information
    |
    +--> Reject
    |
    +--> Edit
            |
            v
          Publish
```

---

## 11. AI Drafting Workflow

1. A registered contributor submits incident information.
2. The application stores the original submission in MongoDB.
3. Gemini receives the structured input using the project's news-generation prompts.
4. The model returns a structured news draft.
5. The generated draft is saved with the submission.
6. The story enters the administrative review flow.
7. The administrator can edit, approve, reject, or request more information.
8. When more information is supplied, the application can regenerate the AI draft.
9. Only an approved/published story becomes publicly visible.

The AI layer is designed to reduce unsupported content by constraining generation to contributor-provided information. Editorial verification remains the final control.

---

## 12. Security Implementations

- **Role-Based Access Control:** Server-side checks protect user and administrator routes.
- **CSRF Protection:** State-changing forms use Flask-WTF CSRF protection.
- **Password Hashing:** Passwords are stored using Werkzeug security hashing functions.
- **OTP Security:** OTPs are hashed before storage and protected by expiry, attempt limits, and resend cooldown.
- **Session Authentication:** Authenticated sessions are handled server-side.
- **File Validation:** Uploads use extension/type validation, controlled storage paths, generated filenames, and size limits.
- **XSS Protection:** Jinja2 template auto-escaping is used for rendered content.
- **Safe Redirect Handling:** Redirect behavior is validated to reduce unsafe/open redirect scenarios.
- **Secrets Management:** Credentials are supplied through environment variables rather than hard-coded into source files.

---

## 13. Testing & Verification

The project includes application-level and repository/integration verification for the MongoDB-based architecture.

### Useful Local Checks

```bash
python -c "from app import app; print('APP_IMPORT_OK')"
```

MongoDB connectivity and initialization:

```bash
python test_mongodb.py
```

Repository checks:

```bash
python test_user_repository.py
python test_news_repository.py
python test_admin_repository.py
python test_engagement_mongodb.py
```

Public-news checks:

```bash
python test_public_news.py
```

Gemini connectivity:

```bash
python test_gemini.py
```

LLM integration:

```bash
python tests/test_llm.py
```

Dependency consistency:

```bash
pip check
```

The application has been manually verified across the main flow, including:

- MongoDB Atlas connection
- User registration and OTP verification
- User login/logout
- News submission and drafting
- Gemini generation
- Administrative review
- Publishing
- Image/video uploads
- Public article details
- View counts
- Likes/unlikes
- Comments
- Category/location/news pages
- IST-aware comment timestamps
- MongoDB collections and indexes

---

## 14. Deployment

The project is prepared for deployment as a Flask web service.

### Render Configuration

Use:

**Root Directory**

```text
(blank)
```

**Build Command**

```bash
pip install -r requirements.txt
```

**Start Command**

```bash
gunicorn app:app
```

**Health Check Path**

```text
/health
```

### Required Render Environment Variables

Add the following to the Render service environment:

```text
SECRET_KEY
MONGO_URI
MONGO_DB_NAME
MAIL_SERVER
MAIL_PORT
MAIL_USE_TLS
MAIL_USERNAME
MAIL_PASSWORD
MAIL_DEFAULT_SENDER
GEMINI_API_KEY
GEMINI_MODEL
```

Do not upload the local `.env` file to the deployment service.

### MongoDB Atlas + Render

The deployed service must be able to reach the MongoDB Atlas cluster. Configure the Atlas Network Access list for the appropriate Render outbound IP/CIDR ranges.

### Local Media on Cloud Deployment

The current application stores uploaded images/videos in:

```text
static/uploads/
```

This local filesystem approach is suitable for development, but production deployments should use persistent object storage for reliable long-term media storage.

---

## 15. Limitations

- **Local Media Storage:** Uploaded files currently use local application storage.
- **No Background Job Queue:** AI generation and related work are handled in the request/application flow rather than a dedicated asynchronous worker system.
- **SMTP Dependency:** OTP delivery requires working Gmail SMTP credentials and network connectivity.
- **AI Latency:** Generation time depends on Gemini API availability, response time, and network conditions.
- **Editorial Dependency:** AI output still requires administrator review before publication.
- **Cloud Deployment Storage:** Ephemeral application files are not a substitute for production-grade persistent media storage.

---

## 16. Future Scope

- Persistent cloud object storage for uploaded images and videos.
- Asynchronous background processing using a task queue such as Celery + Redis.
- Multi-language news translation.
- Text-to-Speech/audio narration.
- Real-time notifications for users when articles need information or are published.
- Advanced reader engagement analytics.
- Editorial performance dashboards.
- Enhanced search and ranking.
- Additional deployment observability and production monitoring.

---

## 17. Project Status

- **Application:** Functional
- **Database:** Migrated from the old SQLAlchemy/MySQL architecture to MongoDB Atlas
- **AI Integration:** Google Gemini integrated
- **Authentication:** Registration, OTP verification, sessions, and role separation implemented
- **Editorial Workflow:** Review, information request, approval, rejection, editing, and publishing implemented
- **Engagement:** Views, likes, and comments implemented
- **Deployment:** Render deployment configuration prepared
- **Health Check:** `/health` endpoint available
- **Testing:** MongoDB repositories, public news flow, engagement flow, and Gemini integration verified

---

## 18. Repository

**GitHub Repository**

[AI-News-Gen-copilot](https://github.com/ankitprajapati8235/AI-News-Gen-copilot)

---

## 19. License

MIT License
