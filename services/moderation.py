from repositories.moderation import ModerationRulesRepository


class ModerationService:
    def __init__(self, rules: ModerationRulesRepository) -> None:
        self.rules = rules

    def has_violation(self, is_verified_seller: bool, images_qty: int) -> bool:
        if is_verified_seller:
            return False

        return images_qty < self.rules.minimum_images_for_unverified_seller()
