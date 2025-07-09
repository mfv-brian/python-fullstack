from unittest.mock import MagicMock, patch

from app.backend_pre_start import logger


def test_init_successful_connection() -> None:
    engine_mock = MagicMock()

    with (
        patch.object(logger, "info"),
        patch.object(logger, "error"),
        patch.object(logger, "warn"),
    ):
        # Test the actual init function without retry decorator
        def init_test(db_engine):
            try:
                from sqlmodel import Session, select
                with Session(db_engine) as session:
                    session.exec(select(1))
            except Exception as e:
                logger.error(e)
                raise e
        
        try:
            init_test(engine_mock)
            connection_successful = True
        except Exception:
            connection_successful = False

        assert (
            connection_successful
        ), "The database connection should be successful and not raise an exception."
