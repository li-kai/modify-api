import psycopg2
import re
import csv
from settings import DATABASE, YEAR, SEM
from datetime import datetime, timedelta

school = 'NTU'
with open('exams.csv', 'rb') as csvfile:
    try:
        connection = psycopg2.connect(
            database=DATABASE['database'],
            user=DATABASE['username'],
            password=DATABASE['password'],
            host=DATABASE['host']
        )
        cursor = connection.cursor()

        cursor.execute(
            '''
            UPDATE modules SET exam_time = null, exam_duration = null
            WHERE school = %s AND year = %s AND sem = %s;
            ''',
            (school, YEAR, SEM)
        )
        connection.commit()
    except Exception, e:
        connection.rollback()
        raise e

    examsReader = csv.reader(csvfile, delimiter=',')
    for row in examsReader:
        date = row[0]
        time = row[2]
        dateTime = datetime.strptime(
            date + time,
            '%d %B %Y%I.%M %p'
        )
        code = re.match(r'[A-Z0-9]+', row[3]).group(0)
        duration = timedelta(hours=float(row[5]))

        try:
            cursor.execute(
                '''
                UPDATE modules
                SET  exam_time = %s, exam_duration = %s
                WHERE school = %s AND code = %s AND year = %s AND sem = %s;
                ''',
                (dateTime, duration, school, code, YEAR, SEM)
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

