from todoist.api import TodoistAPI
import datetime
api = TodoistAPI("4c77490204e6ebc78e66c4e6ae4dcc7966b487a5")


def check_items_todoist():
    try:
        today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        api.sync()
        tasks_today = ""
        for item in api.state['items']:
            if item['due'] is not None and item['date_completed'] is None and item['due']['date'][0:10] == today:
                name = item['content']
                if name == "back day TRAINING":
                    name = f'<a href="https://www.youtube.com/watch?v=4TlfWFzMxn0&t=47s&ab_channel=BIOMACHINE">back day TRAINING</a>'
                elif name == "arms day TRAINING":
                    name = f'<a href="https://www.youtube.com/watch?v=4mNdXz2333U&t=175s&ab_channel=BIOMACHINE">arms day TRAINING</a>'
                elif name == "legs day TRAINING":
                    name = f'<a href="https://www.youtube.com/watch?v=4mNdXz2333U&t=343s&ab_channel=BIOMACHINE">legs day TRAINING</a>'
                tasks_today = tasks_today + '🔘 ' + name + " " + item['due']['date'][11:] +'\n'
        if tasks_today == "":
            return 0
        return tasks_today
    except:
        return 0