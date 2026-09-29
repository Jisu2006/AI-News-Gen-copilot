# AI-NewsGen Copilot

## AI-Powered Digital Newspaper and News Drafting Platform

**AI-NewsGen Copilot** is a digital news management platform that combines community-driven news reporting with Large Language Model (LLM) drafting and human-in-the-loop editorial moderation.

Public visitors can read published news, explore categories, search, and filter news stories. Registered users submit incident details, photos, and videos, which Google Gemini transforms into structured news drafts (headline, subheading, executive summary, article, key facts, and tags). Administrators review, request additional information, edit, approve, and publish the verified stories to the public newspaper website.

AI never publishes directly without administrator review.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [Technology Stack](#technology-stack)
4. [Project Architecture](#project-architecture)
5. [Folder Structure](#folder-structure)
6. [Installation & Setup](#installation--setup)
7. [Environment Variables](#environment-variables)
8. [Database Setup & Schema](#database-setup--schema)
9. [How to Run](#how-to-run)
10. [User Workflow](#user-workflow)
11. [Admin Workflow](#admin-workflow)
12. [AI Drafting Workflow](#ai-drafting-workflow)
13. [Security Implementations](#security-implementations)
14. [Testing & Quality Assurance](#testing--quality-assurance)
15. [Limitations](#limitations)
16. [Future Scope](#future-scope)
17. [Project Status](#project-status)
18. [Author Information](#author-information)

---

## 1. Project Overview

Digital newsrooms face challenges in rapidly processing incident reports into professional, coherent news drafts while preventing misinformation. **AI-NewsGen Copilot** bridges this gap:

- **Public Audience**: Free access to breaking, featured, and categorized news.
- **User Contributors**: Submit structured incident reports with multimedia.
- **AI Copilot (Gemini)**: Rapidly drafts articles adhering strictly to submitted facts with zero fabrication.
- **Editorial Board (Admin)**: Full control to request further evidence, edit, approve, or reject submissions before publication.

---

## 2. Key Features

### 📰 Public Newspaper
- **Homepage**: Displays latest, breaking, and featured stories with category and location filters.
- **Live Search**: Full-text and keyword search across headlines, content, tags, locations, and categories.
- **Dynamic Category Pages**: Filter news by topics such as Local News, Accidents, Crime, Sports, Technology, Business, Politics, Education, Weather, Events, etc.
- **Dedicated Feeds**: Breaking News, Latest News, and Featured News sections.
- **News Details**: Clean typography, hero images, embedded video player, executive summary, key facts list, tags, and related stories.

### 👤 User Portal & Authentication
- **Secure Registration**: Name, email, and password validation with bcrypt hashing.
- **OTP Verification**: Secure 6-digit One-Time Password sent via Gmail SMTP with expiration (10 min) and cooldown protection (60s).
- **Session-Based Authentication**: Strict role segregation preventing standard users from accessing admin routes.
- **User Dashboard**: Track submission statistics (total submissions, pending reviews, published articles, info requests).
- **News Submission**: Support for category, incident date/time, bullet points, narrative description, image upload, video upload, source link, and supporting evidence.
- **Draft Mode**: Save in-progress submissions before sending to AI processing.
- **My News**: View status badges (`DRAFT`, `AI_PROCESSING`, `PENDING_REVIEW`, `NEEDS_INFORMATION`, `APPROVED`, `PUBLISHED`, `REJECTED`, `AI_PROCESSING_FAILED`).
- **Provide Additional Information**: Direct response interface for editor queries with automatic AI regeneration.

### 🛡️ Administrator Editorial Desk
- **Admin Dashboard**: Real-time counters and queues for Pending Review, Approved (Ready to Publish), and Published News.
- **Audit Trail**: Detailed log of all administrative actions (`APPROVED`, `EDITED`, `PUBLISHED`, `REQUEST_INFORMATION`, `REJECTED`).
- **Three-Way Comparison**: Inspect original user input, AI-generated draft, and editorial final content.
- **Editorial Review Actions**:
  - **Approve**: Mark draft as approved, configure breaking/featured flags.
  - **Request Additional Information**: Send specific requests back to the user with feedback.
  - **Reject**: Reject submission with explanation.
  - **Edit Content**: Modify headlines, summaries, full articles, key facts, and tags.
  - **Publish**: Release approved articles to the live public newspaper.

### 🤖 AI News Drafting (Gemini)
- **Strict Anti-Hallucination Prompting**: System prompt strictly enforces that only user-provided facts are used.
- **Date Safety Enforcement**: Disallows fabricated dates when incident date is omitted by the user.
- **Structured JSON Schema**: Produces headlines, subheadings, executive summaries, articles, key facts, and tags.
- **Fault-Tolerant Retries**: Automatic retry handling for transient API errors (429/503) and fallback failure states (`AI_PROCESSING_FAILED`).

---

## 3. Technology Stack

- **Backend**: Python 3.10+, Flask 3.1.3
- **ORM & Database**: Flask-SQLAlchemy 3.1.1, SQLAlchemy 2.0.52, PyMySQL 1.2.0, MySQL 8.0
- **AI / LLM**: Google GenAI SDK (`google-genai`), Gemini 3.6 Flash / Gemini 2.5 Flash
- **Security & Forms**: Werkzeug (Password Hashing), Flask-WTF (CSRF Protection)
- **Email Delivery**: Standard Library `smtplib` + `email.mime` (Gmail SMTP over TLS 587)
- **Frontend**: HTML5, Jinja2, Vanilla CSS (`app.css`), Bootstrap 5.3.3, Bootstrap Icons 1.11.3

---

## 4. Project Architecture

```
                      +-------------------+
                      |  Public Visitor   |
                      +---------+---------+
                                |
               +----------------+----------------+
               |                                 |
       [Read / Search / Filter]          [Submit News Click]
               |                                 |
               v                                 v
      +-----------------+              +-------------------+
      | Published News  |              | User Login / Reg  |
      +-----------------+              +---------+---------+
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
                      +---------------------+         +---------------------+
                      |                                                     |
                      v                                                     v
            [Request More Info]                                         [Approve]
                      |                                                     |
                      v                                                     v
            [User Responds]                                            [Publish]
                      |                                                     |
                      v                                                     v
            [AI Regenerates]                                          [Public Site]
                      |
                      +---------------------> [Admin Review]
```

---

## 5. Folder Structure

```
AI-News-Gen-copilot/
├── app.py                      # Flask Application entry point & factory
├── config.py                   # App Configuration & environment loader
├── reset_admin.py              # Admin account seed/reset script
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (secrets)
├── .gitignore                  # Git ignore rules
├── database/
│   └── db.py                   # SQLAlchemy instance
├── llm/
│   ├── __init__.py             # LLM package marker
│   ├── llm_service.py          # Gemini Client integration & retry handler
│   ├── news_generator.py       # News drafting orchestration & validation
│   └── prompts.py              # Strict factual news system prompts
├── models/
│   └── database_models.py      # User, News, AdminAction, OTPVerification models
├── routes/
│   ├── auth.py                 # User/Admin login, registration, OTP, logout
│   ├── user.py                 # User dashboard, submission, My News, info update
│   ├── admin.py                # Admin dashboard, review, edit, publish
│   └── news.py                 # Public homepage, detail, latest, breaking, categories
├── services/
│   ├── __init__.py             # Services package marker
│   ├── email_service.py        # SMTP email delivery for OTP codes
│   └── otp_service.py          # Secure OTP generation, hashing & verification
├── static/
│   ├── css/
│   │   └── app.css             # Theme design system & custom styles
│   └── uploads/                # User uploaded media (images & videos)
├── templates/
│   ├── admin/
│   │   ├── dashboard.html      # Admin management desk
│   │   ├── review_news.html    # Three-way review & approval screen
│   │   └── edit_news.html      # Editorial draft modification screen
│   ├── auth/
│   │   ├── user_login.html     # User login portal
│   │   ├── admin_login.html    # Administrator login portal
│   │   └── verify_otp.html     # OTP code entry & resend interface
│   ├── errors/
│   │   └── error.html          # Custom 400, 403, 404, 405, 413, 500 error pages
│   ├── news/
│   │   ├── home.html           # Main newspaper homepage
│   │   ├── detail.html         # Individual article reading view
│   │   ├── latest_news.html    # Chronological published news feed
│   │   ├── breaking_news.html  # High-priority breaking news feed
│   │   ├── featured_news.html  # Curated featured news feed
│   │   ├── categories.html     # Topic browsing directory
│   │   └── about.html          # About the platform
│   ├── login.html              # Login redirect helper
│   ├── register.html           # User registration form
│   ├── user_dashboard.html     # User activity overview
│   ├── submit_news.html        # News creation & media upload form
│   ├── my_news.html            # User submission tracking table
│   └── provide_information.html# Additional info submission view
└── tests/
    ├── test_llm.py             # LLM standalone test
    └── test_comprehensive.py   # Full unit and integration test suite
```

---

## 6. Installation & Setup

### Prerequisites
- Python 3.10+
- MySQL 8.0+
- Google Gemini API Key

### Step 1: Clone and Enter Directory
```bash
git clone https://github.com/Jisu2006/AI-News-Gen-copilot.git
cd AI-News-Gen-copilot
```

### Step 2: Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 7. Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-super-secret-flask-key
DATABASE_URL=mysql+pymysql://root:password@localhost/ai_newsgen

# Gmail SMTP Configuration for OTP
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Google Gemini API
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-3.6-flash
```

---

## 8. Database Setup & Schema

1. Create the MySQL database:
```sql
CREATE DATABASE ai_newsgen CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Automatic Table Creation:
Flask automatically synchronizes tables on first startup via `db.create_all()` in `app.py`.

3. Primary Tables:
- `users`: User and admin credentials, roles, email verification status.
- `news`: Full news lifecycle records (user inputs, AI outputs, editorial edits, flags, status).
- `admin_actions`: Complete editorial audit log.
- `otp_verifications`: Hashed OTP tokens, attempt tracking, cooldown, and expiration.

4. Seed Admin Account:
```bash
python reset_admin.py
```
*(Default Admin: `jisu@gmail.com` / Password: `Admin@12345`)*

---

## 9. How to Run

### Start the Application:
```bash
python app.py
```
Visit `http://127.0.0.1:5000` in your web browser.

---

## 10. User Workflow

1. **Visit Homepage**: Browse public stories freely.
2. **Click "Submit News"**: Redirected to Login if not authenticated.
3. **Register**: Provide name, email, password.
4. **Verify OTP**: Enter the 6-digit code delivered to your email inbox.
5. **Dashboard**: Navigate to `User Dashboard` -> `Submit News`.
6. **Fill Incident Form**: Add title, category, date, bullet points, photos, or videos.
7. **Submit for AI Processing**: Gemini analyzes the report and creates a structured draft.
8. **Track in My News**: Monitor review progress. If the editor requests clarification, click "Provide Info" to submit amendments.

---

## 11. Admin Workflow

1. **Login**: Navigate to `/admin/login`.
2. **Admin Dashboard**: View count widgets and categorized queues (Pending, Approved, Published).
3. **Review News**:
   - Compare user inputs and AI drafts.
   - Choose: **Approve**, **Request Information**, or **Reject**.
4. **Edit Draft**: Tweak headline, summary, article, key facts, tags, breaking, and featured switches.
5. **Publish**: Click "Publish News" to make the story live on the public newspaper.
6. **Audit Trail**: Review historical actions taken on all news items.

---

## 12. AI Drafting Workflow

- Prompt templates enforce strict factual boundaries.
- The model structures raw user notes into standard newspaper inverted-pyramid style.
- Output includes: Headline, Subheading, Summary, Article Body, Key Facts Bullet Points, and Search Tags.
- In case of API quota or network failure, the submission is preserved with status `AI_PROCESSING_FAILED` and can be retried without losing data.

---

## 13. Security Implementations

- **Role-Based Access Control (RBAC)**: Strict server-side validation on every route.
- **CSRF Protection**: Token validation on all state-changing `POST` requests via Flask-WTF.
- **Password Security**: Bcrypt / pbkdf2 password hashing via `werkzeug.security`.
- **OTP Security**: Hashed storage (`generate_password_hash`), 10-minute expiry, max 5 attempts, 60-second resend cooldown, zero frontend exposure.
- **File Upload Protection**: Controlled storage path, extension whitelisting, UUID filename generation, size limits (10MB image, 100MB video).
- **Injection Defense**: SQLAlchemy parameterized queries protect against SQL injection. Jinja2 auto-escaping prevents XSS.
- **Safe Redirects**: Protection against open redirect attacks via host validation.

---

## 14. Testing & Quality Assurance

Run the automated test suite:

```bash
# Run comprehensive unit and integration tests
python tests/test_comprehensive.py

# Run standalone LLM generation test
python tests/test_llm.py
```

### Test Coverage Highlights:
- ✅ Public homepage, category, date, and keyword search/filtering.
- ✅ News detail view access control (published vs. 404 for draft/unpublished).
- ✅ User registration, OTP generation, verification, and rate limiting.
- ✅ Role-based access control (User vs. Admin vs. Logged out).
- ✅ Full news submission, draft saving, and administrative approval/publishing.
- ✅ Upload security restrictions and extension filtering.
- ✅ Custom error handlers (400, 403, 404, 405, 413, 500).

---

## 15. Limitations

- **Video Processing**: Videos are stored and streamed directly without asynchronous cloud transcoding.
- **SMTP Dependency**: OTP email delivery requires valid Gmail SMTP credentials or internet access.
- **AI Latency**: Gemini API drafting takes 2–4 seconds depending on network latency.

---

## 16. Future Scope

- Asynchronous background task queue (Celery + Redis) for large video processing.
- Multi-language news translation and audio narration using Text-to-Speech (TTS).
- Real-time notification badges for users when their news is published or needs info.
- Social sharing and reader engagement analytics.

---

## 17. Project Status

- **Status**: Stable, Production-Ready, Fully Tested.
- **Verification**: All routes, database relations, AI flows, and security policies verified.

---

## 18. Author Information

- **Project Lead**: Jisu Kumar Thakur
- **Repository**: [AI-News-Gen-copilot](https://github.com/Jisu2006/AI-News-Gen-copilot)
- **License**: MIT
