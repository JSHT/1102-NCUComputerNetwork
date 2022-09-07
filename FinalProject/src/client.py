# import tkinter as tk
from tkinter import *
from tkinter import colorchooser, messagebox, ttk
import random
import socket
import threading
import pickle
# import json


class GUI:

    def __init__(self, master):
        self.root = master
        self.client_socket = None
        self.first = 0
        self.shapeFirst = 0

        self.fill = 0

        self.lr_preX, self.lr_preY, self.r_preX, self.r_preY = None, None, None, None
        self.startX, self.startY, self.preX, self.preY = None, None, None, None

        self.canvas = None

        self.colorBtn = None
        self.color = "#" + \
            ''.join([random.choice('0123456789ABCDEF') for j in range(6)])
        self.r_color = ''

        self.brushSizeScale = None
        self.brushSize, self.r_brushSize = 1, 1
        self.brushLabel = None

        self.paintSelect = None
        self.paintWay, self.r_paintWay = None, None
        self.init_socket()
        self.init_gui()
        self.listen_for_incoming_messages_in_a_thread()

    def init_socket(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_ip = '127.0.0.1'
        remote_port = 48763
        self.client_socket.connect((remote_ip, remote_port))

    def init_gui(self):
        self.root.title("whiteboard")
        self.root.resizable(0, 0)
        self.display_whiteboard()

    def listen_for_incoming_messages_in_a_thread(self):
        thread = threading.Thread(
            target=self.receive_message_from_server, args=(self.client_socket,))
        thread.start()

    def receive_message_from_server(self, so):
        while 1:
            buffer = so.recv(512)
            if not buffer:
                break
            # details = json.loads(buffer.decode('utf-8'))
            details = pickle.loads(buffer)
            # print(details)
            self.r_paintWay = details.get('way')
            # print(self.r_paintWay)
            self.r_color = details.get('color')
            self.r_brushSize = details.get('size')
            if details.get('fill') == 1:
                self.filledup_receive()
            if (self.r_paintWay == 'pen' or self.r_paintWay == 'block' or self.r_paintWay == 'dot'):
                if details.get('first'):
                    self.lr_preX = details.get('preX')
                    self.lr_preY = details.get('preY')
                else:
                    self.r_preX = details.get('preX')
                    self.r_preY = details.get('preY')
                    self.draw_receive()
            else:
                # print('shape')
                self.startX = details.get('startX')
                self.startY = details.get('startY')
                if details.get('shapeFirst'):
                    self.r_preX = details.get('preX')
                    self.r_preY = details.get('preY')
                else:
                    self.draw_shape_receive()
                # self.r_preX = details.get('preX')
                # self.r_preY = details.get('preY')
            # print(self.r_color, self.r_preX, self.r_preY)
        so.close()

    def display_whiteboard(self):
        self.root.geometry('487x630')
        self.display_brushes_attribute()
        self.display_canvas_area()

    def display_brushes_attribute(self):
        frame = Frame(self.root, padx=5, pady=5, bg='white')
        self.colorBtn = Button(frame, bg=self.color, padx=40, bd=1,
                               command=self.colorPick)
        self.colorBtn.grid(row=0, column=0, padx=5)
        filledupBtn = Button(frame, text="filled up", font=("Cambria", 10), bd=1,
                             command=self.filledup)
        filledupBtn.grid(row=0, column=1, padx=5)
        self.brushSizeScale = Scale(
            frame, from_=1, to=30, bg='white', showvalue=False, bd=0, orient=HORIZONTAL, command=self.get_brushSize)
        self.brushSizeScale.grid(row=0, column=2, padx=5)
        self.brushLabel = Label(
            frame, bg='white', text='size: '+str(self.brushSize))
        self.brushLabel.grid(row=0, column=3, padx=5)
        self.paintSelect = ttk.Combobox(
            frame, values=['pen', 'block', 'dot', '-------------', 'line', 'outline_rectangle', 'rectangle', 'outline_oval', 'oval'], width=15)
        self.paintSelect.grid(row=0, column=4, padx=5)
        self.paintSelect.current(0)
        frame.pack(fill='x')

    def filledup(self):
        self.fill = 1
        self.canvas.delete('all')
        self.canvas.configure(bg=self.color)
        self.send_detail()
        self.fill = 0

    def filledup_receive(self):
        self.canvas.delete('all')
        self.canvas.configure(bg=self.r_color)

    def colorPick(self):
        self.color = colorchooser.askcolor()[1]
        self.colorBtn.configure(bg=self.color)
        # self.send_detail()

        # my_label = Label(self.root, text=my_color).pack(pady=10)
        # my_label2 = Label(self.root, text="you picked a color",
        #                   font=("Helvetica", 32), bg=my_color).pack()

    def get_brushSize(self, val):
        self.brushSize = val
        self.brushLabel['text'] = 'size: ' + str(val)
        # print(val)

    def display_canvas_area(self):
        self.canvas = Canvas(self.root, bg='black')
        self.canvas.pack(
            anchor='nw', fill='both', expand=1)
        self.canvas.bind("<Button-1>", self.get_X_and_Y)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.draw_shape)

    def draw(self, event):
        self.first = 0
        if self.paintWay == 'pen':
            self.canvas.create_line(
                (self.preX, self.preY, event.x, event.y), width=self.brushSize, fill=self.color, capstyle=ROUND)
        elif self.paintWay == 'block':
            self.canvas.create_rectangle(
                (self.preX, self.preY, event.x, event.y), fill=self.color)
        elif self.paintWay == 'dot':
            self.canvas.create_oval(
                (self.preX, self.preY, event.x, event.y), fill=self.color)
        self.preX, self.preY = event.x, event.y
        self.send_detail()

    def draw_receive(self):
        if self.r_paintWay == 'pen':
            self.canvas.create_line(
                (self.lr_preX, self.lr_preY, self.r_preX, self.r_preY), width=self.r_brushSize, fill=self.r_color, capstyle=ROUND)
        elif self.r_paintWay == 'block':
            self.canvas.create_rectangle(
                (self.lr_preX, self.lr_preY, self.r_preX, self.r_preY), fill=self.r_color)
        elif self.r_paintWay == 'dot':
            self.canvas.create_oval(
                (self.lr_preX, self.lr_preY, self.r_preX, self.r_preY), fill=self.r_color)
        self.lr_preX, self.lr_preY = self.r_preX, self.r_preY

    def draw_shape(self, event):
        self.shapeFirst = 0
        if self.paintWay == 'line':
            self.canvas.create_line((self.startX, self.startY, event.x, event.y),
                                    width=self.brushSize, fill=self.color, capstyle=ROUND)
        elif self.paintWay == 'outline_rectangle':
            self.canvas.create_rectangle((self.startX, self.startY, event.x, event.y),
                                         outline=self.color, width=self.brushSize)
        elif self.paintWay == 'rectangle':
            self.canvas.create_rectangle((self.startX, self.startY, event.x, event.y),
                                         fill=self.color, width=0)
        elif self.paintWay == 'outline_oval':
            self.canvas.create_oval((self.startX, self.startY, event.x, event.y),
                                    outline=self.color, width=self.brushSize)
        elif self.paintWay == 'oval':
            self.canvas.create_oval((self.startX, self.startY, event.x, event.y),
                                    fill=self.color, width=0)
        self.preX, self.preY = event.x, event.y
        self.send_detail()

    def draw_shape_receive(self):
        if self.r_paintWay == 'line':
            self.canvas.create_line(
                (self.startX, self.startY, self.r_preX, self.r_preY), width=self.r_brushSize, fill=self.r_color, capstyle=ROUND)
        elif self.r_paintWay == 'outline_rectangle':
            self.canvas.create_rectangle(
                (self.startX, self.startY, self.r_preX, self.r_preY), outline=self.r_color, width=self.r_brushSize)
        elif self.r_paintWay == 'rectangle':
            self.canvas.create_rectangle(
                (self.startX, self.startY, self.r_preX, self.r_preY), fill=self.r_color, width=0)
        elif self.r_paintWay == 'outline_oval':
            self.canvas.create_oval(
                (self.startX, self.startY, self.r_preX, self.r_preY), outline=self.r_color, width=self.r_brushSize)
        elif self.r_paintWay == 'oval':
            self.canvas.create_oval(
                (self.startX, self.startY, self.r_preX, self.r_preY), fill=self.r_color, width=0)

    def get_X_and_Y(self, event):
        self.first = 1
        self.shapeFirst = 1
        self.paintWay = self.paintSelect.get()
        self.preX, self.preY = event.x, event.y
        self.startX, self.startY = event.x, event.y
        self.send_detail()

    def send_detail(self):
        # details = json.dumps(
        #     {"first": self.first, "color": self.color, "size": self.brushSize, "way": self.paintWay, "preX": self.preX, "preY": self.preY})
        details = pickle.dumps(
            {"first": self.first, "shapeFirst": self.shapeFirst, "fill": self.fill, "color": self.color, "size": self.brushSize, "way": self.paintWay, "preX": self.preX, "preY": self.preY, "startX": self.startX, "startY": self.startY})
        # self.client_socket.send(details.encode('utf-8'))
        self.client_socket.send(details)

    def on_close_window(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
            self.client_socket.send(pickle.dumps('close'))
            self.client_socket.close()
            exit(0)


if __name__ == '__main__':
    root = Tk()
    gui = GUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_close_window)
    root.mainloop()
