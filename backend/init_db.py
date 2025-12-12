"""
Initialize database and create tables
"""
from app.database import Base, engine
from app.models import User, Conversation, Message
import uuid
from datetime import datetime
from passlib.context import CryptContext

# Password hashing - use pbkdf2_sha256 (more compatible)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def init_database():
    """Create all tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created!")

def seed_sample_data():
    """Seed database with sample data"""
    from app.database import SessionLocal
    from app.models.user import OAuthProvider
    
    db = SessionLocal()
    
    try:
        # Create sample user
        user = db.query(User).filter(User.email == "test@jarvisx.com").first()
        if not user:
            # Hash password
            password = "test123456"
            password_hash = pwd_context.hash(password)
            
            user = User(
                id=uuid.uuid4(),
                email="test@jarvisx.com",
                username="testuser",
                password_hash=password_hash,
                is_active="true",
                is_verified="true",
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"✅ Created test user: {user.email}")
        else:
            print(f"ℹ️  Test user already exists: {user.email}")
        
        # Create sample conversation
        conversation = db.query(Conversation).filter(
            Conversation.user_id == user.id
        ).first()
        
        if not conversation:
            conversation = Conversation(
                id=uuid.uuid4(),
                user_id=user.id,
                title="Welcome Conversation",
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            print(f"✅ Created sample conversation")
            
            # Add sample messages
            messages = [
                Message(
                    id=uuid.uuid4(),
                    conversation_id=conversation.id,
                    role="user",
                    content="Hello, JarvisX!",
                    created_at=datetime.utcnow(),
                ),
                Message(
                    id=uuid.uuid4(),
                    conversation_id=conversation.id,
                    role="assistant",
                    content="Hello! I'm JarvisX V2, your AI assistant. How can I help you today?",
                    created_at=datetime.utcnow(),
                ),
            ]
            
            for msg in messages:
                db.add(msg)
            db.commit()
            print(f"✅ Created sample messages")
        else:
            print(f"ℹ️  Sample conversation already exists")
        
        print("\n✅ Sample data seeded successfully!")
        print(f"\n📋 Test Credentials:")
        print(f"   Email: test@jarvisx.com")
        print(f"   Password: test123456")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
    seed_sample_data()
