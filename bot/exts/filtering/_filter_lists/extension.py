from __future__ import annotations

import typing
from os.path import splitext

import bot
from bot.constants import Channels
from bot.exts.filtering._filter_context import Event, FilterContext
from bot.exts.filtering._filter_lists.filter_list import FilterList, ListType
from bot.exts.filtering._filters.extension import ExtensionFilter
from bot.exts.filtering._filters.filter import Filter
from bot.exts.filtering._settings import ActionSettings

if typing.TYPE_CHECKING:
    from bot.exts.filtering.filtering import Filtering

PASTE_URL = "https://paste.pythondiscord.com"
PY_EMBED_DESCRIPTION = (
    "It looks like you tried to attach a Python file - "
    f"please use a code-pasting service such as {PASTE_URL}"
)

TXT_LIKE_FILES = {".txt", ".csv", ".json"}
TXT_EMBED_DESCRIPTION = (
    "You either uploaded a `{blocked_extension}` file or entered a message that was too long. "
    f"Please use our [paste bin]({PASTE_URL}) instead."
)

DISALLOWED_EMBED_DESCRIPTION = (
    "It looks like you tried to attach file type(s) that we do not allow ({joined_blacklist}). "
    "We currently allow the following file types: **{joined_whitelist}**.\n\n"
    "Feel free to ask in {meta_channel_mention} if you think this is a mistake."
)


class ExtensionsList(FilterList[ExtensionFilter]):
    """
    A list of filters, each looking for a file attachment with a specific extension.

    If an extension is not explicitly allowed, it will be blocked.

    Whitelist defaults dictate what happens when an extension is *not* explicitly allowed,
    and whitelist filters overrides have no effect.

    Items should be added as file extensions preceded by a dot.
    """

    name = "extension"

    def __init__(self, filtering_cog: Filtering):
        super().__init__()
        filtering_cog.subscribe(self, Event.MESSAGE, Event.SNEKBOX)
        self._whitelisted_description = None

    def get_filter_type(self, content: str) -> type[Filter]:
        """Get a subclass of filter matching the filter list and the filter's content."""
        return ExtensionFilter

    @property
    def filter_types(self) -> set[type[Filter]]:
        """Return the types of filters used by this list."""
        return {ExtensionFilter}

    async def actions_for(
        self, ctx: FilterContext
    ) -> tuple[ActionSettings | None, list[str], dict[ListType, list[Filter]]]:
        """Dispatch the given event to the list's filters, and return actions to take and messages to relay to mods."""
        if not ctx.message or not ctx.attachments:
            return None, [], {}

        _, failed = self[ListType.ALLOW].defaults.validations.evaluate(ctx)
        if failed:
            return None, [], {}

        all_ext = self._get_all_extensions(ctx)
        triggered, allowed_ext = await self._get_triggered_filters_and_allowed_ext(ctx, all_ext)
        not_allowed = self._compute_not_allowed_extensions(ctx, all_ext, allowed_ext)

        if not not_allowed:
            return None, [], {ListType.ALLOW: triggered}

        if ctx.event != Event.SNEKBOX:
            self._set_dm_embed(ctx, not_allowed)

        ctx.matches += not_allowed.values()
        ctx.blocked_exts |= set(not_allowed)
        actions = self[ListType.ALLOW].defaults.actions if ctx.event != Event.SNEKBOX else None
        return actions, [f"`{ext}`" if ext else "`No Extension`" for ext in not_allowed], {ListType.ALLOW: triggered}

    def _get_all_extensions(self, ctx: FilterContext) -> set[tuple[str, str]]:
        """Extract file extensions from the attachments."""
        return {(splitext(attachment.filename.lower())[1], attachment.filename) for attachment in ctx.attachments}

    async def _get_triggered_filters_and_allowed_ext(
        self, ctx: FilterContext, all_ext: set[tuple[str, str]]
    ) -> tuple[list[Filter], set[str]]:
        """Return the list of triggered filters and the allowed extensions."""
        new_ctx = ctx.replace(content={ext for ext, _ in all_ext})
        triggered = [
            filter_ for filter_ in self[ListType.ALLOW].filters.values() if await filter_.triggered_on(new_ctx)
        ]
        allowed_ext = {filter_.content for filter_ in triggered}
        return triggered, allowed_ext

    def _compute_not_allowed_extensions(
        self, ctx: FilterContext, all_ext: set[tuple[str, str]], allowed_ext: set[str]
    ) -> dict[str, str]:
        """Compute extensions in the message that are not allowed."""
        not_allowed = {ext: filename for ext, filename in all_ext if ext not in allowed_ext}
        if ctx.event == Event.SNEKBOX:
            not_allowed = {ext: filename for ext, filename in not_allowed.items() if ext not in TXT_LIKE_FILES}
        return not_allowed

    def _set_dm_embed(self, ctx: FilterContext, not_allowed: dict[str, str]) -> None:
        """Set the DM embed on the context based on which extensions were disallowed."""
        if ".py" in not_allowed:
            ctx.dm_embed = PY_EMBED_DESCRIPTION
        elif txt_extensions := {ext for ext in TXT_LIKE_FILES if ext in not_allowed}:
            ctx.dm_embed = TXT_EMBED_DESCRIPTION.format(blocked_extension=txt_extensions.pop())
        else:
            meta_channel = bot.instance.get_channel(Channels.meta)
            if not self._whitelisted_description:
                self._whitelisted_description = ", ".join(
                    filter_.content for filter_ in self[ListType.ALLOW].filters.values()
                )
            ctx.dm_embed = DISALLOWED_EMBED_DESCRIPTION.format(
                joined_whitelist=self._whitelisted_description,
                joined_blacklist=", ".join(not_allowed),
                meta_channel_mention=meta_channel.mention,
            )
