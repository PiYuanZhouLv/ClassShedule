import datetime
import sys
import tkinter
import time
import tkinter.ttk
import json

root = tkinter.Tk()
root.title('课程表')
root.geometry('250x130')
root.attributes('-topmost', True)
root.attributes('-toolwindow', True)
root.resizable(False, False)
# root.attributes('-transparent', 'white')
# root.overrideredirect(True)
closed = False
rop = None
root.update()
root.geometry('250x130+%s+%s' % (root.winfo_screenwidth() - root.winfo_width() - 10, 1))

close_time = -1
last_close_after = None
on_close_event = False


def on_close(*args):
    global close_time, on_close_event, last_close_after
    on_close_event = True
    close_time += 1
    close_time %= len(close_events)
    if last_close_after:
        root.after_cancel(last_close_after)
    now_time.set(close_events[close_time][0])
    last_close_after = root.after(2000, close_event)


def on_see_through(*args):
    if not closed:
        close()
    else:
        reopen()


def close_event():
    global close_time, on_close_event
    close_events[close_time][1]()
    close_time = -1
    on_close_event = False


def on_really_close():
    from tkinter import messagebox
    if messagebox.askokcancel("关闭确认", "确定要关闭吗?", default="cancel"):
        root.destroy()


close_events = [
    ("隐藏/显示", on_see_through),
    ("再按3次关闭", lambda: None),
    ("再按2次关闭", lambda: None),
    ("再按1次关闭", lambda: None),
    ("关闭", on_really_close),
    ("取消", lambda: None)
]


def close(*args):
    global closed, rop
    root.attributes('-alpha', 0.4)
    closed = True
    root.attributes('-transparentcolor', '#F0F0F0')
    rop = root.after(10 * 60 * 1000, reopen)


def reopen(*args):
    global closed
    root.after_cancel(rop)
    root.attributes('-alpha', 1)
    closed = False
    root.attributes('-transparentcolor', '')


class_list = json.loads(open(sys.argv[0].rsplit('.')[0] + '.json', encoding='utf-8').read())

tkinter.Label(root, text=f'{datetime.date.today().month}月{datetime.date.today().day}日  '
                         f'星期{ {0: "一", 1: "二", 2: "三", 3: "四", 4: "五", 5: "六", 6: "日"}[datetime.date.today().weekday()]}'
              ).pack()
now_time = tkinter.StringVar(root, datetime.datetime.now().strftime('%H:%M:%S'))


def update_now_time(*args):
    global now_time
    if not on_close_event:
        now_time.set(datetime.datetime.now().strftime('%H:%M:%S'))
    root.after(100, update_now_time)


root.after(100, update_now_time)
tkinter.Label(root, textvariable=now_time,
              anchor='center', font=('default', 25, 'bold')).pack()

now_class = tkinter.StringVar(root, '')
tkinter.Label(root, textvariable=now_class,
              anchor='w').pack()
remain_time = tkinter.DoubleVar(root, 0.0)
tkinter.ttk.Progressbar(root, length=250, maximum=1, variable=remain_time).pack()
next_class = tkinter.StringVar(root, '')
tkinter.Label(root, textvariable=next_class,
              anchor='w').pack()
weekday = datetime.datetime.today().weekday() if "-w" not in sys.argv else int(sys.argv[sys.argv.index("-w") + 1])


def update_info(*args):
    now = datetime.datetime.today()
    now_t = datetime.time(now.hour, now.minute, now.second, now.microsecond)
    classes = class_list[str(weekday)]
    # classes = class_list[0] # Test
    if classes[0][1:] not in ((0, 0), [0, 0]):
        classes.insert(0, ('新的一天', 0, 0))
    if classes[-1][1:] not in ((23, 59), [23, 59]):
        classes.append(('迎接新的一天', 23, 59))
    classes = classes.copy()
    classes.reverse()
    for i, c in enumerate(classes):
        t = datetime.time(c[1], c[2], 0)
        if now_t > t:
            index = i
            break
    now_class.set(classes[index][0])
    c = classes[index]
    ct = datetime.datetime(now.year, now.month, now.day, c[1], c[2], 0)
    nc = classes[index - 1]
    nct = datetime.datetime(now.year, now.month, now.day, nc[1], nc[2], 0)
    at = nct - ct
    rt = nct - now
    remain_time.set(1 - rt / at)
    next_class.set(f'{rt.seconds // 60}:{rt.seconds % 60:0>2}后: {nc[0]}')
    root.after(100, update_info)


root.after(0, update_info)

root.bind('<Enter>', lambda *args: root.attributes('-alpha', 1.0 if not closed else 0.2))
root.bind('<Leave>', lambda *args: root.attributes('-alpha', 0.6 if not closed else 0.2))
root.protocol("WM_DELETE_WINDOW", on_close)

root.mainloop()
