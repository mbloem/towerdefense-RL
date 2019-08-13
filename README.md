# towerdefense-RL

My employer holds an optional annual programming game, and in 2019 we could write "bots" to play a game called Tower Defense.
I used this as an excuse to try out a reinforcement learning technique.
In particular, I implemented a version of vanilla Policy Gradients using code inspired by Andrei K's Pong from Pixels.
My parameterized policy requires a probability of selecting each of several types of actions (e.g., build an "attack" building, build a "defense" building), and the goal of the Policy Gradients is to learn these probabilities, which can vary as the state evolves as specified by a neural network.
More specifically, I built a ~30-state vector describing the state and then pass that through the neural network to get the corresponding probabilities of each action type.
I used a very shallow neural network with just one hidden layer in my policy (and so I named my bot "shallowmind"), and I implemented the gradient updates using NumPy as a learning exercise.
Once an action type is selected, some heuristics are used to figure out the details (i.e., where to build the building on the map).
I only ended up with time to run 2 100-game batches before my submission, and furthermore there are many possible enhancements (and probably bug fixes!) to this approach.
I'm putting this up on github in hopes that I (or others?) might pursue some of these possible enhancements. Some of these possible enhancements include:
- Streamlining training and running it for longer to see how much the RL approach can improve performance.
- Enhancing the calculation of the "advantage" by, for example, using a discount factor and an estimate of the value function (making this more of an actor-critic approach).
- Trying out a deeper network using a more raw depiction of the state.
- Trying out a whole different RL framework (something related to the value function instead of a policy gradient approach).

## Tower Defense Game

You can learn more about the game from [its repo](https://github.com/EntelectChallenge/2018-TowerDefence).

## Getting started

### Python Installation:

Simply download the desired version of Python and OS from https://www.python.org/downloads/. I used Python 3.7.3 ([Anaconda distribution](https://www.anaconda.com/distribution/)).
	
Once Installed ensure python has been installed correctly and works bt following these instructions :
- In command line enter the command "python" (without quotes)
- You should get a similar output to the following
```
Python 3.7.3 (default, Apr 24 2019, 15:29:51) [MSC v.1915 64 bit (AMD64)] :: Anaconda, Inc. on win32
Type "help", "copyright", "credits" or "license" for more information.
>>>
```			
		
### Python Environment:

I managed my environment with a conda environment, specified with the `environment.yml` file.
You can re-create the environment with this command:
```
conda env create -f environment.yml
```

## Provided instructions for creating a bot
 	
Copy the python3 starter-bot folder, be sure to keep the TowerDefense.py and TowerDefenseHelper.py files. 
Copy the StarterBot.py with the name of your choice. Modify the class name inside the copied file
Update the main initialization at the bottome to pass your new bot to the TowerDefense.run method
ex. TowerDefense.run(MyNewBot())

## Running the sample bot:

Run the following:
```
python MyNewBot.py
```

## Playing the game

To actually play the game, you'll need a .jar file.
Let me know if you want that and I can send it along.

## Visualizing games

I was also provided a game replay visualizer .exe that I can share if you're interested.
The game-playing .jar file dumps a bunch of files into a directory for the visualizer to use.
