import pandas as pd
import datetime

def processMeetingPatterns(meetingInfo):
    info = meetingInfo.split("|")
    rule = []
    for char in info[0]:
        match char:
            case "M":
                rule.append("MO")
            case "T":
                rule.append("TU")
            case "W":
                rule.append("WE")
            case "R":
                rule.append("TH")
            case "F":
                rule.append("FR")
    timeSlot=[]
    startAndEndTimes = info[1].split("-")
    for time in startAndEndTimes:
        offset = 0
        if "PM" in time:
            cleanedTime = time.replace(" PM ","").split(":") # Deletes the PM off the end and splits into hours and minutes
            if int(cleanedTime[0]) != 12: # Hours
                offset = 12
        elif "AM" in time:
            cleanedTime = time.replace(" AM ","").split(":")
                
        hours = int(cleanedTime[0])+offset
        minutes = int(cleanedTime[1])
        timeSlot.append(hours*(10**4)+minutes*(10**2)) # formatting to turn the time into acceptable strings

    description = info[2][1:] # gets rid of the space at the beginning of the string
    return [rule,timeSlot,description]
    
def processStartAndEndDate(startDate,endDate,frequency):
    splitStart = startDate.split("/")
    splitEnd = endDate.split("/")

    semesterStart = datetime.date(int(splitStart[2]),int(splitStart[0]),int(splitStart[1]))
    semesterStartWeekday = semesterStart.weekday() # Monday = 0, Sunday = 6

    #Adjusting the start date to match the meeting times 
    #This is needed as the start of the semester is the given start date, but that is not necessarily when the first class is.
    datesAsInt = [] 
    for date in frequency:
        match date:
            case "MO":
                datesAsInt.append(0)
            case "TU":
                datesAsInt.append(1)
            case "WE":
                datesAsInt.append(2)
            case "TH":
                datesAsInt.append(3)
            case "FR":
                datesAsInt.append(4)

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

filePath = ""
while filePath == "":
    filePath = input("Paste the file path to the csv here: ")

workdayCSV = pd.read_csv(filePath,header=2)

header = ["BEGIN:VCALENDAR\n","VERSION:2.0\n"]

f = open("courses.ics","w+")
for i in header:
    f.write(i)

numRows = workdayCSV.shape[0]

for i in range(1,numRows):
    currClassProcessed = processMeetingPatterns(workdayCSV.loc[i,"Meeting Patterns"]) 
    meetingDays = currClassProcessed[0]; timeSlot = currClassProcessed[1]; location = currClassProcessed[2]
    startAndEndDates = processStartAndEndDate(workdayCSV.loc[i,"Start Date"],workdayCSV.loc[i,"End Date"],meetingDays)

    # Create VEVENT
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
    title = workdayCSV.loc[i,"Course Listing"]
    f.write("SUMMARY:"+title+"\n")

    #DESCRIPTION provides the description
    instructor = workdayCSV.loc[i,"Instructor"]
    description = currClassProcessed[2] + "\\n" + instructor #\\n to have a line break in the description but not in the .ics file.
    f.write("DESCRIPTION:"+ description+"\n")

    f.write("END:VEVENT\n")

f.write("END:VCALENDAR")

print("File succesfully created!")