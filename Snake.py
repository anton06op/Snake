import random
from tkinter import *
from time import *
from PIL import Image, ImageTk

WIDTH = 1000
HEIGHT = 1000
BODYSIZE = 50
STARTDELAY = 500
MINDELAY = 100
STEPDELAY = 20
LENGTH = 3

countBodyW = WIDTH / BODYSIZE
countBodyH = HEIGHT / BODYSIZE
x = [0] * int(countBodyW)
y = [0] * int(countBodyH)


class Snake(Canvas):

    gametime = False
    headImage = False
    head = False
    body = False
    apple = False
    delay = 0
    direction = "Right"
    direction_temp = "Right"
    loss = False

    def __init__(self):
        Canvas.__init__(self, width=WIDTH, height=HEIGHT, background="black", highlightthickness=0)
        self.focus_get()
        self.bind_all("<Key>", self.on_key_pressed)
        self.load_resources()
        self.beginplay()
        self.pack()

    def load_resources(self):
        self.headImage = Image.open("images/head.png")

        self.head = ImageTk.PhotoImage(self.headImage.resize((BODYSIZE, BODYSIZE), Image.LANCZOS))
        self.body = ImageTk.PhotoImage(Image.open("images/body.png").resize((BODYSIZE, BODYSIZE), Image.LANCZOS))
        self.apple = ImageTk.PhotoImage(Image.open("images/apple.png").resize((BODYSIZE, BODYSIZE), Image.LANCZOS))

    def beginplay(self):
        self.gametime = time()
        self.head = ImageTk.PhotoImage(self.headImage.rotate(0).resize((BODYSIZE, BODYSIZE), Image.LANCZOS))
        self.delay = STARTDELAY
        self.direction = "Right"
        self.direction_temp = "Right"
        self.loss = False

        self.delete(ALL)
        self.spawn_actors()
        self.after(self.delay, self.timer)

    def spawn_actors(self):
        self.spawn_apple()

        x[0] = int(countBodyW / 2) * BODYSIZE
        y[0] = int(countBodyH / 2) * BODYSIZE
        for i in range(1, LENGTH):
            x[i] = x[0] - BODYSIZE * i
            y[i] = y[0]
        self.create_image(x[0], y[0], image=self.head, anchor="nw", tag="head")
        for i in range(LENGTH - 1, 0, -1):
            self.create_image(x[i], y[i], image=self.body, anchor="nw", tag="body")

    def spawn_apple(self):
        apple = self.find_withtag("apple")
        if apple:
            self.delete(apple[0])
        rx = random.randint(0, int(countBodyW) - 1)
        ry = random.randint(0, int(countBodyH) - 1)
        self.create_image(rx * BODYSIZE, ry * BODYSIZE, anchor="nw", image=self.apple, tag="apple")

    def check_apple(self):
        apple = self.find_withtag("apple")[0]
        head = self.find_withtag("head")
        body = self.find_withtag("body")[-1]
        x1, y1, x2, y2 = self.bbox(head[0])
        overlaps = self.find_overlapping(x1, y1, x2, y2)
        for actor in overlaps:
            if actor == apple:
                tempx, tempy = self.coords(body)
                self.spawn_apple()
                self.create_image(tempx, tempy, image=self.body, anchor="nw", tag="body")
                if self.delay > MINDELAY:
                    self.delay -= STEPDELAY

    def check_collisions(self):
        head = self.find_withtag("head")
        body = self.find_withtag("body")
        x1, y1, x2, y2 = self.bbox(head[0])
        overlaps = self.find_overlapping(x1, y1, x2, y2)
        for b in body:
            for actor in overlaps:
                if actor == b:
                    self.loss = True

        if x1 < 0:
            self.loss = True
        if x2 > WIDTH:
            self.loss = True
        if y1 < 0:
            self.loss = True
        if y2 > HEIGHT:
            self.loss = True

    def on_key_pressed(self, event):
        key = event.keysym
        if key == "Left" and self.direction != "Right":
            self.direction_temp = key
        elif key == "Right" and self.direction != "Left":
            self.direction_temp = key
        elif key == "Up" and self.direction != "Down":
            self.direction_temp = key
        elif key == "Down" and self.direction != "Up":
            self.direction_temp = key
        elif key == "space" and self.loss:
            self.beginplay()

    def update_direction(self):
        self.direction = self.direction_temp
        head = self.find_withtag("head")
        headx, heady = self.coords(head[0])
        self.delete(head[0])
        if self.direction == "Left":
            self.head = ImageTk.PhotoImage(self.headImage.transpose(Image.FLIP_LEFT_RIGHT).resize((BODYSIZE, BODYSIZE),
                                                                                                  Image.LANCZOS))
        else:
            rotates = {"Right": 0, "Up": 90, "Down": - 90}
            self.head = ImageTk.PhotoImage(self.headImage.rotate(rotates[self.direction]).resize((BODYSIZE, BODYSIZE),
                                                                                                 Image.LANCZOS))
        self.create_image(headx, heady, image=self.head, anchor="nw", tag="head")

    def timer(self):
        self.check_collisions()
        if not self.loss:
            self.check_apple()
            self.update_direction()
            self.move_snake()
            self.after(self.delay, self.timer)
        else:
            self.game_over()

    def move_snake(self):
        head = self.find_withtag("head")
        body = self.find_withtag("body")
        items = body + head
        for i in range(len(items) - 1):
            currentxy = self.coords(items[i])
            nextxy = self.coords(items[i + 1])
            self.move(items[i], nextxy[0] - currentxy[0], nextxy[1] - currentxy[1])
        if self.direction == "Left":
            self.move(head, -BODYSIZE, 0)
        elif self.direction == "Right":
            self.move(head, BODYSIZE, 0)
        elif self.direction == "Up":
            self.move(head, 0, -BODYSIZE)
        elif self.direction == "Down":
            self.move(head, 0, BODYSIZE)

    def game_over(self):
        body = self.find_withtag("body")
        self.delete(ALL)
        self.create_text(self.winfo_width() / 2, self.winfo_height() / 2 - 120, text="Вы проиграли!", fill="white",
                         font="Tahoma 40", tags="text")
        self.create_text(self.winfo_width() / 2, self.winfo_height() / 2 - 60,
                         text="Время в игре: " + self.get_gametime(), fill="white", font="Tahoma 40",
                         tags="text")
        self.create_text(self.winfo_width() / 2, self.winfo_height() / 2, text="Длина змейки: " + str(len(body) + 1),
                         fill="white", font="Tahoma 40", tags="text")
        self.create_text(self.winfo_width() / 2, self.winfo_height() / 2 + 60, text="Нажмите пробел для новой игры",
                         fill="white", font="Tahoma 40", tags="text")

    def get_gametime(self):
        self.gametime = round(time() - self.gametime - self.delay / 1000)
        if self.gametime < 60:
            return str(self.gametime) + " сек."
        else:
            minutes = str(self.gametime // 60)
            seconds = str(self.gametime % 60)
            if seconds == 0:
                return minutes + " мин. "
            else:
                return minutes + " мин. " + seconds + " сек."


root = Tk()
root.title("Snake")
root.board = Snake()
root.resizable(False, False)
ws = root.winfo_screenwidth()
cx = int(ws / 2 - WIDTH / 2)
root.geometry("+{0}+{1}".format(cx, 0))
root.mainloop()
