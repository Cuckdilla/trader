from datetime import timezone
import datetime, json

class Logger:

    def __init__(self, name="logger", loglevel=3, persist=True, flush=True, rotation_interval=1, format="text"):

        """ The logger gets initialized with a name (logger by default), which is also part of the name 
            of the logfiles, if persistence is enabled. If rotation_interval (log rotation interval) is set 
            to 0 (default), all output will be written to a single log file. When rotation is enabled, 
            the name of the logfiles will be <date>-<instance name>.log (example: 2020-05-16-logger.log)
            
            The available loglevels are:
            0 = Info
            1 = Warning
            2 = Error
            3 = Debug 

            Output will only be displayed according to the initialized loglevel.
        """

        self.name       = name
        self.loglevel   = loglevel
        self.persist    = persist
        self.flush      = flush
        self.format     = format
        
        self.rotation_interval = rotation_interval # (int) days

        self.initialize()


    def initialize(self):

        self.date        = datetime.datetime.today().date().isoformat()
        self.logfile     = self.date + "-" + self.name + ".log"

        self.levels = {
            0: "INFO",
            1: "WARNING",
            2: "ERROR",
            3: "DEBUG"
        }

        if self.rotation_interval != 0:

            try:
                self.rotation_interval = int(self.rotation_interval)
                self.log_needs_rotation()

            except Exception as e:
                self.error("Log retention interval is invalid.")
                self.debug(e)
                
                # Disable log rotation
                self.rotation_interval = 0
                self.debug("Log rotation has been disabled due to an error with the configuration.")


        self.debug('Logger "{}", Loglevel: {}, Logfile: {}'.format(
            self.name, self.loglevel, self.logfile
        ))

    def timestamp(self):
        return datetime.datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def message_level_string(self, level):
        try:
            return self.levels[level]
        except:
            # Default to "debug" if provided loglevel is invalid
            self.debug("An invalid loglevel was requested ({}). Defaulting to level 3 (debug)".format(level))
            return self.levels[3]

    def print_message(self, level, message):

        if self.format.lower() == "json":
            logline = json.dumps({"timestamp": self.timestamp(), "loglevel": self.message_level_string(level), "message": message})
        else:
            logline = "{} [{}] {}".format(self.timestamp(), self.message_level_string(level), message) 

        if self.persist:
            self.log_needs_rotation()

            with open("./logs/" + self.logfile, 'a+') as h:
                h.write(logline + "\n")

        print(logline, flush=self.flush)

    def info(self, message):
        self.print_message(0, message)

    def warning(self, message):
        self.print_message(1, message) if self.loglevel >= 1 else None

    def error(self, message):
        self.print_message(2, message) if self.loglevel >= 2 else None

    def debug(self, message):
        self.print_message(3, message) if self.loglevel >= 3 else None

    def custom_log(self, logfile, message):

        with open("./logs/" + logfile, 'a') as h:
            message = str(message)
            h.write(message + "\n")

    def log_needs_rotation(self):

        if self.rotation_interval != 0:

            # isoformat must be applied after checking timedelta
            current_day = datetime.datetime.today()
            
            if (current_day - datetime.timedelta(days=self.rotation_interval)).date().isoformat() == self.date:
                self.date = current_day.date().isoformat()
                self.set_logfile_name()

                self.debug("New day, new log! Rotating logs now")

    def set_logfile_name(self):
        self.logfile = "{}-{}".format(self.date, self.name + ".log")

        self.debug("Creating new log file ({})".format(self.logfile))