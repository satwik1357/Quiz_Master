# backend/init_db.py

from backend.models import db, User_Info


def setup_admin(app):
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()

        # Check if an admin already exists
        if not User_Info.query.first():
            full_name = "admin"
            email = "admin@gmail.com"
            password = "admin123"
            role = "0"
            address="Default Admin Address"
            pin_code="123456"

    

            new_admin = User_Info(
                full_name=full_name,
                email=email,
                password=password,
                role=role,
                address=address,
                pin_code=pin_code
            )

            db.session.add(new_admin)
            db.session.commit()
            print(f"✅ Admin user '{full_name}' has been created.")
        else:
            print("⚠️ Admin user already exists. Skipping creation.")
