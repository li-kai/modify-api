import psycopg2
import csv
from settings import DATABASE
from datetime import datetime, timedelta

school = 'SMU'
year = 2016
sem = 1
lesson_type = 'SEM'
with open('exams.csv', 'rb') as csvfile:
    try:
        connection = psycopg2.connect(
            database=DATABASE['database'],
            user=DATABASE['username'],
            password=DATABASE['password'],
            host=DATABASE['host']
        )
        cursor = connection.cursor()
    except Exception, e:
        raise e

    examsReader = csv.reader(csvfile, delimiter=',')
    for row in examsReader:
        startdate = row[2]
        enddate = row[3]
        department = row[4]
        code = department + row[5]
        title = row[6]
        class_no = row[7]
        meet = row[8]
        day_text = row[9]
        start_time = row[10]
        end_time = row[11]
        venue = row[12]
        remarks = row[16]
        
        try:
            cursor.execute(
                '''
                UPDATE modules
                SET  exam_time = %s, exam_duration = %s
                WHERE school = %s AND code = %s AND year = %s AND sem = %s;
                ''',
                (dateTime, duration, school, code, year, sem)
            )
            # commit the change
            connection.commit()
        except Exception as e:
            print "Error: %s" % e
            connection.rollback()
            raise
    try:
        cursor.close()
        connection.close()
    except Exception, e:
        raise e

