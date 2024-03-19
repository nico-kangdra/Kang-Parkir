from database import get_space, update_slot, remove_slot
from datetime import datetime, timedelta
from time import sleep
from pytz import timezone
WIB = timezone("Asia/Jakarta")

def update_daily():
    spaces = get_space()
    for name, space in spaces.items():
        tmwr = (datetime.now().astimezone(WIB) + timedelta(days=1)).strftime("%Y%m%d")
        if space["type"] == "mobil":
            update_slot(name, tmwr, {"slotcar": space["car"]})
        elif space["type"] == "motor":
            update_slot(name, tmwr, {"slotmotor": space["motor"]})
        else:
            update_slot(
                name, tmwr, {"slotcar": space["car"], "slotmotor": space["motor"]}
            )
        remove_slot(
            name,
            (datetime.now().astimezone(WIB) - timedelta(days=5)).strftime("%Y%m%d"),
        )
        print(name + " Updated " + tmwr)

now = datetime.now().astimezone(WIB)
while True:
    if 22 <= now.hour < 23:
        update_daily()
        sleep(86400)
    else:
        sleep(3600)