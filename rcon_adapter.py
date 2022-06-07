from discord.ext import commands
from discord.ext.commands import has_permissions
import os
from rcon.source import Client
import re
import time

class RCONAdapter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        rconHost = os.getenv("RCON_HOST")
        if rconHost is None:            
            self.rconHost = "localhost"
            self.bot.log.info("Using default IP")
        else:
            self.rconHost = rconHost

        port = os.getenv("RCON_PORT")
        if port is None:            
            self.rconPort = 27015
            self.bot.log.info("Using default port")
        else:
            self.rconPort = int(port)
        self.rconPassword = os.getenv("RCON_PASSWORD")

    @commands.command()
    @has_permissions(administrator=True)
    async def option(self, ctx, option: str, newValue: str = None):
        """Show or set the value of a server option"""
        if newValue is not None:
            with Client(self.rconHost, self.rconPort, passwd=self.rconPassword, timeout=5.0) as client:
                result = client.run(f"changeoption {option} {newValue}")
            await ctx.send(f"`{result}`")
        else:
            with Client(self.rconHost, self.rconPort, passwd=self.rconPassword, timeout=5.0) as client:
                message = client.run("showoptions")
            message = message.splitlines()
            regex = re.compile(f".*{option}.*", flags=re.IGNORECASE)
            message = list(filter(regex.match, message))
            message = "\n".join(message)
            try:
                if len(message):
                    await ctx.send(f"```\n{message}\n```")
                else:
                    await ctx.send("No matches found")
            except:
                await ctx.send("Unable to send message")

    @commands.command()
    @has_permissions(administrator=True)
    async def addxp(self, ctx, name: str = None, skill: str = None, amount: int = None):
        """Add xp for a skill"""
        if name is None or skill is None or amount is None:
            await ctx.reply("requires three values: Name, skill and amount")
            return
        with Client(self.rconHost, self.rconPort, passwd=self.rconPassword, timeout=5.0) as client:
            result = client.run(f"addxp \"{name}\" {skill}={amount}")
            await ctx.send(result)

    @commands.command()
    @has_permissions(administrator=True)
    async def save(self, ctx):
        """Save the server"""
        with Client(self.rconHost, self.rconPort, passwd=self.rconPassword, timeout=5.0) as client:
            result = client.run(f"save")
            await ctx.send(f":floppy_disk: {result}")
            
    @commands.command()
    @has_permissions(administrator=True)
    async def restart(self, ctx):
        """Reboot the server"""
        with Client(self.rconHost, self.rconPort, passwd=self.rconPassword, timeout=5.0) as client:
            result = client.run(f"quit")
            if result == "Quit":
                await ctx.send(":recycle: Server is restarting...")

    @commands.command()
    @has_permissions(administrator=True)
    async def rcon(self, ctx, *com: str):
        """Send any RCON command, syntax !rcon 'command [options]'"""
        if len(com) != 0:
            for x in range(len(com)):
                if x == 0:
                    string = str(com[x]) + " "
                elif x == len(com)-1:
                    string = string + str(com[x])
                else:
                    string = string + str(com[x]) + " "
            with Client(self.rconHost, self.rconPort, passwd=self.rconPassword, timeout=5.0) as client:
                result = client.run(f"{string}")
                if "Unknown command" in result:
                    await ctx.send(f":warning: {result}")   
                elif len(result) == 0:    
                    return         
                else:
                    await ctx.send(f":desktop: {result}")
        else:
            await ctx.send(f":warning: ERROR: syntax !rcon [command] [options]")
