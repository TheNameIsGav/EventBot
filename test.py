from datetime import datetime, timezone


currentTime = datetime.now(tz=timezone.utc).timestamp()

templateTime = datetime(2021, 1, 13, 23, 30)

templatedTime = templateTime.fromtimestamp(templateTime.timestamp(), tz=timezone.utc).timestamp()

print((currentTime - templatedTime)/60)