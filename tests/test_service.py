from unittest.mock import Mock

import pytest

from repositories.moderation import ModerationRulesRepository
from services.moderation import ModerationService


@pytest.mark.parametrize(("images_qty", "expected"), [(1, True), (2, False)])
def test_unverified_seller_uses_repository_threshold(images_qty, expected):
    rules = Mock(spec=ModerationRulesRepository)
    rules.minimum_images_for_unverified_seller.return_value = 2

    assert ModerationService(rules).has_violation(False, images_qty) is expected


def test_verified_seller_does_not_need_image_rule():
    rules = Mock(spec=ModerationRulesRepository)

    assert ModerationService(rules).has_violation(True, 0) is False
    rules.minimum_images_for_unverified_seller.assert_not_called()
