# fast5surfer
![Logo](https://user-images.githubusercontent.com/41163796/123153288-ca8dad00-d465-11eb-935d-f2550d7c2fc1.jpg)

A custom GUI based software tool for the handling, exploration and visualization of fast5 produced by sequencing instrumentations of the Oxford NanoPore Technology.
To use the software tool:
1) make a a git pull of the repository
2) create a new Python virtual environment
3) install all dependencies from the requirements.txt file
4) open a new console and activate the new virtual environment
5) lauch "python __init__.py" command to start the program.

Once done this, it is possible to use fast5surfer tool with its GUI. 
First of all select a folder with the "Select a folder to explore" button.
After folder selection, the folder tree will be visualised and it is possibile to select from the left panel a valid fast5 to explore.
The content of the selected fast5 file will be showed on the top of the right panel as a hierarchical representation of its structure. 
Either Attributes (metadata of groups and datasets elements of the fast5 file), Data and the plot will be reproduced on the bottom of the righ panel named "Fast5 File".
The plot tab is available only for the fast5 dataset elements containing the raw ionic current signal.


https://user-images.githubusercontent.com/41163796/123151611-ed1ec680-d463-11eb-98d0-5005fe2c6ec3.mp4
