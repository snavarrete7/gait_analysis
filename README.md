# gait-analysis
SERENE all-in-one Gait Analysis Tool

* For now, configuration data should be stored in this directory, in 'app/'. This way it'll be accessible for the application, but the path can be changed.

## Model ##
Contains all data definitions

* globalvars: A reference to the global scope variables used throughout the program. It should be imported with 'import src.model.globalvars' syntax, not with 'from src.model.globalvars import *', since this last syntax creates a copy, and will only affect changes in the same module.


## Tools ##
Contains helper functions to aid throughout the entirety of the application main code, as well as some core calculations.

## Forms ##
* skel: Definition of all graphical components. You can edit styling, placement of widgets, customize each particular widget in appearance and functionality. The class handles initialization of the form and start the main event loop, to handle user input.

* utils: Callbacks for each widget action, as well as some helper functions.

* tl_xxx: Same as above, but for pop-up windows that are customizable in appearance and functionality.

* Set documents folder in src/forms/, function form_load()

* 'Entry' widgets have their content associated to a tkinter Variable, you can retrieve them from a dictionary with the name of the widget as a key (see )

* mappingWidgets.txt: used to locate faster (Ctrl + F) which Tab a widget belongs to. Search by widget name.