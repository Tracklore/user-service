import pytest
from pydantic import ValidationError
from app.schemas.badge import BadgeCreate, Badge
from app.schemas.learning_goal import LearningGoalCreate, LearningGoalUpdate, LearningGoal
from tests.test_utils import SAMPLE_USER_ID, SAMPLE_BADGE_DATA, SAMPLE_LEARNING_GOAL_DATA


def test_badge_create_validation():
    """Test validation for BadgeCreate schema."""
    # Valid data should pass
    badge_create = BadgeCreate(**SAMPLE_BADGE_DATA)
    assert badge_create.name == SAMPLE_BADGE_DATA["name"]
    assert badge_create.description == SAMPLE_BADGE_DATA["description"]
    assert badge_create.icon_url == SAMPLE_BADGE_DATA["icon_url"]
    
    # Empty name should fail
    invalid_data = SAMPLE_BADGE_DATA.copy()
    invalid_data["name"] = ""
    with pytest.raises(ValidationError):
        BadgeCreate(**invalid_data)
    
    # Name too long should fail
    invalid_data = SAMPLE_BADGE_DATA.copy()
    invalid_data["name"] = "A" * 101  # Exceeds max length of 100
    with pytest.raises(ValidationError):
        BadgeCreate(**invalid_data)
    
    # Empty description should fail
    invalid_data = SAMPLE_BADGE_DATA.copy()
    invalid_data["description"] = ""
    with pytest.raises(ValidationError):
        BadgeCreate(**invalid_data)
    
    # Description too long should fail
    invalid_data = SAMPLE_BADGE_DATA.copy()
    invalid_data["description"] = "A" * 501  # Exceeds max length of 500
    with pytest.raises(ValidationError):
        BadgeCreate(**invalid_data)
    
    # Empty icon_url should fail
    invalid_data = SAMPLE_BADGE_DATA.copy()
    invalid_data["icon_url"] = ""
    with pytest.raises(ValidationError):
        BadgeCreate(**invalid_data)
    
    # Icon URL too long should fail
    invalid_data = SAMPLE_BADGE_DATA.copy()
    invalid_data["icon_url"] = "http://example.com/" + "A" * 470  # Exceeds max length of 500
    with pytest.raises(ValidationError):
        BadgeCreate(**invalid_data)


def test_badge_validation():
    """Test validation for Badge schema."""
    from datetime import datetime
    
    # Valid data should pass
    badge_data = {
        "id": 1,
        "name": "Test Badge",
        "description": "Test Description",
        "icon_url": "http://example.com/icon.png",
        "date_achieved": datetime.now(),
        "auth_user_id": SAMPLE_USER_ID
    }
    
    badge = Badge(**badge_data)
    assert badge.id == 1
    assert badge.name == "Test Badge"
    assert badge.auth_user_id == SAMPLE_USER_ID
    
    # Missing id should fail
    invalid_data = badge_data.copy()
    del invalid_data["id"]
    with pytest.raises(ValidationError):
        Badge(**invalid_data)
    
    # Missing auth_user_id should fail
    invalid_data = badge_data.copy()
    del invalid_data["auth_user_id"]
    with pytest.raises(ValidationError):
        Badge(**invalid_data)


def test_learning_goal_create_validation():
    """Test validation for LearningGoalCreate schema."""
    # Valid data should pass
    goal_create = LearningGoalCreate(**SAMPLE_LEARNING_GOAL_DATA)
    assert goal_create.title == SAMPLE_LEARNING_GOAL_DATA["title"]
    assert goal_create.description == SAMPLE_LEARNING_GOAL_DATA["description"]
    assert goal_create.status == SAMPLE_LEARNING_GOAL_DATA["status"]
    assert goal_create.streak_count == SAMPLE_LEARNING_GOAL_DATA["streak_count"]
    
    # Empty title should fail
    invalid_data = SAMPLE_LEARNING_GOAL_DATA.copy()
    invalid_data["title"] = ""
    with pytest.raises(ValidationError):
        LearningGoalCreate(**invalid_data)
    
    # Title too long should fail
    invalid_data = SAMPLE_LEARNING_GOAL_DATA.copy()
    invalid_data["title"] = "A" * 201  # Exceeds max length of 200
    with pytest.raises(ValidationError):
        LearningGoalCreate(**invalid_data)
    
    # Description too long should fail
    invalid_data = SAMPLE_LEARNING_GOAL_DATA.copy()
    invalid_data["description"] = "A" * 1001  # Exceeds max length of 1000
    with pytest.raises(ValidationError):
        LearningGoalCreate(**invalid_data)
    
    # Empty status should fail
    invalid_data = SAMPLE_LEARNING_GOAL_DATA.copy()
    invalid_data["status"] = ""
    with pytest.raises(ValidationError):
        LearningGoalCreate(**invalid_data)
    
    # Status too long should fail
    invalid_data = SAMPLE_LEARNING_GOAL_DATA.copy()
    invalid_data["status"] = "A" * 51  # Exceeds max length of 50
    with pytest.raises(ValidationError):
        LearningGoalCreate(**invalid_data)
    
    # Negative streak_count should fail
    invalid_data = SAMPLE_LEARNING_GOAL_DATA.copy()
    invalid_data["streak_count"] = -1
    with pytest.raises(ValidationError):
        LearningGoalCreate(**invalid_data)


def test_learning_goal_update_validation():
    """Test validation for LearningGoalUpdate schema."""
    # Valid data should pass
    update_data = {
        "title": "Updated Title",
        "description": "Updated Description"
    }
    
    goal_update = LearningGoalUpdate(**update_data)
    assert goal_update.title == "Updated Title"
    assert goal_update.description == "Updated Description"
    
    # Empty title should fail
    invalid_data = {"title": ""}
    with pytest.raises(ValidationError):
        LearningGoalUpdate(**invalid_data)
    
    # Title too long should fail
    invalid_data = {"title": "A" * 201}  # Exceeds max length of 200
    with pytest.raises(ValidationError):
        LearningGoalUpdate(**invalid_data)
    
    # Description too long should fail
    invalid_data = {"description": "A" * 1001}  # Exceeds max length of 1000
    with pytest.raises(ValidationError):
        LearningGoalUpdate(**invalid_data)
    
    # Status too long should fail
    invalid_data = {"status": "A" * 51}  # Exceeds max length of 50
    with pytest.raises(ValidationError):
        LearningGoalUpdate(**invalid_data)
    
    # Negative streak_count should fail
    invalid_data = {"streak_count": -1}
    with pytest.raises(ValidationError):
        LearningGoalUpdate(**invalid_data)


def test_learning_goal_validation():
    """Test validation for LearningGoal schema."""
    # Valid data should pass
    goal_data = {
        "id": 1,
        "title": "Test Goal",
        "description": "Test Description",
        "status": "in-progress",
        "streak_count": 5,
        "auth_user_id": SAMPLE_USER_ID
    }
    
    goal = LearningGoal(**goal_data)
    assert goal.id == 1
    assert goal.title == "Test Goal"
    assert goal.auth_user_id == SAMPLE_USER_ID
    
    # Missing id should fail
    invalid_data = goal_data.copy()
    del invalid_data["id"]
    with pytest.raises(ValidationError):
        LearningGoal(**invalid_data)
    
    # Missing auth_user_id should fail
    invalid_data = goal_data.copy()
    del invalid_data["auth_user_id"]
    with pytest.raises(ValidationError):
        LearningGoal(**invalid_data)


def test_data_integrity_validation():
    """Test data integrity validation across related models."""
    from datetime import datetime
    
    # Test that badges and learning goals have proper user references
    badge_data = {
        "id": 1,
        "name": "Test Badge",
        "description": "Test Description",
        "icon_url": "http://example.com/icon.png",
        "date_achieved": datetime.now(),
        "auth_user_id": SAMPLE_USER_ID
    }
    
    badge = Badge(**badge_data)
    assert badge.auth_user_id == SAMPLE_USER_ID
    
    goal_data = {
        "id": 1,
        "title": "Test Goal",
        "description": "Test Description",
        "status": "in-progress",
        "streak_count": 5,
        "auth_user_id": SAMPLE_USER_ID
    }
    
    goal = LearningGoal(**goal_data)
    assert goal.auth_user_id == SAMPLE_USER_ID
    
    # Test that both models reference the same user when they should
    assert badge.auth_user_id == goal.auth_user_id


def test_optional_fields_validation():
    """Test validation of optional fields."""
    # Test badge with minimal required fields
    badge_data = {
        "name": "Test Badge",
        "description": "Test Description",
        "icon_url": "http://example.com/icon.png"
    }
    
    badge_create = BadgeCreate(**badge_data)
    assert badge_create.name == "Test Badge"
    
    # Test learning goal with optional description
    goal_data = {
        "title": "Test Goal",
        "status": "in-progress",
        "streak_count": 0
    }
    
    goal_create = LearningGoalCreate(**goal_data)
    assert goal_create.title == "Test Goal"
    assert goal_create.description is None  # Should default to None


def test_url_validation():
    """Test URL validation."""
    # Valid URLs should pass
    valid_urls = [
        "http://example.com",
        "https://example.com",
        "http://example.com/path",
        "https://example.com/path?query=value",
        "http://subdomain.example.com",
    ]
    
    for url in valid_urls:
        badge_data = {
            "name": "Test Badge",
            "description": "Test Description",
            "icon_url": url
        }
        
        # This should not raise an exception
        badge_create = BadgeCreate(**badge_data)
        assert badge_create.icon_url == url


def test_string_length_validation():
    """Test string length validation."""
    # Test exact boundary values
    badge_data = {
        "name": "A" * 100,  # Exactly 100 characters (max)
        "description": "B" * 500,  # Exactly 500 characters (max)
        "icon_url": "http://example.com/" + "C" * 473  # Exactly 500 characters total
    }
    
    # This should pass
    badge_create = BadgeCreate(**badge_data)
    assert len(badge_create.name) == 100
    assert len(badge_create.description) == 500
    assert len(badge_create.icon_url) == 500
    
    # Test learning goal boundary values
    goal_data = {
        "title": "A" * 200,  # Exactly 200 characters (max)
        "description": "B" * 1000,  # Exactly 1000 characters (max)
        "status": "C" * 50,  # Exactly 50 characters (max)
        "streak_count": 0
    }
    
    # This should pass
    goal_create = LearningGoalCreate(**goal_data)
    assert len(goal_create.title) == 200
    assert len(goal_create.description) == 1000
    assert len(goal_create.status) == 50


def test_numeric_validation():
    """Test numeric validation."""
    # Test maximum streak_count
    goal_data = {
        "title": "Test Goal",
        "status": "in-progress",
        "streak_count": 2147483647  # Max 32-bit integer
    }
    
    goal_create = LearningGoalCreate(**goal_data)
    assert goal_create.streak_count == 2147483647
    
    # Test zero streak_count
    goal_data["streak_count"] = 0
    goal_create = LearningGoalCreate(**goal_data)
    assert goal_create.streak_count == 0


def test_special_character_validation():
    """Test validation with special characters."""
    # Test with unicode characters
    badge_data = {
        "name": "テストバッジ",  # Japanese characters
        "description": "Special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?",
        "icon_url": "http://example.com/icon.png"
    }
    
    badge_create = BadgeCreate(**badge_data)
    assert badge_create.name == "テストバッジ"
    
    # Test with accented characters
    goal_data = {
        "title": "Étude des éléménts",
        "status": "in-progress",
        "streak_count": 5
    }
    
    goal_create = LearningGoalCreate(**goal_data)
    assert goal_create.title == "Étude des éléménts"