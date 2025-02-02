import tkinter as tk
from tkinter import Canvas
from agent import *
import math
import numpy as np

# Customizable colors
TEXT = "#462d26"        
STATE = "#5b7a8c"      
BACKGROUND = "#dabdab"  
ARROW = "#395c78"       
HIGHLIGHT = "#bd3b3b" 

RADIUS = 25

class StateDiagramApp:
    """
    A class for creating the GUI for the model-based agent

    Attributes:
        agent (Agent): Agent object that the app will visualize
        animation_frames (list[tuple[str,str]]): List of tuples representing information to help animate the visualization. Each tuple is composed of the current state as a string and the agent's current model of the environment as a string
        current_frame (int): Index of the animation frame to render
        ENV (Environment): Environment object that will be used to test the agent
    """
    def __init__(self, root):
        self.agent = None
        self.animation_frames = []
        self.current_frame = 0
        self.ENV = Environment("0")

        # Everything below is for visual stuff
        self.root = root
        self.root.title("Model-based Agent Visualization")

        # Frame for buttons
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(anchor="w", padx=10, pady=5)

        # Prev button
        self.prev_button = tk.Button(self.button_frame, text="Prev", command=self.prev_action, state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT, padx=5)

        # Next button
        self.next_button = tk.Button(self.button_frame, text="Next", command=self.next_action, state=tk.DISABLED)
        self.next_button.pack(side=tk.LEFT, padx=5)

        self.status_text = tk.Text(root, height=4, width=80, state=tk.DISABLED)
        self.status_text.pack(anchor="w", padx=10, pady=5)

        # Entry for binary input
        self.entry_label = tk.Label(root, text="Enter a binary string:")
        self.entry_label.pack()
        self.entry = tk.Entry(root)
        self.entry.pack()
        self.entry.bind("<Return>", self.process_input)

        # Canvas for drawing state diagram
        self.canvas = Canvas(root, width=600, height=400, bg=BACKGROUND)
        self.canvas.pack()

        # Text visuals for output
        self.reading = self.canvas.create_text(0, 0, text="", font=("Arial", 24, "bold"), fill=TEXT)

        # Textbox for output (initially hidden)
        self.output_text = tk.Text(root, height=4, width=50, state=tk.DISABLED)
        self.output_text.pack()
        self.output_text.pack_forget()

        # State tracking
        self.states = {}
        self.transitions = []
        self.state_to_circle = {}
        self.current_state = None

        # Event bindings for dragging
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)

    def load_agent(self,agent):
        """Load the Agent object into the app and build the state diagram"""
        self.agent = agent

    def create_diagram(self):
        """Creates the diagram using the agent's states"""
        state_set = self.agent.get_states()
        num_states = len(state_set)
        increment = (2*math.pi)/num_states
        angle = 0

        temp = {} # Simply to make it easier to draw the transition arrows

        # Create the state circles
        for state_name in state_set:

            x = 300 + 100*math.cos(angle)
            y = 200 + 100*math.sin(angle)

            self.create_state(x,y,state_name)
            angle += increment

        # Create the transition arrows
        for start, info in state_set.items():
            for read_bit, next_write in info.items():
                first_circle = self.state_to_circle[start]
                second_circle = self.state_to_circle[next_write[0]]
                label = f"{read_bit}? write {next_write[1]}"
                self.create_transition(first_circle,second_circle,label)

        start_state = self.agent.start_state
        self.update_current_state(self.state_to_circle[start_state])

    def run_agent(self):
        """Make the agent obeserve the environment"""
        if not self.agent:
            raise Exception("Something went horribly wrong. No agent was loaded.")
        self.agent.reset()
        self.animation_frames = [(self.agent.current_state,self.agent.get_output())] # First animation frame
        self.current_frame = 0

        for bit in self.ENV.read_bit():
            self.agent.sense(bit)
            self.animation_frames.append((self.agent.current_state,self.agent.get_output()))
        print(f"Created {len(self.animation_frames)} frames of animation")
        
    def update_status_text(self, message):
        """Updates the content of the status textbox."""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete("1.0", tk.END)
        self.status_text.insert(tk.END, message)
        self.status_text.config(state=tk.DISABLED)

    def update_animation(self):
        """Just updates the text in the canvas for each animation frame"""
        final = self.ENV.world
        visual_output = final[:self.current_frame] + '[' + final[self.current_frame] + ']' + final[self.current_frame+1:]
        _,internal = self.animation_frames[self.current_frame]
        thing = f"What the agent sees: {visual_output}\nWhat the agent has written: {internal}"
        # self.reading.config(text=thing)
        # self.canvas.itemconfig(self.reading,text=thing)
        self.update_status_text(thing)

    def prev_action(self):
        """Rewinds to the previous animation frame"""
        self.current_frame -= 1
        self.next_button.config(state=tk.NORMAL)
        if self.current_frame <= 0:
            self.prev_button.config(state=tk.DISABLED)
        next_state,model = self.animation_frames[self.current_frame]
        self.update_current_state(self.state_to_circle[next_state])
        self.update_animation()
        print(f"Prev button clicked. Now on frame {self.current_frame}")

    def next_action(self):
        """Moves forward to the next animation frame"""
        self.current_frame += 1
        self.prev_button.config(state=tk.NORMAL)
        if self.current_frame >= len(self.animation_frames)-1:
            self.next_button.config(state=tk.DISABLED)
        next_state,model = self.animation_frames[self.current_frame]
        self.update_current_state(self.state_to_circle[next_state])
        self.update_animation()
        print(f"Next button clicked. Now on frame {self.current_frame}")

    def process_input(self, event=None):
        """Processes input and updates the output box."""
        user_input = self.entry.get()
        try:
            self.ENV.new_string(user_input)
        except:
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END,"Invalid input. Please enter a binary string.")
            return

        self.next_button.config(state=tk.NORMAL)
        self.run_agent()
        output = self.agent.get_output()
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, output)
        self.output_text.config(state=tk.DISABLED)
        self.output_text.pack()
        self.update_animation()

    def create_state(self, x, y, name):
        """Creates a draggable circle with a label."""
        radius = RADIUS
        circle = self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                         fill=STATE, outline=ARROW, width=2)
        label = self.canvas.create_text(x, y, text=name, font=("Arial", 12, "bold"), fill=TEXT)

        self.states[circle] = {"label": label, "transitions": [], "offset": (0, 0)}
        self.state_to_circle[name] = circle

    def create_transition(self, from_state, to_state, label):
        """Draws an arrow with a label between two states and keeps track of it."""
        arrow, text = self.draw_arrow(from_state, to_state, label)
        self.states[from_state]["transitions"].append((to_state, arrow, text))
        self.transitions.append((from_state, to_state, arrow, text))

    def normalize(self,v):
        """Returns a normalized version of a vector v because for some reason, numpy doesn't do that already"""
        return v/np.linalg.norm(v)
    
    def rotate_vector(self,v, angle_degrees):
        """Returns a vector rotated a certain amount of degrees"""
        angle_radians = np.radians(angle_degrees)
        rotation_matrix = np.array([
            [np.cos(angle_radians), -np.sin(angle_radians)],
            [np.sin(angle_radians), np.cos(angle_radians)]
        ])
        return rotation_matrix @ v

    def neat_coords(self,x1,y1,x2,y2):
        """Provides three 2d coordinates to create a neat curve between two points. This is only used for making the arrows not overlap so much."""
        # Turn them into vectors to make things a bit easier
        start_point = np.array([x1,y1])
        end_point = np.array([x2,y2])
        mid_point = (start_point + end_point)/2

        center = np.array([300,200]) # Center of the canvas
        between = self.normalize(end_point - start_point) # Vector pointing from the start to end
        dist = np.linalg.norm(end_point-start_point)
        warp = self.normalize(mid_point - center)
        
        if(dist>2.5*RADIUS):
            stretch = (2 if np.cross(start_point,end_point)>0 else -2)*RADIUS/(0.01*dist + 0.5) + 2*RADIUS
            mid_point += stretch*warp

            start_point += RADIUS*self.normalize(between + warp)
            end_point += RADIUS*self.normalize(warp - between)
        else:
            mid_point += warp*2.5*RADIUS
            start_point += self.rotate_vector(warp,45)*RADIUS
            end_point += self.rotate_vector(warp,-45)*RADIUS

        output = tuple(start_point) + tuple(mid_point) + tuple(end_point)
        return (float(x) for x in output) # Very nasty way to do it, but I couldn't figure out anything better

    def draw_arrow(self, from_state, to_state, label):
        """Draws an arrow and label between two states."""
        x1, y1, _, _ = self.canvas.coords(from_state)
        x2, y2, _, _ = self.canvas.coords(to_state)

        x1 += RADIUS
        y1 += RADIUS
        x2 += RADIUS
        y2 += RADIUS

        sx, sy, mx, my, ex, ey = self.neat_coords(x1,y1,x2,y2)
        arrow = self.canvas.create_line(sx, sy, mx, my, ex, ey, smooth="True", arrow=tk.LAST, width=2, fill=ARROW)
        text_x, text_y = mx, my
        text = self.canvas.create_text(text_x, text_y, text=label, font=("Arial", 12, "italic"), fill=TEXT)

        return arrow, text

    def update_transitions(self):
        """Updates all arrows when states move."""
        for from_state, to_state, arrow, text in self.transitions:
            x1, y1, _, _ = self.canvas.coords(from_state)
            x2, y2, _, _ = self.canvas.coords(to_state)

            x1 += RADIUS
            y1 += RADIUS
            x2 += RADIUS
            y2 += RADIUS

            sx, sy, mx, my, ex, ey = self.neat_coords(x1,y1,x2,y2)

            # Update arrow position
            self.canvas.coords(arrow, sx, sy, mx, my, ex, ey)

            # Update label position
            text_x, text_y = mx, my
            self.canvas.coords(text, text_x, text_y)

    def update_current_state(self, state):
        """Highlights the selected state by changing its outline color."""
        if self.current_state:
            self.canvas.itemconfig(self.current_state, outline=ARROW, width=2)  # Reset previous state outline

        self.canvas.itemconfig(state, outline=HIGHLIGHT, width=3)  # Highlight new state
        self.current_state = state

    def on_press(self, event):
        """Detects if a state is clicked and stores the offset."""
        for state, data in self.states.items():
            x1, y1, x2, y2 = self.canvas.coords(state)
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                self.selected_state = state
                data["offset"] = (event.x - x1, event.y - y1)
                return
        self.selected_state = None

    def on_drag(self, event):
        """Drags the selected state and updates transitions."""
        if self.selected_state:
            x1, y1, x2, y2 = self.canvas.coords(self.selected_state)
            offset_x, offset_y = self.states[self.selected_state]["offset"]

            # Move state
            new_x1, new_y1 = event.x - offset_x, event.y - offset_y
            new_x2, new_y2 = new_x1 + 50, new_y1 + 50
            self.canvas.coords(self.selected_state, new_x1, new_y1, new_x2, new_y2)

            # Move label
            label = self.states[self.selected_state]["label"]
            self.canvas.coords(label, (new_x1 + new_x2) / 2, (new_y1 + new_y2) / 2)

            # Update transitions
            self.update_transitions()

# Example usage
if __name__ == "__main__":
    # Create agent
    agent = Agent(DETECT1001,"A")
    root = tk.Tk()
    app = StateDiagramApp(root)

    app.load_agent(agent)
    app.create_diagram()
    app.run_agent()

    # # Example states
    # app.create_state(100, 100, "q0")
    # app.create_state(300, 100, "q1")

    # # Example transition
    # state_keys = list(app.states.keys())
    # app.create_transition(state_keys[0], state_keys[1], "0")

    root.mainloop()