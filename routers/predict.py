import logging

from fastapi import APIRouter, HTTPException, status

from repositories.moderation import ModerationRulesRepository
from schemas import ErrorResponse, PredictRequest, ValidationErrorResponse
from services.moderation import ModerationService

router = APIRouter()
logger = logging.getLogger(__name__)
moderation = ModerationService(ModerationRulesRepository())


@router.post(
    "/predict",
    response_description="true при нарушении, false при его отсутствии",
    responses={
        400: {"model": ValidationErrorResponse, "description": "Некорректный запрос"},
        "4XX": {"model": ErrorResponse, "description": "Другая ошибка клиента"},
        500: {"model": ErrorResponse, "description": "Ошибка модерации"},
    },
)
def predict(ad: PredictRequest) -> bool:
    try:
        return moderation.has_violation(ad.is_verified_seller, ad.images_qty)
    except Exception as exc:
        logger.exception("Ошибка при проверке объявления")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось проверить объявление",
        ) from exc
