# PacksGUI
GUI project for the classification, storing and recollection of screenshots from Hearthstone


Motivation
==========
Prior to this GUI, I had been keeping track of pack openings via a spreadsheet.
In order to enter the information of a pack, I needed to have both the spreadsheet, and an image viewer open.
Constantly having to swap between the two applications made the process annoying and slow, both of which could be solved with a custom GUI program.

As well as tracking openings, I was using the spreasheet to calculate basic statistics, and so called pity timers. 
These are additional requirements for the project.

Code Structure
==============
This is my first project using the *tkinter* package for GUI creation, chosen for its presence in the standard python library.

Code aims to be built in the **MVC** (model-view-controller) style, aiming to separate the duties of presentation from those handling data.

As Hearthstone is continually updated, and recieves new content regularly, this project aims to keep its approach flexible. 
Information that will require updating over time is stored within the [config file](PacksGUI_conf.ini), parsed with *configparser*.

Pack opening data is stored in a JSON format file, handled with *tinydb*.

Tests are written with *unittest*, and can currently be run by simply executing [tests.py](tests/tests.py).


**Note:** As this personal project is still in development, code on the master branch may be urefined or unfinished.

**To run the project:** The main file for this project is [layout_test](PacksGUI/layout_test.py).

