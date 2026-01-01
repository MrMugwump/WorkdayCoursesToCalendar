How to use:
- Download a CSV of your classes from Workday
    - Workday -> Academics -> View My Courses
    - I don't think Workday allows you to download a CSV, so download the excel file and convert that to a CSV
- Copy the file path to the CSV
- Run createCalFile.py in command line
    - If you don't have python installed you will have to install that first.
        - once installing python, you will have to install pandas as well, just type "pip install pandas" into the terminal.
    - Once you succesfully run createCalFile.py, paste the file path when prompted.
- A file titled courses.ics will have now been created in the same folder that createCalFile.py is in. All that is left is to import courses.ics into whatever calendar software you use.

The title of each event will be the full course title listed on Workday.
The description will be the room and instructor.

Its very possible that online classes will be formatted differently, and this program will (most likely) not be able to handle that.