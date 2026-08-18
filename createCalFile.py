import pandas as pd
import datetime

timezoneText ="X-WR-TIMEZONE:America/Chicago\nBEGIN:VTIMEZONE\nTZID:America/Chicago\nX-LIC-LOCATION:America/Chicago\nBEGIN:DAYLIGHT\nTZOFFSETFROM:-0600\nTZOFFSETTO:-0500\nTZNAME:CDT\nDTSTART:19700308T020000\nRRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU\nEND:DAYLIGHT\nBEGIN:STANDARD\nTZOFFSETFROM:-0500\nTZOFFSETTO:-0600\nTZNAME:CST\nDTSTART:19701101T020000\nRRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU\nEND:STANDARD\nEND:VTIMEZONE\n"

def formatDaysAndTime(days,times):

    rule = []
    for char in days:
        if char == "M":
            rule.append("MO")
        elif char == "T":
            rule.append("TU")
        elif char == "W":
            rule.append("WE")
        elif char == "R":
            rule.append("TH")
        elif char == "F":
            rule.append("FR")
        # match char:
        #     case "M":
        #         rule.append("MO")
        #     case "T":
        #         rule.append("TU")
        #     case "W":
        #         rule.append("WE")
        #     case "R":
        #         rule.append("TH")
        #     case "F":
        #         rule.append("FR")
    timeSlot=[]
    startAndEndTimes = times.split("-")
    for time in startAndEndTimes:
        offset = 0
        if "PM" in time:
            cleanedTime = time.replace(" PM","").split(":") # Deletes the PM off the end and splits into hours and minutes
            if int(cleanedTime[0]) != 12: # Hours
                offset = 12
        elif "AM" in time:
            cleanedTime = time.replace(" AM","").split(":")
                
        
        hours = int(cleanedTime[0])+offset #offset is for am/pm
        minutes = int(cleanedTime[1])

        #Some additional formatting, need exactly six digits, so 95500 becomes 095500
        strToAdd = ""
        if hours < 10:
            strToAdd = "0"+str(hours*(10**4)+minutes*(10**2))
        else:
            strToAdd = str(hours*(10**4)+minutes*(10**2))
        timeSlot.append(strToAdd) # formatting to turn the time into acceptable strings
    return [rule,timeSlot]

# This version is for classes
def processMeetingPatternsForClasses(meetingInfo): 
    info = meetingInfo.split("|")
    [rule, timeSlot]= formatDaysAndTime(days = info[0], times = info[1])

    description = info[2][1:] # gets rid of the space at the beginning of the string
    return [rule,timeSlot,description]
    
# This version is for teaching assignments. 
# Im doing this in a slightly stupid way in order to minimize the amount of code 
# I have to change in order to add the capability to do teaching assignments without
# just creating a second python script. So if you notice how much unnecessary repeated code I have 
# you know why.
def processMeetingPatternsForTeaching(meetingInfo, classroomInfo):
    info = meetingInfo.split("|")
    [rule, timeSlot]= formatDaysAndTime(days = info[0], times = info[1])

    return [rule,timeSlot,classroomInfo]

# This correctly formats the start and end dates, 
# manually adjusting the start date to be the actual first day of class 
# rather than the start of the semester, which is what workday gives. 
def processStartAndEndDate(startDate,endDate,frequency):
    splitStart = startDate.split("/")
    splitEnd = endDate.split("/")

    semesterStart = datetime.date(int(splitStart[2]),int(splitStart[0]),int(splitStart[1]))
    semesterStartWeekday = semesterStart.weekday() # Monday = 0, Sunday = 6

    #Adjusting the start date to match the meeting times 
    #This is needed as the start of the semester is the given start date, but that is not necessarily when the first class is.
    datesAsInt = [] 
    for date in frequency:
        if date=="MO":
            datesAsInt.append(0)
        elif date=="TU":
            datesAsInt.append(1)
        elif date=="WE":
            datesAsInt.append(2)
        elif date=="TH":
            datesAsInt.append(3)
        elif date=="FR":
            datesAsInt.append(4)
        # match date:
        #     case "MO":
        #         datesAsInt.append(0)
        #     case "TU":
        #         datesAsInt.append(1)
        #     case "WE":
        #         datesAsInt.append(2)
        #     case "TH":
        #         datesAsInt.append(3)
        #     case "FR":
        #         datesAsInt.append(4)

    dateAdjustment=0
    # print(datesAsInt[len(datesAsInt)-1])
    if semesterStartWeekday > datesAsInt[len(datesAsInt)-1]: # If the semester change occurs on a weekend, shift the start date to the first day in the week that the class occurs.
        dateAdjustment = 7-semesterStartWeekday + datesAsInt[0] 
    else: 
        for i in range(len(datesAsInt)-1,0,-1): # Going backwards from the last day in the week
            if datesAsInt[i] >= semesterStartWeekday and datesAsInt[i-1] < semesterStartWeekday: # If between the current day and the previous class, shift to current day
                dateAdjustment = datesAsInt[i] - semesterStartWeekday
                break
        if semesterStartWeekday <= datesAsInt[0]:
            dateAdjustment = datesAsInt[0]-semesterStartWeekday
    # print(dateAdjustment)
    startingDay = semesterStart + datetime.timedelta(days=dateAdjustment) # Shifts date forward, accounting for month and year changes
    splitStart = startingDay.strftime('%Y/%m/%d').split("/")
    
    for i in range(2): # Making sure in MM and DD
        if len(splitEnd[i])<2:
            splitEnd[i] = "0"+splitEnd[i]

    formattedStart = splitStart[0] + splitStart[1] + splitStart[2] # YYYYMMDD
    formattedEnd = splitEnd[2]+splitEnd[0]+splitEnd[1] #YYYYMMDD
    return [formattedStart,formattedEnd]

response = input("Type 1 if you are converting your course schedule, and 2 if you are converting your teaching schedule: ")
while response != "1" and response != "2":
    print("\nInvalid input")
    response = input("Type 1 if you are converting your course schedule, and 2 if you are converting your teaching schedule: ")
response = int(response)

def recursivelyAskForFilePath():
    filePath = ""
    while filePath == "":
        filePath = input("Paste the file path to the csv here: ")
    try:
        csv = pd.read_csv(filePath,header=2 if response == 1 else 0)
    except FileNotFoundError:
        print("\nInvalid file path. Use only the file path and no quotation marks.\n")
        csv = recursivelyAskForFilePath()
    return csv

workdayCSV = recursivelyAskForFilePath()

header = ["BEGIN:VCALENDAR\n","VERSION:2.0\n",timezoneText]


icsTitle = "courses.ics" if response == 1 else "teachingAssignments.ics"

f = open(icsTitle,"w+")
for i in header:
    f.write(i)

numRows = workdayCSV.shape[0]


# I'm suspicous that workday changes the column titles to 
# be singlular instead of plural if you only have classes that meet once a week. 
# For example, I personally only teach on tuesdays, and it 
# says "Meeting Time" instead of "Meeting Times"
meetingPatternsColumnName = "Meeting Patterns" if response == 1 else "Meeting Time" 
courseTitleColumnName = "Course Listing" if response == 1 else "Course Section"

for i in range(0,numRows):
    if response == 1:
        currClassProcessed = processMeetingPatternsForClasses(workdayCSV.loc[i,meetingPatternsColumnName])
    else:
        currClassProcessed = processMeetingPatternsForTeaching(workdayCSV.loc[i,meetingPatternsColumnName],workdayCSV.loc[i,"Location"])
    meetingDays = currClassProcessed[0]; timeSlot = currClassProcessed[1]; location = currClassProcessed[2]
    startAndEndDates = processStartAndEndDate(
        workdayCSV.loc[i,"Start Date"],workdayCSV.loc[i,"End Date"],meetingDays)

    f.write("BEGIN:VEVENT\n")

    #DTSTART and DTEND specify the length of each class and the first day of class.
    dtstart = "DTSTART:" + str(startAndEndDates[0])+"T"+str(currClassProcessed[1][0])+"\n"
    dtend = "DTEND:" + str(startAndEndDates[0])+"T"+str(currClassProcessed[1][1])+"\n"
    f.write(dtstart+dtend)

    #RRULE specifies the frequency of repetition, the days on which the class repeats, and the last day of class.
    rrule = "RRULE:FREQ=WEEKLY;BYDAY=" 
    for j in range(len(meetingDays)-1):
        rrule = rrule+meetingDays[j]+","
    rrule = rrule+meetingDays[len(meetingDays)-1]+";"
    rrule = rrule+"UNTIL="+str(startAndEndDates[1])+"T"+"235959\n"
    f.write(rrule)

    #SUMMARY provides the title
    title = workdayCSV.loc[i,courseTitleColumnName]
    f.write("SUMMARY:"+title+"\n")

    #LOCATION is just the classroom number and building
    f.write("LOCATION:"+currClassProcessed[2]+"\n")

    #DESCRIPTION provides the description
    if response == 1:
        instructor = workdayCSV.loc[i,"Instructor"]
        description = instructor #\\n to have a line break in the description but not in the .ics file.
    else:
        numOfStudents = workdayCSV.loc[i,"Number of Enrolled Students"]
        description = "Number of students: "+str(numOfStudents)
    f.write("DESCRIPTION:"+ description+"\n")

    f.write("END:VEVENT\n")

f.write("END:VCALENDAR")

print("File succesfully created! File is called: " + icsTitle)
