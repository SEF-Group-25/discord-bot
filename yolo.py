#!/usr/bin/env python3
import asyncio
from unittest.mock import AsyncMock
import textwrap

# Dummy mark_branch function (if not already defined in your module)
def mark_branch(branch_id):
    with open("branch_count.log", "a") as f:
        f.write(f"branch {branch_id} executed\n")

# Dummy implementations for the minimal required attributes.
class DummyContext:
    async def send(self, message, allowed_mentions):
        print("Message sent:", message)

class DummyUser:
    mention = "DummyUserMention"
    id = 1234
    display_avatar = type("Avatar", (), {"url": "http://dummyurl/avatar.png"})

# Dummy infraction dictionary
dummy_infraction = {
    "type": "ban",
    "reason": "Test reason",
    "id": 1,
    "jump_url": "http://dummyurl/jump",
    "expires_at": "2025-01-01T00:00:00Z",  # use a fixed string for testing
    "last_applied": "2024-12-31T23:59:00Z",
    "hidden": False,
    "purge": "",
    "actor": 9999,
    "user": 1234,
}

# Dummy bot with a dummy API client
class DummyApiClient:
    async def get(self, endpoint, params):
        # Return a dummy list for mod channel branch.
        return [dummy_infraction]
    async def delete(self, endpoint):
        print(f"Deleted {endpoint}")

class DummyBot:
    async def wait_until_guild_available(self):
        pass
    def get_cog(self, name):
        return None
    api_client = DummyApiClient()

# Dummy Infractions class that contains the instrumented apply_infraction
# Here, import your actual Infractions class from your project.
# from bot.exts.moderation.infraction.infractions import Infractions
# For this demo, we'll define a dummy version that simply calls the instrumented function.
class DummyInfractions:
    def __init__(self, bot):
        self.bot = bot

    async def apply_infraction(
        self,
        ctx,
        infraction,
        user,
        action=AsyncMock(),  # dummy async action
        user_reason=None,
        additional_info="",
    ) -> bool:
        # Paste your instrumented apply_infraction function here.
        infr_type = infraction["type"]
        icon = "dummy_icon"
        reason = infraction["reason"]
        id_ = infraction["id"]
        jump_url = infraction["jump_url"]
        # For simplicity, use textwrap to simulate expiry formatting
        expiry = f"formatted({infraction['expires_at']}, {infraction['last_applied']})"

        if user_reason is None:
            mark_branch(1)
            user_reason = reason

        print(f"Applying {infr_type} infraction #{id_} to {user.mention}.")

        confirm_msg = ":ok_hand: applied"

        if infr_type in ("note", "warning"):
            mark_branch(2)
            expiry_msg = ""
        else:
            if expiry:
                mark_branch(22)
                expiry_msg = f" until {expiry}"
            else:
                expiry_msg = " permanently"

        dm_result = ""
        dm_log_text = ""
        expiry_log_text = f"\nExpires: {expiry}" if expiry else ""
        log_title = "applied"
        log_content = None
        failed = False

        if not infraction["hidden"] and infr_type in {"ban", "kick"}:
            mark_branch(3)
            # Simulate notify_infraction returning True
            if True:
                mark_branch(4)
                dm_result = ":incoming_envelope: "
                dm_log_text = "\nDM: Sent"
            else:
                dm_result = "failmail"
                dm_log_text = "\nDM: **Failed**"

        end_msg = ""
        # Simulate is_mod_channel always returning True for testing
        if True:
            mark_branch(5)
            # Simulate API client get call
            infractions = await self.bot.api_client.get("dummy_endpoint", params={"user__id": str(user.id)})
            total = len(infractions)
            end_msg = f" (#{id_} ; {total} infraction{'s' if total != 1 else ''} total)"
        elif infraction["actor"] == self.bot.get_cog("DummyBot"):
            mark_branch(6)
            if reason:
                mark_branch(7)
                end_msg = (
                    f" (reason: {textwrap.shorten(reason, width=1500, placeholder='...')})."
                    f"\n\nDummy moderator alert"
                )

        purge = infraction.get("purge", "")

        if action:
            mark_branch(8)
            try:
                mark_branch(9)
                await action()
                if expiry:
                    mark_branch(10)
                    print("Scheduled expiration")
            except Exception as e:
                mark_branch(11)
                confirm_msg = ":x: failed to apply"
                expiry_msg = ""
                log_content = ctx.author.mention if hasattr(ctx, "author") else "dummy_author"
                log_title = "failed to apply"
                if isinstance(e, Exception):
                    mark_branch(12)
                    print("Exception simulated: bot lacks permissions")
                failed = True

        if not failed:
            mark_branch(14)
            infr_message = f" **{purge}{infr_type}** to {user.mention}{expiry_msg}{end_msg}"
            if not infraction["hidden"] and infr_type not in {"ban", "kick"}:
                mark_branch(15)
                # Simulate notify_infraction for non-ban/kick returning True
                if True:
                    mark_branch(16)
                    dm_result = ":incoming_envelope: "
                    dm_log_text = "\nDM: Sent"
                else:
                    dm_result = "failmail"
                    dm_log_text = "\nDM: **Failed**"
                    if infr_type == "warning" and False:
                        mark_branch(17)
                        failed = True
                        log_title = "failed to apply"
                        additional_info += "\n*Failed to show the warning to the user*"
                        confirm_msg = f":x: Failed to apply warning to {user.mention} because DMing was unsuccessful"
        if failed:
            mark_branch(18)
            try:
                mark_branch(19)
                await self.bot.api_client.delete(f"dummy_endpoint/{id_}")
            except Exception as e:
                mark_branch(20)
                confirm_msg += " and failed to delete"
                log_title += " and failed to delete"
                print("Deletion failed with simulated error")
            infr_message = ""

        print(f"Sending confirmation message: {dm_result}{confirm_msg}{infr_message}")
        if jump_url is None:
            mark_branch(21)
            jump_url = "(Infraction issued in a ModMail channel.)"
        else:
            jump_url = f"[Click here.]({jump_url})"

        print(f"Log message: Icon: {icon}, Title: Infraction {log_title}: {infr_type}, Reason: {reason}, Jump URL: {jump_url}")
        return not failed

# Create dummy instances
dummy_bot = DummyBot()
infractions_obj = DummyInfractions(dummy_bot)
dummy_ctx = DummyContext()
dummy_user = DummyUser()

async def main():
    # Use a dummy async action that simply prints a message.
    async def dummy_action():
        print("dummy action executed")
    # Clear existing log file contents.
    open("branch_count.log", "w").close()
    result = await infractions_obj.apply_infraction(
        dummy_ctx,
        dummy_infraction,
        dummy_user,
        action=dummy_action,
        user_reason=None,
        additional_info="Test additional info"
    )
    print("Result:", result)
    with open("branch_count.log", "r") as f:
        print("Branch count log contents:")
        print(f.read())

asyncio.run(main())
