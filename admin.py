from datetime import datetime
from discord.ext import tasks, commands
from file_read_backwards import FileReadBackwards
import glob


class AdminHandler(commands.Cog):
    """Class which handles the server log files"""

    def __init__(self, bot, logPath):
        self.bot = bot
        self.logPath = logPath
        self.tellchat = False
        self.lastUpdateTimestamp = datetime.now()
        self.update.start()

    def splitLine(self, line: str):
        """Split a log line into a timestamp and the remaining message"""
        timestampStr, message = line.strip()[1:].split("]", 1)
        timestamp = datetime.strptime(timestampStr, "%d-%m-%y %H:%M:%S.%f")
        return timestamp, message

    @tasks.loop(seconds=2)
    async def update(self):  
        """Update the handler

        This will check the latest log file and update our data based on any
        new entries
        """
        files = glob.glob(self.logPath + "/*server.txt")
        if len(files) > 0:
            with FileReadBackwards(files[0]) as f:
                newTimestamp = self.lastUpdateTimestamp
                for line in f:
                    timestamp, message = self.splitLine(line)
                    if timestamp > newTimestamp:
                        newTimestamp = timestamp
                    if timestamp > self.lastUpdateTimestamp:
                        message = self.handleLog(timestamp, message)
                        if message is not None and self.bot.channel is not None:
                            await self.bot.channel.send(message)
                    else:
                        break
                self.lastUpdateTimestamp = newTimestamp

    # Parse a line in the user log file and take appropriate action

    def handleLog(self, timestamp: datetime, message: str):
        if "IngameTime" in message and self.sendtochat:
            self.sendtochat = False
            message = message[message.find(">", 2) + 2 :]
            message = message.split(" ")
            time = message[3].replace(".","")
            time = time.split(":")
            hour = int(time[0])
            minute = int(time[1])
            if hour > 11:
                if hour > 12:
                    hour = hour-12
                meridiem = "PM"
            elif hour == 0:
                hour = 12
                meridiem = "AM"
            else:
                meridiem = "AM"
            if minute == 0:
                minute = "00"  
                emoji = hour
            elif minute > 0 and minute < 30:
                emoji = hour
            elif minute == 30:
                emoji = f"{hour}30"
            elif minute > 30 and minute < 60:
                emoji = f"{hour}30"
            return f":clock{emoji}: The current server time is {hour}:{minute} {meridiem} "
        

    @commands.command()
    async def gettime(self, ctx):
        self.sendtochat = True
