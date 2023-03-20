import typing
import discord
import inspect

from discord.ext import commands

if typing.TYPE_CHECKING:
    CommandList = typing.List[commands.Command[commands.Cog, ..., typing.Any]]
    CogMapping = typing.Dict[typing.Optional[commands.Cog], CommandList]


class SelectInfoCategories(discord.ui.Select):
    def __init__(self, mapping: 'CogMapping'):
        super().__init__(min_values=1, max_values=1)

        local_mapping: typing.Dict[str, CommandList] = {}
        for cog, commands in mapping.items():  # get the cog and its commands separately
            if len(commands) < 1:
                continue
            local_mapping[cog.qualified_name if cog else "No Category"] = commands
        self.mapping = local_mapping

        # Set the options that will be presented inside the dropdown
        for group in [("🛠️ Utils", "Utils"),
                      ("❓ No Category", "No Category"),
                      ("🎵 Music", "Music"),
                      ]:
            self.add_option(
                label=group[0],
                value=group[1])

    def _str_command(self, command: commands.Command):
        params = command.params.values()
        params = filter(
            lambda param:
            param.name != "self" and param.name != "ctx",
            params)
        return f"{command.name} {' '.join(map(self._str_command_param, params))}"

    def _str_command_param(self, param: inspect.Parameter):
        return f"<{param.name}>" if param.default else f"[{param.name}]"

    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0]
        selected = next(filter(lambda option: option.value == selected,
                               self.options))
        self.placeholder = selected.label

        commands = self.mapping[selected.value]
        description = commands[0].cog.description if not commands[0].cog is None else None
        embed = discord.Embed(title=selected.label, description=description)

        for command in commands:
            value = f"""
                {(
                    "aliases: `" + "|".join(
                        [f'{alias}' for alias in command.aliases]
                    ) + "`"
                ) if len(command.aliases) else " "}
                {
                    f"*{command.short_doc}*" if len(
                        command.short_doc) or len(
                        command.aliases) > 0 else "-"
                } 
                """

            embed.add_field(name=self._str_command(
                command), value=value, inline=False)

        embed.set_footer(text="[] => Optional | <> => Required")

        return await interaction.response.edit_message(embed=embed, view=self.view)


class HelpView(discord.ui.View):

    def __init__(self, *, mapping: 'CogMapping', msg: discord.Message, timeout: typing.Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.msg = msg
        self.add_item(SelectInfoCategories(mapping=mapping))

    async def on_timeout(self) -> None:
        self.clear_items()
        await self.msg.edit(content="`_help`",
                            embed=discord.Embed(
                                title="Expired",
                                description="Command help expired.",
                                color=discord.Color.dark_red()
                            ), view=self)


class HelpCommand(commands.HelpCommand):

    async def send_bot_help(self, mapping: 'CogMapping'):
        channel = self.get_destination()
        embed = discord.Embed(title="Help", description="Select the category")

        embed.set_footer(text="wait...")
        message = await channel.send(embed=embed)

        embed.set_footer(text="")
        await message.edit(embed=embed, view=HelpView(
            mapping=mapping, msg=message))
