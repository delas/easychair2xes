# easychair2xes

This script allows the construction of an event log starting from the EasyChair system, to be analyzed using process mining tools.

In order to extract the log you need to be *superchair* of a conference in EasyChair and you need to click the *Events* button on the top bar. You can then select all events, and copy them into a spreadsheet, where you need to change the dates to the format `YYYY-MM-DD`. After that you can copy all rows and paste them inside the `easychair2xes.py` script. Having a fully self-contained script allows to run in on online services like Google Colab.

<img width="500" src="https://raw.githubusercontent.com/delas/easychair2xes/main/screenshot.jpg" />


*Andrea Burattin*  
https://andrea.burattin.net
