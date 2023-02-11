import discord
from discord.ext import commands
import config
import json
import re

class Counters(commands.Cog):
    
    def __init__(self, bot) -> None:
        self.bot = bot
        self.data = []
        self.scoreboard = {}
        for filename in config.DATA_DIR.glob("*.json"):
            with open(filename, "r") as f:
                print(f"Reading chat history as JSON: {filename}")
                d = json.load(f)
                for subdict in d['messages']:
                    self.data.append((subdict['author']['id'], subdict['content']))
        self._populate_leaderboard()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        for key in config.NAUGHTY_WORDS:
            for word in config.NAUGHTY_WORDS[key]:
                if re.search(r'\b%s\b' % word, message.content.lower()):
                    await message.add_reaction("🤨")
                    await message.add_reaction("📸")
                    await message.reply("🚨 WOAH 🚨 😱😱😱")

    @commands.command()
    async def bad(self, ctx, user: discord.User):
        curr_count = {word_family: 0 for word_family in config.NAUGHTY_WORDS}
        
        await self._read_current(ctx, user, config.NAUGHTY_WORDS, curr_count)
        
        for key in curr_count:
            await ctx.send(f"{user.mention} has said {key} {self.scoreboard[str(user.id)][key] + curr_count[key]} times")

        await self._add_reacts(ctx, curr_count)

    @commands.command()
    async def count(self, ctx, user: discord.User, *args):
        final_count = {"word_list": 0}
        words = {"word_list": args}

        await self._read_prior(ctx, user, words, final_count)
        await self._read_current(ctx, user, words, final_count)

        await ctx.send(f"{user.mention} has said {', '.join(args)} {sum(final_count.values())} times")

    @commands.command()
    async def leaderboard(self, ctx):
        scores = []
        await ctx.send("Compiling leaderboard...")
        for user in self.scoreboard:
            curr_count = {word_family: 0 for word_family in config.NAUGHTY_WORDS}
            await self._read_current(ctx, user, config.NAUGHTY_WORDS, curr_count)
            scores.append((user, max(self.scoreboard[user].values()) + max(curr_count.values())))

        leaders = sorted(scores, key=lambda x: x[1], reverse=True)
        msg = "NAUGHTY WORD LEADERBOARD:\n"
        for i in range(3):
            if i == 0: msg += "🥇"
            elif i == 1: msg += "🥈"
            else: msg += "🥉"
            msg += f"<@{leaders[i][0]}>: {leaders[i][1]}"
            if i != 2: msg += "\n"
        await ctx.send(msg)

    # Reads downloaded history and populates leaderboard
    def _populate_leaderboard(self):
        for messages in self.data:
            for key in config.NAUGHTY_WORDS:
                for word in config.NAUGHTY_WORDS[key]:
                    found = len(re.findall(r'\b%s\b' % word, messages[1].lower()))
                    if found > 0:
                        if messages[0] not in self.scoreboard:
                            self.scoreboard[messages[0]] = {word_family: 0 for word_family in config.NAUGHTY_WORDS}
                        self.scoreboard[messages[0]][key] += found

    # Reads downloaded history and counts arguments provided in 'count' command
    async def _read_prior(self, ctx, user, words, word_count):
        for messages in self.data:
            if messages[0] == str(user.id):
                for key in words:
                    for word in words[key]:
                        found = len(re.findall(r'\b%s\b' % word, messages[1].lower()))
                        if found > 0:
                            word_count[key] += found

    # Most recent messages
    async def _read_current(self, ctx, user, words, counts) -> None:
        for channel in ctx.guild.text_channels:
            try:
                messages = [message async for message in channel.history(limit=200) 
                            if message.author == user]
                for m in messages:
                    for key in words:
                        for word in words[key]:
                            found = len(re.findall(r'\b%s\b' % word, m.content.lower()))
                            if found > 0:
                                counts[key] += found
            except Exception as e:
                print(f"Exception Occured: {e}")
                continue
    
    # Adds reactions based on count
    async def _add_reacts(self, ctx, count) -> None:
        msg = ctx.channel.last_message
        num = max(count.values())
        if num == 0:
            await msg.add_reaction("👍")
        elif num == 1:
            await msg.add_reaction("🤨")
        elif num > 1 and num < 25:
            await msg.add_reaction("🤨")
            await msg.add_reaction("📸")
        elif num >= 25 and num < 50:
            await msg.add_reaction("💀")
        else:
            await msg.add_reaction("😱")
            await msg.add_reaction("🇧")
            await msg.add_reaction("🇷")
            await msg.add_reaction("🇴")

async def setup(bot):
    await bot.add_cog(Counters(bot))