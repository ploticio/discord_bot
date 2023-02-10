import discord
from discord.ext import commands
import sqlite3
import config
import json
import re

class Counters(commands.Cog):
    
    def __init__(self, bot) -> None:
        self.bot = bot
        self.data = []
        for filename in config.DATA_DIR.glob("*.json"):
            with open(config.DATA_DIR / filename, "r") as f:
                print(f"Reading chat history as JSON: {filename}")
                d = json.load(f)
                for subdict in d['messages']:
                    self.data.append((subdict['author']['id'], subdict['content']))

        self.connection = sqlite3.connect(config.DATA_DIR / "leaderboard.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS leaderboard(author TEXT PRIMARY KEY, score TEXT)")

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
        final_count = {word: 0 for word in config.NAUGHTY_WORDS}
        
        await self._read_prior(ctx, user, config.NAUGHTY_WORDS, final_count)
        await self._read_current(ctx, user, config.NAUGHTY_WORDS, final_count)

        self.cursor.execute(f"INSERT OR IGNORE INTO leaderboard(author, score) VALUES ({user.id}, {max(final_count.values())})")
        self.cursor.execute(f"UPDATE leaderboard SET score={max(final_count.values())} WHERE author={user.id}")
        self.connection.commit()
        
        for key in final_count:
            await ctx.send(f"{user.mention} has said {key} {final_count[key]} times")

        await self._add_reacts(ctx, final_count)

    @commands.command()
    async def count(self, ctx, user: discord.User, *args):
        final_count = {"word_list": 0}
        words = {"word_list": args}

        await self._read_prior(ctx, user, words, final_count)
        await self._read_current(ctx, user, words, final_count)

        await ctx.send(f"{user.mention} has said {', '.join(args)} {sum(final_count.values())} times")

    @commands.command()
    async def leaderboard(self, ctx):
        self.cursor.execute("SELECT author, score FROM leaderboard ORDER BY 1 ASC LIMIT 3")
        leaders = self.cursor.fetchall()
        msg = "NAUGHTY WORD LEADERBOARD\n"
        for i in range(len(leaders)):
            msg += f"<@{leaders[i][0]}>: {leaders[i][1]}"
            if i == 0: msg += "🥇"
            elif i == 1: msg += "🥈"
            else: msg += "🥉"
            if i != 2: msg += "\n"
        await ctx.send(msg)

    # Text history read in as JSON
    async def _read_prior(self, ctx, user, words, counts) -> None:
        for messages in self.data:
            if messages[0] == str(user.id):
                for key in words:
                    for word in words[key]:
                        found = len(re.findall(r'\b%s\b' % word, messages[1].lower()))
                        if found > 0:
                            counts[key] += found

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