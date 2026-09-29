import unittest
from app import create_app
from database.db import db
from models.database_models import News, User, NewsLike, NewsComment


class TestEngagementFeatures(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.client = self.app.test_client()

    def test_view_count_and_deduplication(self):
        with self.app.app_context():
            news_item = News.query.filter_by(status="PUBLISHED").first()
            self.assertIsNotNone(news_item)
            news_id = news_item.id
            initial_views = news_item.views_count or 0

            # 1st visit
            resp1 = self.client.get(f"/news/{news_id}")
            self.assertEqual(resp1.status_code, 200)
            db.session.refresh(news_item)
            self.assertEqual(news_item.views_count, initial_views + 1)

            # 2nd visit (same session) -> should not increment
            resp2 = self.client.get(f"/news/{news_id}")
            self.assertEqual(resp2.status_code, 200)
            db.session.refresh(news_item)
            self.assertEqual(news_item.views_count, initial_views + 1)

    def test_like_and_unlike_flow(self):
        with self.app.app_context():
            user = User.query.first()
            news_item = News.query.filter_by(status="PUBLISHED").first()
            news_id = news_item.id

            # Unauthenticated like -> 401
            unauth_client = self.app.test_client()
            unauth_resp = unauth_client.post(
                f"/news/{news_id}/like",
                headers={"X-Requested-With": "XMLHttpRequest"}
            )
            self.assertEqual(unauth_resp.status_code, 401)
            self.assertEqual(unauth_resp.get_json()["error"], "login_required")

            # Authenticated like
            with self.client.session_transaction() as sess:
                sess["user_id"] = user.id
                sess["user_name"] = user.name
                sess["user_role"] = user.role

            # Clear existing like for test
            NewsLike.query.filter_by(news_id=news_id, user_id=user.id).delete()
            db.session.commit()

            # Like
            like_resp = self.client.post(
                f"/news/{news_id}/like",
                headers={"X-Requested-With": "XMLHttpRequest"}
            )
            self.assertEqual(like_resp.status_code, 200)
            self.assertTrue(like_resp.get_json()["liked"])

            # Unlike
            unlike_resp = self.client.post(
                f"/news/{news_id}/like",
                headers={"X-Requested-With": "XMLHttpRequest"}
            )
            self.assertEqual(unlike_resp.status_code, 200)
            self.assertFalse(unlike_resp.get_json()["liked"])

    def test_comment_submission_and_rendering(self):
        with self.app.app_context():
            user = User.query.first()
            news_item = News.query.filter_by(status="PUBLISHED").first()
            news_id = news_item.id

            # Unauthenticated comment -> 401
            unauth_client = self.app.test_client()
            unauth_resp = unauth_client.post(
                f"/news/{news_id}/comment",
                json={"comment_text": "Test unauth comment"},
                headers={"X-Requested-With": "XMLHttpRequest"}
            )
            self.assertEqual(unauth_resp.status_code, 401)

            # Authenticated comment
            with self.client.session_transaction() as sess:
                sess["user_id"] = user.id
                sess["user_name"] = user.name
                sess["user_role"] = user.role

            # Empty comment validation -> 400
            empty_resp = self.client.post(
                f"/news/{news_id}/comment",
                json={"comment_text": "   "},
                headers={"X-Requested-With": "XMLHttpRequest"}
            )
            self.assertEqual(empty_resp.status_code, 400)

            # Valid comment post
            comment_text = "Automated test comment for verified news discussion."
            post_resp = self.client.post(
                f"/news/{news_id}/comment",
                json={"comment_text": comment_text},
                headers={"X-Requested-With": "XMLHttpRequest"}
            )
            self.assertEqual(post_resp.status_code, 200)
            json_data = post_resp.get_json()
            self.assertTrue(json_data["success"])
            self.assertEqual(json_data["comment"]["comment_text"], comment_text)

            # Check rendered page
            page_resp = self.client.get(f"/news/{news_id}")
            self.assertIn(comment_text, page_resp.get_data(as_text=True))
            self.assertIn("Comments", page_resp.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
