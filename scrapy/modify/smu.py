import psycopg2
import csv
from settings import DATABASE
from datetime import datetime, timedelta
from math import ceil

school = 'SMU'
year = 2016
sem = 1
lesson_type = 'SEM'


def differenceInWeeks(dateTime, anotherDateTime):
    daysDifference = abs((dateTime - anotherDateTime).days)
    return int(ceil((daysDifference + 1.0) / 7))


def weekText(date, anotherDate):
    dateFormat = '%m/%d/%Y'
    startDate = datetime.strptime('8/15/2016', dateFormat)
    dateTime = datetime.strptime(date, dateFormat)
    anotherDateTime = datetime.strptime(anotherDate, dateFormat)


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
    lessonUidSet = set()
    for row in examsReader:
        startdate = row[2]
        enddate = row[3]
        week_text = 
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
                INSERT INTO modules (
                school,
                year,
                sem,
                code,
                title,
                credit,
                remarks,
                department,
                prerequisite,
                preclusion,
                availability,
                description,
                exam_time,
                exam_venue,
                exam_duration
                ) values (
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s
                ) ON CONFLICT (school, year, sem, code) DO UPDATE SET (
                title,
                credit,
                remarks,
                department,
                prerequisite,
                preclusion,
                availability,
                description,
                exam_time,
                exam_venue,
                exam_duration
                ) = (
                EXCLUDED.title,
                EXCLUDED.credit,
                EXCLUDED.remarks,
                EXCLUDED.department,
                EXCLUDED.prerequisite,
                EXCLUDED.preclusion,
                EXCLUDED.availability,
                EXCLUDED.description,
                EXCLUDED.exam_time,
                EXCLUDED.exam_venue,
                EXCLUDED.exam_duration
                );
                ''',
                (school,
                 year,
                 sem,
                 code,
                 title,
                 0,
                 remarks,
                 department,
                 None,
                 None,
                 None,
                 None,
                 None,
                 None,
                 None
                 )
            )

            cursor.execute(
                '''
                INSERT INTO lessons (
                modules_id,
                class_no,
                day_text,
                lesson_type,
                week_text,
                start_time,
                end_time,
                venue
                ) values (
                (SELECT id from modules
                WHERE school = %s AND year = %s
                AND sem = %s AND code = %s),
                %s, %s, %s,
                %s, %s, %s,
                %s
                );
                ''',
                (school,
                 year,
                 sem,
                 code,
                 class_no,
                 day_text,
                 lesson_type,
                 week_text,
                 start_time,
                 end_time,
                 venue
                 )
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

