import psycopg2
import csv
from settings import DATABASE
from datetime import datetime, timedelta


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
        date = row[0]
        time = row[2]
        dateTime = datetime.strptime(
            date + time,
            '%d %B %Y%I.%M %p'
        )
        code = row[3]
        duration = timedelta(hours=float(row[5]))

        try:
            cursor.execute(
                '''
                UPDATE modules
                SET  exam_time = %s, exam_duration = %s
                WHERE school = %s AND code = %s AND year = %s AND sem = %s;
                ''',
                (dateTime, duration, 'NTU', code, 2016, 1)
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
