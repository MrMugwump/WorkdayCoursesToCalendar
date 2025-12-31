How to use:
- Download a CSV of your classes from Workday
    - Workday -> Academics -> View My Courses
    - I don't think Workday allows you to download a CSV, so download the excel file and convert that to a CSV
- Copy the file path to the CSV
- Run this program in command line
    - Paste the file path when prompted

Dependencies: 
- pandas

The title of each event will be the full course title listed on Workday.
The description will be the room and instructor.

Its very possible that online classes will be formatted differently, and this program will (most likely) not be able to handle that.