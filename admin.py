from datetime import datetime
from discord.ext import tasks, commands
from file_read_backwards import FileReadBackwards
import glob


class AdminHandler(commands.Cog):
    """Class which handles the server log files"""

    def __init__(self, bot, logPath):
        self.lastupdatetime = str
        self.alerttime = str
        self.checktime = str
        self.trigger = bool
        #server start date
        self.lastupdate = datetime(1993, 7, 8)
        self.bot = bot
        self.logPath = logPath
        self.tellchat = False
        self.lastUpdateTimestamp = datetime.now()
        self.update.start()

    def splitLine(self, line: str):
        """Split a log line into a timestamp and the remaining message"""
        try:
            timestampStr, message = line.strip()[1:].split("]", 1)
            timestamp = datetime.strptime(timestampStr, "%d-%m-%y %H:%M:%S.%f")
            return timestamp, message
        except:
            return self.lastUpdateTimestamp, line

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
                    if timestamp:
                        if timestamp > newTimestamp:
                            newTimestamp = timestamp
                        if timestamp > self.lastUpdateTimestamp:
                            message = self.handleLog(timestamp, message)
                            if message is not None and self.bot.channel is not None:
                                await self.bot.channel.send(message)
                        else:
                            break
                    else:
                        break
                self.lastUpdateTimestamp = newTimestamp
                
    # Parse a line in the user log file and take appropriate action

    def handleLog(self, timestamp: datetime, message: str):
        if "RESET INBOUND" in message:
            return f":no_entry: Server is doing a Hard reset. \n:warning: remove '%HOMEPATH%\Zomboid\Saves\Multiplayer\THIS_SERVER'"
        if "SERVER STARTED" in message:
            return f":satellite_orbital: Server connected succesfully"
        if " IngameTime" in message:
            # strip timestap from this line from the log
            message = message[message.find(">", 2) + 2 :]
            # turn message variable into an array with the time and date. 
            message = message.split(" ")
            # Get time from array and assign time variable
            time = message[3].replace(".","")
            # Get date from array and assign date variable
            date = message[2].split("-")
            # Reformate date string to match US locale
            date = f"{date[1]}/{date[2]}/{date[0]}"
            date_from_string = datetime.strptime(date, "%m/%d/%Y")
            # add time variable to Global checktime
            self.checktime = time
            # split time into hours and minutes
            time = time.split(":")
            # assign hour to hour variable
            hour = int(time[0])
            # assign minute to minute variable
            minute = int(time[1])
            # Handle AM/PM 
            if hour > 11:
                if hour > 12:
                    hour = hour-12
                meridiem = "PM"
            elif hour == 0:
                hour = 12
                meridiem = "AM"
            else:
                meridiem = "AM"
            # Change minute from INT to STR to match formatting.
            # Create Clock Emoji based on actual ingame time
            if minute == 0:
                minute = "00"  
                emoji = hour
            elif minute > 0 and minute < 30:
                emoji = hour
            elif minute == 30:
                emoji = f"{hour}30"
            elif minute > 30 and minute < 60:
                emoji = f"{hour}30"
            # Create string to send to chat
            self.lastupdatetime = f":clock{emoji}: The current server time is {hour}:{minute} {meridiem}"
            # If "Alert" is run send to chat when the time matches the alert time.
            if self.trigger == True and self.checktime == self.alerttime:
                self.trigger = False
                return self.lastupdatetime
            # if its this time in the game, send to chat.
            if hour == 8 and minute == "00" and meridiem == "AM":
                return self.lastupdatetime
            # send the date to chat, and midnight everday.
            if date_from_string > self.lastupdate:
                self.lastupdate = datetime.strptime(date, "%m/%d/%Y")
                return f":calendar_spiral: The current server date is {date}"
        
    @commands.command()
    async def gettime(self, ctx):
        """Return the current surver time."""
        # Send the last saved time to chat
        if self.lastupdatetime is not None and self.bot.channel is not None:
            await self.bot.channel.send(self.lastupdatetime)

    @commands.command()
    async def alert(self, ctx, alert: str, meridiem=None):
        """Alert when the serve is at a specifc time."""
        # set the requested time into an array from the alert command
        rtime = alert.split(":")
        # get the minutes from the array
        rminute = int(rtime[1])
        # change the minutes to 00 if 0 for formatting reasons
        if rminute == 0:
            rminute = "00"
        # Check if its AM/PM or millitary time, and handle it.
        # Alert chat that the request was recieved.
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
        # create variable for the alert time to check against the current time from the above function.
        self.alerttime = f"{rhour}:{rminute}"
        # Tell the above function to send the alert.
        self.trigger = True