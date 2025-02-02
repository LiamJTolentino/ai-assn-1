import sys

# State diagram for the assignment
DETECT1001 = {
    "A":{
        0:('A',0),
        1:('B',0)
    },
    "B":{
        0:('C',0),
        1:('B',0)
    },
    "C":{
        0:('D',0),
        1:('B',0)
    },
    "D":{
        0:('A',0),
        1:('B',1)
    }
}

class Environment:
    """
    A class representing the external environment that the model will observe. For this assignment, the environment is just a string of 1s and 0s, but to keep in spirit of model-based agents, I've made it into a class that gives a limited view of the environment.

    Attributes:
        world (str): String of 1s and 0s representing the environment that the agent will have to observe
        index (int): Integer representing the single bit that will be returned to the agent (so a 1 or 0) (Yeah, I know it's probably more efficient to use booleans but whatever)
    """

    def __init__(self,bits:str):
        """Initializes an Environment

        Args:
            bits (str): String of 1s and 0s representing... I already explained this in an earlier docstring smh
        """

        try:
            int(bits,2)
        except:
            raise Exception("Environment has to be a string of 1s and 0s")

        self.world = bits
        self.index = 0

    def new_string(self,bits:str):
        """Resets the Environment with a whole new string to work with"""
        try:
            int(bits,2)
        except:
            raise Exception("Environment has to be a string of 1s and 0s")
        self.world = bits
        self.reset()

    def read_bit(self) -> int:
        """Returns the next bit in the string; -1 if we've reached the end

        Returns:
            int: 1 or 0 or even -1 depending on where we're at in the environment
        """

        # There is probably a much better way to do this, but I want to experiment around with Python generators to implement this
        while self.index < len(self.world):
            yield int(self.world[self.index])
            self.index += 1
        
        yield -1

    def reset(self):
        """Set index back to 0 to start reading again"""
        self.index = 0

class Agent:
    """
    A class representing the model-based agent that will do the stuff with the bits or whatever idk how to use technical terms for these docstrings

    Attributes:
        model (str): String representing the agent's internal model of the environment based on what it has observed so far. This will be used as the output string when the agent is done.
        state_set (dict[str,dict[int,tuple(str,int)]]): Dict representing the finite state automaton that will handle the logic. (To be honest, I designed this agent with Turing machines in mind but had to change some things to make it simpler, so I don't know if I'm using the correct terminology for some of these)
        start_state (str): String representing the initial state of the automaton
        current_state (str): String representing the current state of the machine
    """
    
    def __init__(self,states,start):
        """Initializes an agent

        Args:
            states (dict[str,dict[int,tuple(str,int)]]): The finite state automaton for the logic
            start (str): Starting/initial state
        """
        
        self.state_set = states
        self.start_state = start
        self.model = ''
        self.current_state = start

    def reset(self):
        """Resets the agent"""
        self.current_state = self.start_state
        self.model = ''

    def sense(self,next_bit):
        """Reads the next symbol then does the necessary actions based on the current state. This would basically be the sensors in Figure 2.11 from the lecture slides but also the other stuff.
        
        Args:
            next_bit (int): The next bit read from the Environment
        """

        # If we read -1, that means we reached the end of the input string and can't read any more
        if next_bit<0:
            return

        rules = self.state_set[self.current_state] # Basically just the arrows in the diagram that tell you which state to go to next and stuff
        next_state, write = rules[next_bit] # The information about the next state to go to and the thing to write to the output is in a nice little tuple we can use :)
        self.model += str(write) # Basically we just keep adding 0s and add 1 if we find a matching pattern to match the output of the assignment
        self.current_state = next_state
    
    def get_output(self) -> str:
        """Returns the agent's internal model of the environment"""
        return self.model
    
    def get_states(self):
        """Returns the agent's states"""
        return self.state_set



if __name__=='__main__':
    try:
        input_string = sys.argv[1]
    except:
        input_string = input("Enter a string of 1s and 0s: ")
    world = Environment(input_string)
    table = {
        "A":{
            0:('A',0),
            1:('B',0)
        },
        "B":{
            0:('C',0),
            1:('B',0)
        },
        "C":{
            0:('D',0),
            1:('B',0)
        },
        "D":{
            0:('A',0),
            1:('B',1)
        }
    }
    agent = Agent(table,"A")

    for n in world.read_bit():
        print(n)
        agent.sense(n)
        print(agent.get_output())

    print(next(world.read_bit()))
    print(agent.get_output())

    