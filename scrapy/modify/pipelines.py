# -*- coding: utf-8 -*-
import psycopg2
from settings import DATABASE
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class ModifyPipeline(object):
    """docstring for ModifyPipeline"""

    def __init__(self):
        """
        Initializes database connection.
        """
        try:
            self.connection = psycopg2.connect(
                database=DATABASE['database'],
                user=DATABASE['username'],
                password=DATABASE['password'],
                host=DATABASE['host']
            )
            self.cursor = self.connection.cursor()
        except Exception, e:
            raise e

    def close_spider(self, spider):
        try:
            self.cursor.close()
            self.connection.close()
        except Exception, e:
            raise e

    def upsertIntoModules(self, item):
        """insert if new, if not, update"""
        self.cursor.execute(
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
            (self.school,
             item.get('year'),
             item.get('sem'),
             item.get('code'),
             item.get('title'),
             item.get('credit'),
             item.get('remarks'),
             item.get('department'),
             item.get('prerequisite'),
             item.get('preclusion'),
             item.get('availability'),
             item.get('description'),
             item.get('exam_time'),
             item.get('exam_venue'),
             item.get('exam_duration')
             )
        )

    def deleteFromLessons(self, item):
        self.cursor.execute(
            '''
            DELETE FROM lessons
            WHERE lessons.modules_id = (
            SELECT id from modules
            WHERE school = %s AND code = %s AND year = %s AND sem = %s);
            ''',
            (self.school, item.get('code'),
                item.get('year'), item.get('sem'))
        )

    def insertIntoLessons(self, item):
        timetable = item.get('timetable')

        if timetable is not None:
            for lesson in timetable:
                self.cursor.execute(
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
                    (self.school,
                     item.get('year'),
                     item.get('sem'),
                     item.get('code'),
                     lesson['class_no'],
                     lesson['day_text'],
                     lesson['lesson_type'],
                     lesson['week_text'],
                     lesson['start_time'],
                     lesson['end_time'],
                     lesson['venue']
                     )
                )


class NusDetailsPipeline(ModifyPipeline):
    school = 'NUS'

    def process_item(self, item, spider):
        """Save modules in the database.
        This method is called for every item pipeline component.
        """
        try:
            self.upsertIntoModules(item)

            # delete then insert new ones
            self.deleteFromLessons(item)
            self.insertIntoLessons(item)

            self.connection.commit()
        except Exception as e:
            print "Error: %s" % e
            self.connection.rollback()
            raise

        return item


class NtuDetailsPipeline(ModifyPipeline):
    """NtuDetailsPipeline pipeline for storing scraped items in the database"""
    school = 'NTU'

    def process_item(self, item, spider):
        """Save modules in the database.

        This method is called for every item pipeline component.

        """
        try:
            self.upsertIntoModules(item)
            self.connection.commit()
        except Exception as e:
            print "Error: %s" % e
            self.connection.rollback()
            raise

        return item


class NtuTimetablesPipeline(ModifyPipeline):
    school = 'NTU'

    def process_item(self, item, spider):
        """Save modules in the database.
        This method is called for every item pipeline component.
        """
        try:
            self.cursor.execute(
                '''
                UPDATE modules
                SET  remarks = CONCAT(%s, remarks)
                WHERE school = %s AND code = %s AND year = %s AND sem = %s;
                ''',
                (item.get('remark'), self.school, item.get('code'),
                    item.get('year'), item.get('sem'))
            )
            # delete then insert new ones
            self.deleteFromLessons(item)
            self.insertIntoLessons(item)
            # commit the change
            self.connection.commit()
        except Exception as e:
            print "Error: %s" % e
            self.connection.rollback()
            raise

        return item
