import pytest
from datetime import datetime
from app.models.badge import Badge
from app.models.learning_goal import LearningGoal
from app.models.auth_user_reference import AuthUserReference
from tests.test_utils import SAMPLE_USER_ID, SAMPLE_BADGE_DATA, SAMPLE_LEARNING_GOAL_DATA


def test_auth_user_reference_model():
    """Test the AuthUserReference model."""
    # Create an instance
    auth_user_ref = AuthUserReference(id=SAMPLE_USER_ID)
    
    # Verify attributes
    assert auth_user_ref.id == SAMPLE_USER_ID
    assert auth_user_ref.__tablename__ == "auth_users"


def test_badge_model():
    """Test the Badge model."""
    # Create an instance with minimal data
    badge = Badge(
        id=1,
        name="Test Badge",
        description="Test Description",
        icon_url="http://example.com/icon.png",
        auth_user_id=SAMPLE_USER_ID
    )
    
    # Verify attributes
    assert badge.id == 1
    assert badge.name == "Test Badge"
    assert badge.description == "Test Description"
    assert badge.icon_url == "http://example.com/icon.png"
    assert badge.auth_user_id == SAMPLE_USER_ID
    assert badge.__tablename__ == "badges"
    
    # Verify date_achieved is set by default
    assert isinstance(badge.date_achieved, datetime)
    
    # Create an instance with explicit date_achieved
    specific_date = datetime(2023, 1, 1, 12, 0, 0)
    badge_with_date = Badge(
        id=2,
        name="Test Badge 2",
        description="Test Description 2",
        icon_url="http://example.com/icon2.png",
        date_achieved=specific_date,
        auth_user_id=SAMPLE_USER_ID
    )
    
    # Verify explicit date_achieved
    assert badge_with_date.date_achieved == specific_date


def test_learning_goal_model():
    """Test the LearningGoal model."""
    # Create an instance with minimal data
    goal = LearningGoal(
        id=1,
        title="Test Goal",
        description="Test Description",
        status="in-progress",
        streak_count=5,
        auth_user_id=SAMPLE_USER_ID
    )
    
    # Verify attributes
    assert goal.id == 1
    assert goal.title == "Test Goal"
    assert goal.description == "Test Description"
    assert goal.status == "in-progress"
    assert goal.streak_count == 5
    assert goal.auth_user_id == SAMPLE_USER_ID
    assert goal.__tablename__ == "learning_goals"
    
    # Create an instance with None description
    goal_no_desc = LearningGoal(
        id=2,
        title="Test Goal 2",
        status="completed",
        streak_count=10,
        auth_user_id=SAMPLE_USER_ID
    )
    
    # Verify None description
    assert goal_no_desc.description is None


def test_model_repr():
    """Test the string representation of models."""
    # Test AuthUserReference repr
    auth_user_ref = AuthUserReference(id=SAMPLE_USER_ID)
    assert repr(auth_user_ref) == f"<AuthUserReference(id={SAMPLE_USER_ID})>"
    
    # Test Badge repr
    badge = Badge(
        id=1,
        name="Test Badge",
        description="Test Description",
        icon_url="http://example.com/icon.png",
        auth_user_id=SAMPLE_USER_ID
    )
    assert "Test Badge" in repr(badge)
    assert "1" in repr(badge)
    
    # Test LearningGoal repr
    goal = LearningGoal(
        id=1,
        title="Test Goal",
        description="Test Description",
        status="in-progress",
        streak_count=5,
        auth_user_id=SAMPLE_USER_ID
    )
    assert "Test Goal" in repr(goal)
    assert "1" in repr(goal)


def test_model_relationships():
    """Test model relationships and foreign keys."""
    # Test Badge foreign key relationship
    badge = Badge(
        id=1,
        name="Test Badge",
        description="Test Description",
        icon_url="http://example.com/icon.png",
        auth_user_id=SAMPLE_USER_ID
    )
    assert hasattr(badge, 'auth_user_id')
    assert badge.auth_user_id == SAMPLE_USER_ID
    
    # Test LearningGoal foreign key relationship
    goal = LearningGoal(
        id=1,
        title="Test Goal",
        description="Test Description",
        status="in-progress",
        streak_count=5,
        auth_user_id=SAMPLE_USER_ID
    )
    assert hasattr(goal, 'auth_user_id')
    assert goal.auth_user_id == SAMPLE_USER_ID


def test_model_defaults():
    """Test model default values."""
    # Test Badge default date_achieved
    badge = Badge(
        name="Test Badge",
        description="Test Description",
        icon_url="http://example.com/icon.png",
        auth_user_id=SAMPLE_USER_ID
    )
    assert badge.date_achieved is not None
    assert isinstance(badge.date_achieved, datetime)
    
    # Test LearningGoal default streak_count
    goal = LearningGoal(
        title="Test Goal",
        description="Test Description",
        status="in-progress",
        auth_user_id=SAMPLE_USER_ID
    )
    assert goal.streak_count == 0


def test_model_validation():
    """Test model validation through Pydantic schemas."""
    from app.schemas.badge import BadgeCreate
    from app.schemas.learning_goal import LearningGoalCreate
    
    # Test BadgeCreate validation
    badge_create = BadgeCreate(**SAMPLE_BADGE_DATA)
    assert badge_create.name == SAMPLE_BADGE_DATA["name"]
    assert badge_create.description == SAMPLE_BADGE_DATA["description"]
    assert badge_create.icon_url == SAMPLE_BADGE_DATA["icon_url"]
    
    # Test LearningGoalCreate validation
    goal_create = LearningGoalCreate(**SAMPLE_LEARNING_GOAL_DATA)
    assert goal_create.title == SAMPLE_LEARNING_GOAL_DATA["title"]
    assert goal_create.description == SAMPLE_LEARNING_GOAL_DATA["description"]
    assert goal_create.status == SAMPLE_LEARNING_GOAL_DATA["status"]
    assert goal_create.streak_count == SAMPLE_LEARNING_GOAL_DATA["streak_count"]


def test_model_to_dict():
    """Test converting models to dictionary."""
    # Test Badge to_dict
    badge = Badge(
        id=1,
        name="Test Badge",
        description="Test Description",
        icon_url="http://example.com/icon.png",
        auth_user_id=SAMPLE_USER_ID
    )
    
    # Test LearningGoal to_dict
    goal = LearningGoal(
        id=1,
        title="Test Goal",
        description="Test Description",
        status="in-progress",
        streak_count=5,
        auth_user_id=SAMPLE_USER_ID
    )