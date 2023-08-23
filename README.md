# GameOfLifeBMP
GameOfLifeBMP is a project made to explore the popular game by John Horton Conway, the [Game of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life).

This project is currently quite buggy, and relies on some tkinter and selenium mess to work. The plan is to fix these down the line.

# What is Conway's Game of Life?
The Game of Life is a cellular automaton devised by the British mathematician John Horton Conway in 1970. It is a zero-player game, meaning that its evolution is determined by its initial state, requiring no further input. 
One interacts with the Game of Life by creating an initial configuration and observing how it evolves. (from [Wikipedia](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life))

In this case, the initial state is any given bitmap (.bmp) file. The evolution is observed through your web browser.

# What does this project do?
Essentially, an inputted bitmap image is split into every one of its pixels. Each pixel is made up of it's RGB colour values, usually an integer. This integer can then be split into all of its bits forming a 3D object where the length and width are the length and width of the bitmap and the height is the amount of bits in one pixel. Now you can imagine splitting this 3D object into a bunch of 2D objects with the same length and width. All that happens now is the Game of Life algorithm is played on each of these subsections of the image. Once a generation has been computed, the bitmap is reassembled and displayed.
This algorithm leads to some crazy results like image colours being inverted, infections of different colours and a lot of very interesting patterns.

Unlike [this project](https://www.stringham.me/conway/) there are no arbitrary rules to decide on whether a pixel is "alive" or "dead". It replicates the original algorithm exactly.

# Why?
I got into a rabbit hole learning about bitmap files and the Game of Life, and I decided to combine both into one project! There is also lots of very interesting math that goes into how the algorithm works, which is exactly what I enjoy learning about.

This was also my first time messing with bit structure and bitwise functions as I had never had a use for these before.

# How do I run it?
To start, make sure you have [Firefox](https://www.mozilla.org/en-CA/firefox/new/) installed.
You will also need to install selenium using `pip install selenium`.

Once everything is installed, clone this repository and run the `__main__.py` file. You should see a window appear where you can select a file and decide on the Game of Life rules. 
Once you're ready press "Run" and a browser window will open and refresh everytime a new generation is calculated.
