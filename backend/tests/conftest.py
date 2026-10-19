import uuid

import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token, hash_password
from app.db import Base, get_db
from app.main import app
from app.models.business import Business
from app.models.membership import BusinessMembership
from app.models.permissions import Permission
from app.models.roles import Role
from app.models.users import User


TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=test_engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_business(db_session):
    business = Business(
        name="Test Salon",
        email="test@example.com",
    )

    db_session.add(business)
    db_session.commit()
    db_session.refresh(business)

    return business


@pytest.fixture
def admin_user(db_session, test_business):
    permissions = [
        Permission(
            code="customers:read",
            description="View customers",
        ),
        Permission(
            code="customers:create",
            description="Create customers",
        ),
        Permission(
            code="customers:update",
            description="Update customers",
        ),
        Permission(
            code="customers:delete",
            description="Delete customers",
        ),

            Permission(
            code="services:read",
            description="View services",
        ),
        Permission(
            code="services:create",
            description="Create services",
        ),
        Permission(
            code="services:update",
            description="Update services",
        ),
        Permission(
            code="services:delete",
            description="Delete services",
        ),
        
        Permission(
            code="settings:manage",
            description="Manage settings",
        ),

         Permission(
            code="loyalty:read",
            description="View loyalty balances and history",
        ),
        Permission(
            code="loyalty:earn",
            description="Award loyalty points",
        ),
        Permission(
            code="loyalty:redeem",
            description="Redeem loyalty points",
        ),

        Permission(
    code="workers:read",
    description="View workers",
        ),
        Permission(
            code="workers:create",
            description="Create workers",
        ),
        Permission(
            code="workers:update",
            description="Update workers",
        ),
        Permission(
            code="workers:delete",
            description="Delete workers",
        ),

        Permission(
            code="expenses:read",
            description="View expenses",
        ),
        Permission(
            code="expenses:create",
            description="Create expenses",
        ),
        Permission(
            code="expenses:update",
            description="Update expenses",
        ),
        Permission(
            code="expenses:delete",
            description="Delete expenses",
        ),

                Permission(
            code="payments:read",
            description="View payments and collection reports",
        ),
        Permission(
            code="payments:create",
            description="Record customer payments",
        ),

        Permission(
    code="loyalty:manage",
    description="Manage loyalty settings",
),


    Permission(code="appointments:read", description="View appointments"),
    Permission(code="appointments:create", description="Create appointments"),
    Permission(code="appointments:update", description="Update appointments"),
    Permission(code="appointments:delete", description="Delete appointments"),
]

    db_session.add_all(permissions)
    db_session.flush()

    admin_role = Role(
        name=f"ADMIN-{uuid.uuid4()}",
        description="Test administrator",
    )

    admin_role.permissions = permissions

    db_session.add(admin_role)
    db_session.flush()

    user = User(
        email=f"admin-{uuid.uuid4()}@example.com",
        password_hash=hash_password("TestPassword123!"),
        first_name="Test",
        last_name="Admin",
        is_active=True,
    )

    db_session.add(user)
    db_session.flush()

    membership = BusinessMembership(
        user_id=user.id,
        business_id=test_business.id,
        role_id=admin_role.id,
    )

    db_session.add(membership)
    db_session.commit()

    db_session.refresh(user)

    return user


@pytest.fixture
def auth_headers(admin_user):
    token = create_access_token(admin_user.id)

    return {
        "Authorization": f"Bearer {token}",
    }