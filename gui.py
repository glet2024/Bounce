import tkinter as tk

class CheckboxWindow:
    def __init__(self, master, cpu_velocity, cpu_color, memory_gravity, game_start):
        self.master = master
        self.master.title("Checkbox and Slider Controls")

        # Initialize global boolean variables
        self.cpu_velocity = cpu_velocity
        self.cpu_color = cpu_color
        self.memory_gravity = memory_gravity
        self.reset_balls = False
        self.ball_num = 0

        # Checkbox variables
        self.checkbox_var1 = tk.BooleanVar()
        self.checkbox_var1.set(self.cpu_velocity)

        self.checkbox_var2 = tk.BooleanVar()
        self.checkbox_var2.set(self.cpu_color)

        self.checkbox_var3 = tk.BooleanVar()
        self.checkbox_var3.set(self.memory_gravity)

        self.checkbox_var4 = tk.BooleanVar()
        self.checkbox_var4.set(False)

        self.ball_num_var = tk.IntVar()
        self.ball_num_var.set(self.ball_num)

        # Checkboxes
        self.checkbox1 = tk.Checkbutton(self.master, text="CPU Velocity", variable=self.checkbox_var1, command=self.update_cpu_velocity)
        self.checkbox1.pack(anchor='w')

        self.checkbox2 = tk.Checkbutton(self.master, text="CPU Color", variable=self.checkbox_var2, command=self.update_cpu_color)
        self.checkbox2.pack(anchor='w')

        self.checkbox3 = tk.Checkbutton(self.master, text="Memory Gravity", variable=self.checkbox_var3, command=self.update_memory_gravity)
        self.checkbox3.pack(anchor='w')


        # Slider
        if game_start:
            self.slider_label = tk.Label(self.master, text="# initial balls:")
            self.slider_label.pack(anchor='w')

            self.slider = tk.Scale(self.master, from_=0, to=20, orient=tk.HORIZONTAL, variable=self.ball_num_var, command=self.update_num_ball)
            self.slider.pack(anchor='w')

        else:
            self.checkbox4 = tk.Checkbutton(self.master, text="Clear Balls", variable=self.checkbox_var4, command=self.update_reset_balls)
            self.checkbox4.pack(anchor='w')


    def update_cpu_velocity(self):
        self.cpu_velocity = self.checkbox_var1.get()

    def update_cpu_color(self):
        self.cpu_color = self.checkbox_var2.get()

    def update_memory_gravity(self):
        self.memory_gravity = self.checkbox_var3.get()

    def update_reset_balls(self):
        self.reset_balls = self.checkbox_var4

    def update_num_ball(self, value):
        self.ball_num = self.ball_num_var.get()

    def get_bool_vars_on_close(self):
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        self.master.destroy()