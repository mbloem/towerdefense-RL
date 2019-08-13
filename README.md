# towerdefense-RL

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
