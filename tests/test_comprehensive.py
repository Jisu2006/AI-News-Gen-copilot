import io
import os
import sys
from datetime import datetime, date, time
from pathlib import Path
import unittest

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from database.db import db
from models.database_models import User, News, AdminAction, OTPVerification
from werkzeug.security import generate_password_hash
from services.otp_service import generate_and_send_otp, verify_otp, can_resend_otp


class ComprehensiveTestSuite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.app.config["WTF_CSRF_ENABLED"] = False
        cls.client = cls.app.test_client()

    def setUp(self):
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    # ==================================================
    # 1. PUBLIC ROUTES TESTING
    # ==================================================

    def test_homepage_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"AI-NewsGen Copilot", response.data)
        self.assertIn(b"Latest News", response.data)

    def test_latest_news_page(self):
        response = self.client.get("/latest-news")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Latest News", response.data)

    def test_breaking_news_page(self):
        response = self.client.get("/breaking-news")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Breaking News", response.data)

    def test_featured_news_page(self):
        response = self.client.get("/featured-news")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Featured News", response.data)

    def test_categories_page(self):
        response = self.client.get("/categories")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Categories", response.data)
        self.assertIn(b"Technology", response.data)

    def test_about_page(self):
        response = self.client.get("/about")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"About", response.data)

    def test_search_and_filters(self):
        # Empty search
        response = self.client.get("/?search=")
        self.assertEqual(response.status_code, 200)

        # Keyword search
        response = self.client.get("/?search=Cricket")
        self.assertEqual(response.status_code, 200)

        # Special characters in search
        response = self.client.get("/?search=%27%22%3Cscript%3E")
        self.assertEqual(response.status_code, 200)

        # Category filter
        response = self.client.get("/?category=Sports")
        self.assertEqual(response.status_code, 200)

        # Date filter
        response = self.client.get("/?date=2026-09-04")
        self.assertEqual(response.status_code, 200)

    def test_news_detail_published_vs_unpublished(self):
        # Find a published news
        published = News.query.filter_by(status="PUBLISHED").first()
        if published:
            response = self.client.get(f"/news/{published.id}")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"AI-NewsGen Copilot", response.data)

        # Request non-existent or unpublished news -> 404
        response = self.client.get("/news/99999999")
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"404", response.data)

    # ==================================================
    # 2. AUTHENTICATION & OTP WORKFLOW TESTING
    # ==================================================

    def test_otp_service_workflow(self):
        test_email = "pytest_user@example.com"

        # Generate OTP
        success, msg = generate_and_send_otp(test_email, "registration", "Pytest User")
        self.assertTrue(success)

        # Fetch stored OTP record
        record = OTPVerification.query.filter_by(email=test_email, used=False).first()
        self.assertIsNotNone(record)
        self.assertEqual(record.attempts, 0)

        # Test cooldown
        can_resend, cooldown_msg, remaining = can_resend_otp(test_email, "registration")
        self.assertFalse(can_resend)
        self.assertGreater(remaining, 0)

        # Test invalid OTP
        valid, invalid_msg = verify_otp(test_email, "000000", "registration")
        self.assertFalse(valid)
        self.assertIn("Incorrect", invalid_msg)

        # Clean up test OTPs
        OTPVerification.query.filter_by(email=test_email).delete()
        db.session.commit()

    def test_user_registration_and_login_flow(self):
        test_email = "test_register_flow@example.com"
        test_pass = "SecurePass123"

        # Clean up prior test user if exists
        User.query.filter_by(email=test_email).delete()
        OTPVerification.query.filter_by(email=test_email).delete()
        db.session.commit()

        # 1. Register User
        resp = self.client.post("/register", data={
            "name": "Flow Tester",
            "email": test_email,
            "password": test_pass
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Verify Email", resp.data)

        user = User.query.filter_by(email=test_email).first()
        self.assertIsNotNone(user)
        self.assertFalse(user.is_verified)

        # 2. Try Login While Unverified -> Redirects to verify-otp
        login_resp = self.client.post("/user/login", data={
            "email": test_email,
            "password": test_pass
        }, follow_redirects=True)
        self.assertEqual(login_resp.status_code, 200)
        self.assertIn(b"Verify Email", login_resp.data)

        # 3. Verify User manually
        user.is_verified = True
        db.session.commit()

        # 4. Login With Verified User
        login_resp = self.client.post("/user/login", data={
            "email": test_email,
            "password": test_pass
        }, follow_redirects=True)
        self.assertEqual(login_resp.status_code, 200)
        self.assertIn(b"User Dashboard", login_resp.data)

        # 5. Logout
        logout_resp = self.client.get("/logout", follow_redirects=True)
        self.assertEqual(logout_resp.status_code, 200)
        self.assertIn(b"Logged out successfully", logout_resp.data)

        # Clean up
        User.query.filter_by(email=test_email).delete()
        OTPVerification.query.filter_by(email=test_email).delete()
        db.session.commit()

    def test_admin_login_and_access(self):
        # Admin account exists in DB (jisu@gmail.com / Admin@12345)
        resp = self.client.post("/admin/login", data={
            "email": "jisu@gmail.com",
            "password": "Admin@12345"
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Admin Dashboard", resp.data)

    def test_rbac_user_cannot_access_admin(self):
        # Create a test session with role = 'user'
        with self.client.session_transaction() as sess:
            sess["user_id"] = 2
            sess["user_name"] = "Regular User"
            sess["user_role"] = "user"

        # Try to access Admin Dashboard
        resp = self.client.get("/admin/dashboard")
        self.assertEqual(resp.status_code, 403)
        self.assertIn(b"403", resp.data)

    def test_rbac_logged_out_cannot_access_user_routes(self):
        # Clear session
        with self.client.session_transaction() as sess:
            sess.clear()

        resp = self.client.get("/user/dashboard", follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/user/login", resp.headers["Location"])

    # ==================================================
    # 3. NEWS SUBMISSION AND ADMIN WORKFLOW
    # ==================================================

    def test_news_submission_validation(self):
        with self.client.session_transaction() as sess:
            sess["user_id"] = 5
            sess["user_name"] = "Tester"
            sess["user_role"] = "user"

        # Missing required fields -> redirect
        resp = self.client.post("/user/submit-news", data={
            "title": "",
            "category": "",
            "bullet_points": ""
        }, follow_redirects=True)
        self.assertIn(b"Category, title and bullet points are required", resp.data)

        # Valid Draft Submission
        resp = self.client.post("/user/submit-news", data={
            "title": "Unit Test Campus Festival",
            "category": "Events",
            "location": "Main Auditorium",
            "incident_date": "2026-09-27",
            "incident_time": "14:30",
            "bullet_points": "Annual festival conducted\nOver 500 participants attended",
            "additional_description": "A successful event celebrating technology and arts.",
            "action": "draft"
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"News saved as draft successfully", resp.data)

        # Clean up created draft
        test_news = News.query.filter_by(title="Unit Test Campus Festival").first()
        self.assertIsNotNone(test_news)
        self.assertEqual(test_news.status, "DRAFT")

        # Admin workflow on this news
        test_news.status = "PENDING_REVIEW"
        db.session.commit()

        # Admin Login
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Admin"
            sess["user_role"] = "admin"

        # Admin Review: Request Information
        resp = self.client.post(f"/admin/review/{test_news.id}", data={
            "action": "request_information",
            "comment": "Please provide proof and official link."
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        db.session.refresh(test_news)
        self.assertEqual(test_news.status, "NEEDS_INFORMATION")

        # Admin Review: Approve
        resp = self.client.post(f"/admin/review/{test_news.id}", data={
            "action": "approve",
            "comment": "Verified and approved.",
            "is_breaking": "1",
            "is_featured": "1"
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        db.session.refresh(test_news)
        self.assertEqual(test_news.status, "APPROVED")
        self.assertTrue(test_news.is_breaking)

        # Admin Edit
        resp = self.client.post(f"/admin/edit/{test_news.id}", data={
            "final_headline": "Annual Tech & Arts Festival Draws Hundreds",
            "final_subheading": "Over 500 students gathered for the vibrant campus fest.",
            "final_summary": "The campus held its annual tech and arts festival with huge participation.",
            "final_article": "The annual festival took place at the Main Auditorium on September 27, 2026. Over 500 participants attended.",
            "key_facts": '["500 participants", "Main Auditorium"]',
            "tags": '["Events", "CampusFest"]',
            "is_breaking": "1",
            "is_featured": "1"
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        # Admin Publish
        resp = self.client.post(f"/admin/publish/{test_news.id}", follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        db.session.refresh(test_news)
        self.assertEqual(test_news.status, "PUBLISHED")
        self.assertIsNotNone(test_news.published_at)

        # Check that it appears on public detail page
        pub_resp = self.client.get(f"/news/{test_news.id}")
        self.assertEqual(pub_resp.status_code, 200)
        self.assertIn(b"Annual Tech &amp; Arts Festival", pub_resp.data)

        # Clean up
        db.session.delete(test_news)
        db.session.commit()

    # ==================================================
    # 4. FILE UPLOAD SECURITY TESTING
    # ==================================================

    def test_file_upload_security(self):
        with self.client.session_transaction() as sess:
            sess["user_id"] = 5
            sess["user_name"] = "Tester"
            sess["user_role"] = "user"

        # Disallowed file extension (.exe / .php / .sh)
        fake_executable = (io.BytesIO(b"MALICIOUS CODE"), "script.exe")
        resp = self.client.post("/user/submit-news", data={
            "title": "Malicious Upload Attempt",
            "category": "Technology",
            "bullet_points": "Testing file upload security restrictions",
            "image": fake_executable,
            "action": "draft"
        }, follow_redirects=True)
        self.assertIn(b"Invalid image file type", resp.data)

        # Allowed image upload
        valid_img = (io.BytesIO(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00"), "sample.jpg")
        resp = self.client.post("/user/submit-news", data={
            "title": "Valid Upload Test",
            "category": "Technology",
            "bullet_points": "Testing valid JPG upload",
            "image": valid_img,
            "action": "draft"
        }, follow_redirects=True)
        self.assertIn(b"News saved as draft successfully", resp.data)

        # Cleanup
        created = News.query.filter_by(title="Valid Upload Test").first()
        if created:
            if created.image_path:
                full_path = Path(PROJECT_ROOT) / "static" / created.image_path
                if full_path.exists():
                    full_path.unlink()
            db.session.delete(created)
            db.session.commit()

    # ==================================================
    # 5. ERROR HANDLERS TESTING
    # ==================================================

    def test_custom_error_pages(self):
        # 404
        r404 = self.client.get("/non-existent-page-url-xyz")
        self.assertEqual(r404.status_code, 404)
        self.assertIn(b"404", r404.data)
        self.assertIn(b"Page Not Found", r404.data)

        # 405
        r405 = self.client.post("/latest-news")
        self.assertEqual(r405.status_code, 405)
        self.assertIn(b"405", r405.data)
        self.assertIn(b"Method Not Allowed", r405.data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
