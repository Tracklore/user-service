"""Test utilities and fixtures for the user service tests."""

import pytest
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.badge import Badge
from app.models.learning_goal import LearningGoal
from app.schemas.badge import BadgeCreate
from app.schemas.learning_goal import LearningGoalCreate


# Sample test data
SAMPLE_USER_ID = 1
SAMPLE_USER_DATA = {
    "id": SAMPLE_USER_ID,
    "username": "testuser",
    "email": "test@example.com"
}

SAMPLE_BADGE_DATA = {
    "name": "Test Badge",
    "description": "A test badge for testing purposes",
    "icon_url": "http://example.com/badge.png"
}

SAMPLE_LEARNING_GOAL_DATA = {
    "title": "Test Learning Goal",
    "description": "A test learning goal for testing purposes",
    "status": "in-progress",
    "streak_count": 5
}


@pytest.fixture
def mock_db_session():
    """Create a mock database session for testing."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def sample_user_data():
    """Sample user data from auth service."""
    return SAMPLE_USER_DATA.copy()


@pytest.fixture
def sample_badge_create():
    """Sample badge create schema."""
    return BadgeCreate(**SAMPLE_BADGE_DATA)


@pytest.fixture
def sample_learning_goal_create():
    """Sample learning goal create schema."""
    return LearningGoalCreate(**SAMPLE_LEARNING_GOAL_DATA)


@pytest.fixture
def sample_badge():
    """Sample badge model instance."""
    return Badge(
        id=1,
        **SAMPLE_BADGE_DATA,
        auth_user_id=SAMPLE_USER_ID
    )


@pytest.fixture
def sample_learning_goal():
    """Sample learning goal model instance."""
    return LearningGoal(
        id=1,
        **SAMPLE_LEARNING_GOAL_DATA,
        auth_user_id=SAMPLE_USER_ID
    )


def create_mock_db_result(scalars_return_value=None, scalar_one_return_value=None, 
                         scalar_one_or_none_return_value=None, fetchone_return_value=None):
    """Create a mock database result object."""
    mock_result = AsyncMock()
    if scalars_return_value is not None:
        mock_result.scalars().all.return_value = scalars_return_value
        mock_result.scalars().first.return_value = scalars_return_value[0] if scalars_return_value else None
    if scalar_one_return_value is not None:
        mock_result.scalar_one.return_value = scalar_one_return_value
    if scalar_one_or_none_return_value is not None:
        mock_result.scalar_one_or_none.return_value = scalar_one_or_none_return_value
    if fetchone_return_value is not None:
        mock_result.fetchone.return_value = fetchone_return_value
    return mock_result