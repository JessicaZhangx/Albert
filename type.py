# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 16:49:35 2018

@author: Jessica
"""

import pandas as pd
import pymysql.cursors

conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='albert',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

def update_course(data):
    cursor = conn.cursor()
    for index, row in data.iterrows():
        query = 'UPDATE course SET course_type = %s WHERE course_id = %s'
        cursor.execute(query, (row["course_type"],row["course_ID"])) 
    conn.commit()
    cursor.close()
    print("updated course")

def update_instructor(data):
    cursor = conn.cursor()
    for index, row in data.iterrows():
        query = 'UPDATE instructor SET faculty_type = %s WHERE first_name = %s AND last_name = %s'
        cursor.execute(query, (row["Faculty Type"],row["first_name"], row["last_name"])) 
    conn.commit()
    cursor.close()
    print("updated instructors")
def main():
    excel_file1 = "instructor.xlsx"
    excel_file2 = "course.xlsx"
    
    print("Select 1 to update instructors")
    print("Select 2 to update course")
    choice = input("What would you like to do? ")
    
    if(choice == "1"):
        instructorData = pd.read_excel(excel_file1)
        update_instructor(instructorData)
    elif(choice == "2"):
        courseData = pd.read_excel(excel_file2)
        update_course(courseData)
    
main()