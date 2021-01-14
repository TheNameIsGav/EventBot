from datetime import datetime, timezone


currentTime = datetime.now(tz=timezone.utc).timestamp()

templateTime = datetime(2021, 1, 13, 23, 30)

templatedTime = templateTime.fromtimestamp(templateTime.timestamp(), tz=timezone.utc).timestamp()

print((currentTime - templatedTime)/60)


#await user.send("You have a meeting at {0}, which is in {1} minutes".format(event[0], mins))
#                try: 
#                    description = event[2]
##                except IndexError:
#                    return
#                else:
#                    await user.send("You gave the description as:\n {0}".format(description))
#                return
#            if mins < 0:
#                return