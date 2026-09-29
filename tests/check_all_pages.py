from app import create_app
from models.database_models import db, User, News
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Make sure test user and admin exist
    user = User.query.filter_by(email="testuser_check@example.com").first()
    if not user:
        user = User(
            name="Test Check User",
            email="testuser_check@example.com",
            password_hash=generate_password_hash("Pass@123"),
            role="user",
            is_verified=True,
            email_verified=True
        )
        db.session.add(user)
    
    admin = User.query.filter_by(email="testadmin_check@example.com").first()
    if not admin:
        admin = User(
            name="Test Check Admin",
            email="testadmin_check@example.com",
            password_hash=generate_password_hash("Pass@123"),
            role="admin",
            is_verified=True,
            email_verified=True
        )
        db.session.add(admin)
    
    # Check if there is published news and pending news
    pub_news = News.query.filter_by(status="PUBLISHED").first()
    if not pub_news:
        pub_news = News(
            user_id=user.id if user.id else 1,
            title="Sample Published News For Check",
            category="Technology",
            location="Global",
            additional_description="Tech update",
            ai_headline="Sample Published News For Check",
            ai_summary="Summary of tech update",
            ai_article="Full article about tech update.",
            status="PUBLISHED",
            is_breaking=True,
            is_featured=True
        )
        db.session.add(pub_news)
    
    pend_news = News.query.filter(News.status == "NEEDS_INFORMATION").first()
    if not pend_news:
        pend_news = News(
            user_id=user.id if user.id else 1,
            title="Sample Needs Info News For Check",
            category="Business",
            location="Local",
            additional_description="Business update",
            ai_headline="Sample Needs Info News For Check",
            ai_summary="Summary of biz update",
            ai_article="Full article about biz update.",
            status="NEEDS_INFORMATION",
            admin_comment="Please provide source URL and more details"
        )
        db.session.add(pend_news)
    else:
        pend_news.user_id = user.id
        pend_news.admin_comment = "Please provide source URL and more details"
    
    db.session.commit()
    
    pub_id = pub_news.id
    pend_id = pend_news.id
    u_id = user.id
    u_name = user.name
    u_email = user.email
    a_id = admin.id
    a_name = admin.name
    a_email = admin.email

client = app.test_client()

print("\n--- 1. Testing Unauthenticated Public Routes ---")
public_routes = [
    ("/", 200),
    ("/latest", 200),
    ("/latest-news", 200),
    ("/breaking", 200),
    ("/breaking-news", 200),
    ("/featured", 200),
    ("/featured-news", 200),
    ("/categories", 200),
    ("/categories?category=Technology", 200),
    ("/about", 200),
    (f"/news/{pub_id}", 200),
    ("/login", 200),
    ("/user/login", 200),
    ("/admin-login", 200),
    ("/admin/login", 200),
    ("/register", 200),
    ("/user/dashboard", 302),
    ("/user/submit-news", 302),
    ("/user/my-news", 302),
    ("/admin/dashboard", 302),
]

for url, expected in public_routes:
    res = client.get(url)
    status_icon = "[OK]" if res.status_code == expected else f"[FAIL] (Got {res.status_code}, expected {expected})"
    print(f"Public GET {url:<35} -> {res.status_code} {status_icon}")
    if res.status_code == 500:
        print(res.data.decode('utf-8')[:300])

print("\n--- 2. Testing Logged-in User Routes ---")
with client.session_transaction() as sess:
    sess["user_id"] = u_id
    sess["user_role"] = "user"
    sess["user_name"] = u_name
    sess["user_email"] = u_email

user_routes = [
    ("/", 200),
    ("/latest", 200),
    ("/breaking", 200),
    ("/featured", 200),
    ("/categories", 200),
    ("/about", 200),
    (f"/news/{pub_id}", 200),
    ("/user/dashboard", 200),
    ("/user/submit-news", 200),
    ("/user/my-news", 200),
    (f"/user/news/{pend_id}", 200),
    (f"/user/news/{pend_id}/provide-info", 200),
    ("/admin/dashboard", 403),
]

for url, expected in user_routes:
    res = client.get(url)
    status_icon = "[OK]" if res.status_code == expected else f"[FAIL] (Got {res.status_code}, expected {expected})"
    print(f"User GET {url:<35} -> {res.status_code} {status_icon}")
    if res.status_code == 500:
        print(res.data.decode('utf-8')[:300])

print("\n--- 3. Testing Logged-in Admin Routes ---")
with client.session_transaction() as sess:
    sess["user_id"] = a_id
    sess["user_role"] = "admin"
    sess["user_name"] = a_name
    sess["user_email"] = a_email

admin_routes = [
    ("/", 200),
    ("/latest", 200),
    ("/breaking", 200),
    ("/featured", 200),
    ("/categories", 200),
    ("/about", 200),
    (f"/news/{pub_id}", 200),
    ("/admin/dashboard", 200),
    (f"/admin/news/{pend_id}/review", 200),
    (f"/admin/news/{pend_id}/edit", 200),
]

for url, expected in admin_routes:
    res = client.get(url)
    status_icon = "[OK]" if res.status_code == expected else f"[FAIL] (Got {res.status_code}, expected {expected})"
    print(f"Admin GET {url:<35} -> {res.status_code} {status_icon}")
    if res.status_code == 500:
        print(res.data.decode('utf-8')[:300])
