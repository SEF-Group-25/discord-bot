import pytest
import arrow
import dateutil.parser
import asyncio
from unittest.mock import patch, AsyncMock
import discord
from bot.exts.moderation.infraction._scheduler import InfractionScheduler


# --- Fake Dependencies for Testing ---

class FakeResponse:
    def __init__(self, status, reason=""):
        self.status = status
        self.reason = reason


class FakeScheduler:
    def __init__(self):
        self.cancelled = []

    def cancel(self, id_):
        self.cancelled.append(id_)

class FakeAPIClient:
    """A fake API client with a patch method that simulates a successful API call."""
    async def patch(self, url, json):
        return {"patched": True}

    async def get(self, url, params=None):
        return []

class FakeGuild:
    """A fake guild that returns a fake moderator role."""
    def get_role(self, role_id):
        class FakeRole:
            mention = f"<@&{role_id}>"
        return FakeRole()

class FakeUser:
    """A fake user with a display avatar URL."""
    def __init__(self, user_id):
        self.id = user_id

        self.display_avatar = type("FakeAvatar", (), {"url": "http://avatar.url"})()

class FakeBot:
    """A fake bot that provides minimal implementations required by the scheduler."""
    def __init__(self):
        self.api_client = FakeAPIClient()
        self.user = FakeUser(2222)  

    def get_guild(self, guild_id):
        return FakeGuild()

    def get_user(self, user_id):
        return FakeUser(user_id)

    def get_cog(self, name):
        # Return None or a fake cog if needed.
        return None

class InfractionSchedulerTestHelper(InfractionScheduler):

    async def _pardon_action(self, infraction, notify):
        """
        Dummy implementation that simulates performing deactivation actions.
        Returns a log dict that will be merged with the initial log.
        """
        return {"PardonInfo": "Test log"}

# Subclass for an unsupported infraction type (returns None).
class UnsupportedTypeScheduler(InfractionScheduler):
    async def _pardon_action(self, infraction, notify):
        # Returning None triggers a ValueError in deactivate_infraction
        return None

# Subclass that simulates discord.Forbidden
class ForbiddenScheduler(InfractionScheduler):
    async def _pardon_action(self, infraction, notify):
        response_403 = FakeResponse(403, "Forbidden")
        raise discord.Forbidden(response_403, "Missing permissions.")

#  Subclass that simulates discord.HTTPException (404 or code=10007)
class HTTP404Scheduler(InfractionScheduler):
    async def _pardon_action(self, infraction, notify):
        response_404 = FakeResponse(404, "Not Found")
        error = discord.HTTPException(response_404, "Some message")
        error.code = 10007  # e.g. "Unknown Member"
        raise error


@pytest.mark.asyncio
async def test_deactivate_infraction_pardon_reason():
    """
    Checks if "Pardoned: Test pardon" is included
    in the patch call, but not in the returned log_text["Reason"].
    """
    bot = FakeBot()
    scheduler_instance = InfractionSchedulerTestHelper(
        bot,
        supported_infractions={"ban", "kick", "note", "warning"}
    )
    fake_scheduler = FakeScheduler()
    scheduler_instance.scheduler = fake_scheduler

    infraction = {
        "id": "123",
        "user": 1111,
        "actor": 2222,
        "type": "ban",
        "reason": "Original reason",
        "inserted_at": "2023-01-01T00:00:00Z",
        "expires_at": "2025-01-01T00:00:00Z"
    }

    with patch.object(bot.api_client, 'patch', new_callable=AsyncMock) as mock_patch:
        log_text = await scheduler_instance.deactivate_infraction(
            infraction,
            pardon_reason="Test pardon",
            send_log=False,
            notify=False
        )

    mock_patch.assert_awaited_once()
    args, kwargs = mock_patch.call_args
    assert "123" in args[0], "Should PATCH the correct infraction ID"
    assert "reason" in kwargs["json"], "Should include 'reason' in the patch data"
    updated_reason = kwargs["json"]["reason"]
    assert "Original reason" in updated_reason
    assert "Pardoned: Test pardon" in updated_reason

    assert "Original reason" in log_text["Reason"]


@pytest.mark.asyncio
async def test_deactivate_infraction_unsupported_type_raises_value_error():
    """
    Test that if _pardon_action returns None (unsupported type),
    deactivate_infraction raises a ValueError.
    """
    bot = FakeBot()
    scheduler_instance = UnsupportedTypeScheduler(
        bot,
        supported_infractions={"ban", "kick", "note", "warning"}
    )
    infraction = {
        "id": "999",
        "user": 1111,
        "actor": 2222,
        "type": "some_unsupported_type",
        "reason": "Some reason",
        "inserted_at": "2023-01-01T00:00:00Z",
        "expires_at": "2025-01-01T00:00:00Z"
    }

    with pytest.raises(ValueError) as exc_info:
        await scheduler_instance.deactivate_infraction(
            infraction,
            pardon_reason="Irrelevant",
            send_log=False,
            notify=False
        )

    assert "unsupported infraction" in str(exc_info.value)


@pytest.mark.asyncio
async def test_deactivate_infraction_discord_forbidden():
    """
    Test that if _pardon_action raises discord.Forbidden,
    we get a 'Failure' key in the returned log_text indicating missing permissions.
    """
    bot = FakeBot()
    scheduler_instance = ForbiddenScheduler(
        bot,
        supported_infractions={"ban", "kick", "note", "warning"}
    )
    infraction = {
        "id": "777",
        "user": 1111,
        "actor": 2222,
        "type": "ban",
        "reason": "Test reason",
        "inserted_at": "2023-01-01T00:00:00Z",
        "expires_at": "2025-01-01T00:00:00Z"
    }

    log_text = await scheduler_instance.deactivate_infraction(
        infraction,
        pardon_reason="Irrelevant",
        send_log=False,
        notify=False
    )

    assert "Failure" in log_text, "Should indicate failure due to Forbidden"
    assert "permissions" in log_text["Failure"], "Should mention lacking permissions"


@pytest.mark.asyncio
async def test_deactivate_infraction_discord_http_404():
    """
    Test that if _pardon_action raises discord.HTTPException with status=404 or code=10007,
    we interpret it as the user having left the guild, and log 'Failure: User left the guild.'.
    """
    bot = FakeBot()
    scheduler_instance = HTTP404Scheduler(
        bot,
        supported_infractions={"ban", "kick", "note", "warning"}
    )
    infraction = {
        "id": "888",
        "user": 1111,
        "actor": 2222,
        "type": "ban",
        "reason": "Test reason",
        "inserted_at": "2023-01-01T00:00:00Z",
        "expires_at": "2025-01-01T00:00:00Z"
    }

    log_text = await scheduler_instance.deactivate_infraction(
        infraction,
        pardon_reason="Irrelevant",
        send_log=False,
        notify=False
    )

    assert "Failure" in log_text, "Should indicate failure due to HTTPException 404"
    assert "left the guild" in log_text["Failure"], "Should mention user left the guild"