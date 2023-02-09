import discord
from discord.ext import commands
import config
import json
import re
import os

class Counters(commands.Cog):
    
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        for key in config.NAUGHTY_WORDS:
            for word in config.NAUGHTY_WORDS[key]:
                if re.search(r'\b%s\b' % word, message.content.lower()):
                    await message.add_reaction("🤨")
                    await message.add_reaction("📸")
                    await message.reply(f"🚨 WOAH 🚨 😱😱😱")

    @commands.command()
    async def bad(self, ctx, user: discord.User):
        final_count = {word: 0 for word in config.NAUGHTY_WORDS}
        
        await self._read_prior(ctx, user, config.NAUGHTY_WORDS, final_count)
        await self._read_current(ctx, user, config.NAUGHTY_WORDS, final_count)
        
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

    # Text history read in as JSON
    async def _read_prior(self, ctx, user, words, counts) -> None:
        await ctx.send("Reading history...")
        for filename in os.listdir("data/"):
            with open(os.path.join("data/", filename), "r") as f:
                data = json.load(f)
            for subdict in data['messages']:
                if subdict['author']['id'] == str(user.id): 
                    for key in words:
                        for word in words[key]:
                            found = len(re.findall(r'\b%s\b' % word, subdict['content'].lower()))
                            if found > 0:
                                counts[key] += found

    # Most recent messages
    async def _read_current(self, ctx, user, words, counts):
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
    async def _add_reacts(self, ctx, count):
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