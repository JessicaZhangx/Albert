import os
import pandas as pd
import pymysql.cursors

conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='albert',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)
'''
class row:
	#ignore class status, session, start/end date (add sem/year ), description, 
	#component = class_type
	#min/max units = credits
	#building room = room_num/building
	#primary instructor = first_name, last_name 
	def __init__(self, catalog_num, class_section, title, classnbr, days, 
		timest, sem, year, class_type, credits, consent, course_id, location,
		room_num, building, room_cap, enroll_cap, enroll_tot, waitlist_cap, waitlist_tot,
		combined, class_topic, first_name, last_name):
		self.catalog_num = catalog_num
		self.class_section = class_section
		self.title = title
		self.classnbr = classnbr
		self.days = days
		self.timest = timest
		self.sem = sem
		self.year = year
		self.class_type = class_type
		self.credits = credits
		self.consent = consent
		self.course_id = course_id
		self.location = location
		self.room_num = room_num
		self.building = building
		self.room_cap = room_cap
		self.enroll_cap = enroll_cap
		self.enroll_tot = enroll_tot
		self.waitlist_cap = waitlist_cap
		self.waitlist_tot = waitlist_tot
		self.combined = combined
		self.class_topic = class_topic
		self.first_name = first_name
		self.last_name = last_name

def readFile():
    rows = []
    excel_file = "data.xlsx"
    data = pd.read_excel(excel_file)
    j = 2;
    for index, row in data.iterrows():
      print("row" + str(j))
      #add sem/year
      if (row["Start/End Date"][1] == "9"):
          sem = "Fall"
      else:
          sem = "Spring"
          
      year = row["Start/End Date"][-4:]
      
      #add building  
      
      #if empty
      if (pd.isnull(row["Building Room"])):
          building = ""
          room_num = ""
      #if online
      elif(row["Building Room"] == "On-Line"):
          building = "Online"
          room_num = "N/A"
      else:
          build = row["Building Room"].split(" Rm ")
          building = build[0]
          room_num = build[1]
      
      #add Instructors
      
      #No instructor
      if(pd.isnull(row["Primary Instructor"])):
          first_name = ""
          last_name = ""
          x = addRow(row, sem, year, room_num, building, first_name, last_name)
          rows.append(x)
     #2 instructors
      elif ("&" in row["Primary Instructor"]):
          names = row["Primary Instructor"].split("& ")
          for i in names:
              name = i.split(",")
              x = addRow(row, sem, year, room_num, building, name[0], name[1])
              rows.append(x)
     #1 instructor
      else:
          name = row["Primary Instructor"].split(",")
          x = addRow(row, sem, year, room_num, building, name[0], name[1])
          rows.append(x)
      j+=1
      
    course_sheet(rows)
def addRow(line, sem, year, room_num, building, first_name, last_name):          
       x = row(line["Subject/Catalog#"], line["Class Section"], line["Class Title"], 
                line["Class Nbr"], line["Days"], line["Time"], sem, year ,line["Component"],
                line["Min/Max Units"], line["Consent"], line["Course ID"], line["Location"],
                room_num, building, line["Room Cap"], line["Enrollment Capacity"], 
                line["Enrollment Total"], line["Class Wait List Cap"], line["Wait List Total"],
                line["Combined Status"], line["Class Topic"], first_name, last_name)
       return x
'''
    
def course_sheet(data):
    
    cursor = conn.cursor()
    
    df = pd.DataFrame({"Course ID":data["Course ID"], "Class Title":data["Class Title"], 
                  "Subject/Catalog#":data["Subject/Catalog#"], 
                  "Credits":data["Min/Max Units"], "Consent":data["Consent"], "Location":data["Location"]})
    df = df.drop_duplicates("Course ID")
    
    for index, row in df.iterrows():
        if(row["Consent"] != "Dept"):
            df.set_value(index, "Consent", "No")
    
    for index, row in df.iterrows():
        query = 'INSERT INTO course(course_id, title, catalog_num, credits, consent, location) VALUES (%s, %s, %s, %s,%s,%s) ON DUPLICATE KEY UPDATE title = VALUES(title), catalog_num = VALUES(catalog_num), credits = VALUES(credits), consent = VALUES(consent), location = VALUES(location)'
        cursor.execute(query, (row["Course ID"], row["Class Title"], row["Subject/Catalog#"], row["Credits"], row["Consent"], row["Location"]))    
    
    conn.commit()
    cursor.close()

def split_classroom(data):
    room_num = []
    building = []
    for index, row in data.iterrows():
      if (pd.isnull(row["Building Room"])):
          building.append("N/A")
          room_num.append("N/A")
      #if online
      elif(row["Building Room"] == "On-Line"):
          building.append("Online")
          room_num.append("N/A")
      elif(row["Building Room"] == "No Room Required"):
          building.append("No Room")
          room_num.append("N/A")
      elif(row["Building Room"] == "Dibner , Pfizer Auditorium"):
          building.append("Dibner")
          room_num.append("Pfizer Auditorium")
      elif("Rm" in row["Building Room"]):
          build = row["Building Room"].split(" Rm ")
          room_num.append(build[1])  
          if("," in build[0]):
              building.append(build[0].rstrip(","))
          else:
              building.append(build[0])
      else:
          building.append("Unknown")
          room_num.append("Unknown")
          
    return room_num, building

def split_instructor(data):
    first_name = []
    last_name = []
    
    #add Instructors      
    #No instructor
    for index, row in data.iterrows():
        if(pd.isnull(row["Primary Instructor"])):
            first_name.append("N/A")
            last_name.append("N/A")
        #2 instructors
        elif ("&" in row["Primary Instructor"]):
            names = row["Primary Instructor"].split(" & ")
            for i in names:
                name = i.split(",")
                if(len(name) > 1):
                    first_name.append(name[1])
                else:
                    first_name.append("N/A")
                if(name[0]):
                    last_name.append(name[0])
                else:
                    last_name.append("N/A")
         #1 instructor
        else:
            name = row["Primary Instructor"].split(",")
            first_name.append(name[1])
            last_name.append(name[0])
    return first_name, last_name
def classroom_sheet(data):
    #go through the data frame and add it in two separate dictionaries, add that in with room Cap
    cursor = conn.cursor()
    
    room_num, building = split_classroom(data)
             
    df = pd.DataFrame({"room_num":room_num, "building":building, "room_cap":data["Room Cap"]})
    df = df.drop_duplicates(subset=["room_num", "building"])
    
    df["room_cap"] = df["room_cap"].astype(str) 
    for index, row in df.iterrows():
        if(row["room_cap"] == "nan"):
          df.set_value(index, "room_cap", "N/A")

    
    for index, row in df.iterrows():
        query = 'INSERT INTO classroom(room_num, building, room_cap) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE room_num = VALUES(room_num), building = VALUES(building), room_cap = VALUES(room_cap)'
        cursor.execute(query, (row["room_num"], row["building"], row["room_cap"]))    
                                 
    conn.commit()
    cursor.close()
    
    
def instructor_sheet(data):
    #go through data frame, parse instructor and add dictionaries and write it back in
    cursor = conn.cursor()
    
    first_name, last_name = split_instructor(data) 
        
    df = pd.DataFrame({"first_name":first_name, "last_name":last_name})
    df = df.drop_duplicates(subset=["first_name", "last_name"])
    
    for index, row in df.iterrows():
        query = 'INSERT INTO instructor(first_name, last_name) VALUES (%s, %s) ON DUPLICATE KEY UPDATE first_name = VALUES(first_name), last_name = VALUES(last_name)'
        cursor.execute(query, (row["first_name"], row["last_name"]))    
                                 
    conn.commit()
    cursor.close()
 
def time_sheet(data):
    
    cursor = conn.cursor()
    
    df = pd.DataFrame({"days":data["Days"], "timest":data["Time"]})
    df = df.drop_duplicates(subset=["days","timest"])
    
    for index, row in df.iterrows():
        if(pd.isnull(row["days"])):
            df.set_value(index, "days", "N/A")
        if(pd.isnull(row["timest"])):
            df.set_value(index, "timest", "N/A")
    
    for index, row in df.iterrows():
        query = 'INSERT INTO class_time(days, timest) VALUES (%s, %s) ON DUPLICATE KEY UPDATE days = VALUES(days), timest = VALUES(timest)'
        cursor.execute(query, (row["days"], row["timest"]))  
    
    conn.commit()
    cursor.close()
    

def teaches_sheet(data):
    #class_section, sem, year, course_id, first_name, last_name
    cursor = conn.cursor()
    
    class_section = []
    sem = []
    year = []
    course_id = []
    first_name = []
    last_name = []
    
    #checking month/year
    if (data["Start/End Date"][0][1] == "9"):
        sems = "Fall"
    else:
        sems = "Spring"
    years = data["Start/End Date"][0][-4:]
    

    for index, row in data.iterrows():
      if(pd.isnull(row["Primary Instructor"])):
          class_section.append(row["Class Section"])
          course_id.append(row["Course ID"])
          sem.append(sems)
          year.append(years)
          first_name.append("N/A")
          last_name.append("N/A")  
      elif("&" in row["Primary Instructor"]):
          names = row["Primary Instructor"].split(" & ")
          for i in names:
              class_section.append(row["Class Section"])
              course_id.append(row["Course ID"])
              sem.append(sems)
              year.append(years)
              name = i.split(",")
              if(len(name) > 1):
                  first_name.append(name[1])
              else:
                  first_name.append("N/A")
              if(name[0]):
                  last_name.append(name[0])
              else:
                  last_name.append("N/A")
      else:
          class_section.append(row["Class Section"])
          course_id.append(row["Course ID"])
          sem.append(sems)
          year.append(years)
          #add instructor
          name = row["Primary Instructor"].split(",")
          first_name.append(name[1])
          last_name.append(name[0])
          
    df = pd.DataFrame({"class_section":class_section, "sem":sem, "year":year, "course_id":course_id, "first_name":first_name, "last_name":last_name})
    for index, row in df.iterrows():
        query = 'INSERT INTO teaches(class_section, sem, year, course_id, first_name, last_name) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE class_section = VALUES(class_section), sem = VALUES(sem), year = VALUES(year), course_id = VALUES(course_id), first_name = VALUES(first_name), last_name = VALUES(last_name)'
        cursor.execute(query, (row["class_section"], row["sem"], row["year"], row["course_id"], row["first_name"], row["last_name"]))  
    
    conn.commit()
    cursor.close()
    

def cross_listed_sheet(data):
    #class_section_u, sem_u, year_u, course_id_u, class_section_g, sem_g, year_g, course_id_g
    #match with title, professor 
    cursor = conn.cursor()
    
    class_section_u =[]
    sem_u = []
    year_u = []
    course_id_u = []
    class_section_g = []
    sem_g = []
    year_g = []
    course_id_g = []
    
    undergrad = []
    
    #checking month/year
    if (data["Start/End Date"][0][1] == "9"):
        sems = "Fall"
    else:
        sems = "Spring"
    years = data["Start/End Date"][0][-4:]
    
    #grab data that is crosslisted
    for index, row in data.iterrows():
        if(row["Combined Status"] == "Combin" and "UY" in row["Subject/Catalog#"]):
            undergrad.append(row)

    #go through each data and find the crosslisted part 
    for under in undergrad:
        for index, row in data.iterrows():
            if(under["Class Title"].lower() == "computer security" and row["Class Title"].lower() == "information security & privacy" and under["Primary Instructor"] == row["Primary Instructor"] and "GY" in row["Subject/Catalog#"] and under["Days"] == row["Days"] and under["Time"] == row["Time"]):
                class_section_u.append(under["Class Section"])
                sem_u.append(sems)
                year_u.append(years)
                course_id_u.append(under["Course ID"])
                
                class_section_g.append(row["Class Section"])
                sem_g.append(sems)
                year_g.append(years)
                course_id_g.append(row["Course ID"])
            
            elif(under["Class Title"].lower() == "interactive computer graphics" and row["Class Title"].lower() == "interact comp graphics" and under["Primary Instructor"] == row["Primary Instructor"] and "GY" in row["Subject/Catalog#"] and under["Days"] == row["Days"] and under["Time"] == row["Time"]):
                class_section_u.append(under["Class Section"])
                sem_u.append(sems)
                year_u.append(years)
                course_id_u.append(under["Course ID"])
                
                class_section_g.append(row["Class Section"])
                sem_g.append(sems)
                year_g.append(years)
                course_id_g.append(row["Course ID"])
            elif(under["Class Title"].lower() == row["Class Title"].lower() and under["Primary Instructor"] == row["Primary Instructor"] and "GY" in row["Subject/Catalog#"] and under["Days"] == row["Days"] and under["Time"] == row["Time"]):
                
                class_section_u.append(under["Class Section"])
                sem_u.append(sems)
                year_u.append(years)
                course_id_u.append(under["Course ID"])
                
                class_section_g.append(row["Class Section"])
                sem_g.append(sems)
                year_g.append(years)
                course_id_g.append(row["Course ID"])
    
    df = pd.DataFrame({"class_section_u":class_section_u, "sem_u":sem_u, "year_u":year_u, "course_id_u":course_id_u, "class_section_g": class_section_g, "sem_g":sem_g, "year_g":year_g, "course_id_g":course_id_g})
    for index, row in df.iterrows():
        query = 'INSERT INTO crosslisted(class_section_u, sem_u, year_u, course_id_u, class_section_g, sem_g, year_g, course_id_g) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE class_section_u = VALUES(class_section_u), sem_u = VALUES(sem_u), year_u = VALUES(year_u), course_id_u = VALUES(course_id_u), class_section_g = VALUES(class_section_g), sem_g = VALUES(sem_g), year_g = VALUES(year_g), course_id_g = VALUES(course_id_g)'
        cursor.execute(query, (row["class_section_u"], row["sem_u"], row["year_u"], row["course_id_u"], row["class_section_g"], row["sem_g"], row["year_g"], row["course_id_g"]))  

    conn.commit()
    cursor.close()

            
def section_sheet(data):
    #class_section, sem, year course_id, room_num, building, day, timest, classnbr, class_type, enroll_cap, enroll_tot, waitlist_cap, class_topic, waitlist_tot, consent
    cursor = conn.cursor()
    
    sem = []
    year = []
    
    room_num, building = split_classroom(data)
    
    #checking month/year
    for index, row in data.iterrows():
        if (data["Start/End Date"][0][1] == "9"):
            sem.append("Fall")
        else:
            sem.append("Spring")
        year.append(data["Start/End Date"][0][-4:])
            
        data["Enrollment Capacity"] = data["Enrollment Capacity"].astype(str) 
        data["Enrollment Total"] = data["Enrollment Total"].astype(str) 
        data["Class Wait List Cap"] = data["Class Wait List Cap"].astype(str) 
        data["Class Topic"] = data["Class Topic"].astype(str)   
        data["Wait List Total"] = data["Wait List Total"].astype(str) 
        data["Consent"] = data["Consent"].astype(str) 
        
        if(row["Enrollment Capacity"] == "nan"):
            data.set_value(index, "Enrollment Capacity", "N/A")
        if(row["Enrollment Total"] == "nan"):
            data.set_value(index, "Enrollment Total", "N/A")
        if(pd.isnull(row["Class Wait List Cap"])):
            data.set_value(index, "Class Wait List Cap", "N/A")
        if(pd.isnull(row["Class Topic"])):
            data.set_value(index, "Class Topic", "N/A")
        if(pd.isnull(row["Wait List Total"])):
            data.set_value(index, "Wait List Total", "N/A")
        if(row["Consent"] == "nan"):
            data.set_value(index, "Consent", "No")
        if(pd.isnull(row["Days"])):
            data.set_value(index, "Days", "N/A")

            
        
    df = pd.DataFrame({"class_section":data["Class Section"], "sem":sem, "year":year, "course_id":data["Course ID"], "room_num":room_num, "building":building, "day":data["Days"], "timest":data["Time"], "classnbr":data["Class Nbr"], 
                       "class_type":data["Component"], "enroll_cap":data["Enrollment Capacity"], "enroll_tot":data["Enrollment Total"], "waitlist_cap":data["Class Wait List Cap"], 
                       "class_topic":data["Class Topic"], "waitlist_tot":data["Wait List Total"], "consent":data["Consent"]})
    for index, row in df.iterrows():
        query = 'INSERT INTO section(class_section, sem, year, course_id, room_num, building, days, timest, classnbr, class_type, enroll_cap, enroll_tot, waitlist_cap, waitlist_tot, class_topic, consent) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE class_section = VALUES(class_section), sem = VALUES(sem), year = VALUES(year), course_id = VALUES(course_id), room_num = VALUES(room_num), building = VALUES(building), days = VALUES(days), timest = VALUES(timest), classnbr = VALUES(classnbr), class_type = VALUES(class_type), enroll_cap = VALUES(enroll_cap), enroll_tot = VALUES(enroll_tot), waitlist_cap = VALUES(waitlist_cap), waitlist_tot = VALUES(waitlist_tot), class_topic = VALUES(class_topic), consent = VALUES(consent)'
        cursor.execute(query, (row["class_section"], row["sem"], row["year"], row["course_id"], row["room_num"], row["building"], row["day"], row["timest"], row["classnbr"], row["class_type"], row["enroll_cap"], row["enroll_tot"], row["waitlist_cap"], row["waitlist_tot"], row["class_topic"], row["consent"]))  

    conn.commit()
    cursor.close()
          

def run_sheets(data): 
    course_sheet(data)
    classroom_sheet(data)
    instructor_sheet(data)
    time_sheet(data)
    section_sheet(data)
    teaches_sheet(data)
    cross_listed_sheet(data)

def main():
    print("Select 1 to run all files")
    print("Select 2 to run latest file")
    choice = input("What would you like to do? ")
    
    dirs = os.listdir(os.getcwd()) #get current directory and list 
    if(choice == "1"):        
        for file in dirs:
            if(file != "automate.py"):
                print(file)
                data = pd.read_excel(file)
                run_sheets(data)
                print("done")
    elif(choice == "2"):
        latest_file = max(dirs, key=os.path.getctime)
        print(latest_file)
        data = pd.read_excel(latest_file)
        run_sheets(data)
        print("done")
        

main()
    
    

	