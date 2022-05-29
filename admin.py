from datetime import datetime
from discord.ext import tasks, commands
from file_read_backwards import FileReadBackwards
import glob


class AdminHandler(commands.Cog):
    """Class which handles the server log files"""

    def __init__(self, bot, logPath):
        self.lastupdatetime = str
        self.lastupdate = str
        self.alerttime = str
        self.checktime = str
        self.trigger = bool
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
        if "IngameTime" in message:
            message = message[message.find(">", 2) + 2 :]
            message = message.split(" ")
            time = message[3].replace(".","")
            date = message[2].split("-")
            date = f"{date[1]}/{date[2]}/{date[0]}"
            self.checktime = time
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
            self.lastupdatetime = f":clock{emoji}: The current server time is {hour}:{minute} {meridiem}"
            if self.trigger == True and self.checktime == self.alerttime:
                self.trigger = False
                return self.lastupdatetime
            if hour == 8 and minute == "00" and meridiem == "AM":
                return self.lastupdatetime
            if date != self.lastupdate:
                self.lastupdate = f":calendar_spiral: The current server date is {date}"
                return self.lastupdate
        
    @commands.command()
    async def gettime(self, ctx):
        """Return the current surver time."""
        if self.lastupdatetime is not None and self.bot.channel is not None:
            await self.bot.channel.send(self.lastupdatetime)

    @commands.command()
    async def alert(self, ctx, alert: str, meridiem=None):
        """Alert when the serve is at a specifc time."""
        rtime = alert.split(":")
        rminute = int(rtime[1])
        if rminute == 0:
            rminute = "00"
        if meridiem != None:
            await self.bot.channel.send(f"Setting an alert for {alert} {meridiem}")
            if meridiem.upper() == "PM" or meridiem.upper() == "P":
                if int(rtime[0]) == 12:
                    rhour = int(rtime[0])
                else:
                    rhour = int(rtime[0]) +12
            else:
                if int(rtime[0]) == 12:
                    rhour = "00"
                else:
                    rhour = int(rtime[0])
        else:
            await self.bot.channel.send(f"Setting an alert for {alert}")
            rhour = int(rtime[0])
        self.alerttime = f"{rhour}:{rminute}"
        self.trigger = True