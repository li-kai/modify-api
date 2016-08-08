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


class NtuDetailsPipeline(ModifyPipeline):
    """NtuDetailsPipeline pipeline for storing scraped items in the database"""

    def process_item(self, item, spider):
        """Save modules in the database.

        This method is called for every item pipeline component.

        """
        try:
            self.cursor.execute(
                '''
                INSERT INTO ntu_modules (
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
                description
                ) values (
                %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s
                ) ON CONFLICT (code) DO UPDATE SET (
                year,
                sem,
                title,
                credit,
                remarks,
                department,
                prerequisite,
                preclusion,
                availability,
                description
                ) = (
                EXCLUDED.year,
                EXCLUDED.sem,
                EXCLUDED.title,
                EXCLUDED.credit,
                EXCLUDED.remarks,
                EXCLUDED.department,
                EXCLUDED.prerequisite,
                EXCLUDED.preclusion,
                EXCLUDED.availability,
                EXCLUDED.description
                );
                ''',
                (item.get('year'),
                 item.get('sem'),
                 item.get('code'),
                 item.get('title'),
                 item.get('credit'),
                 item.get('gradeType'),
                 item.get('department'),
                 item.get('prerequisite'),
                 item.get('preclusion'),
                 item.get('availability'),
                 item.get('description'),
                 )
            )
            self.connection.commit()
        except psycopg2.DatabaseError, e:
            print "Error: %s" % e
            self.connection.rollback()
            raise

        return item


class NtuTimetablesPipeline(ModifyPipeline):
    """NtuDetailsPipeline pipeline for storing scraped items in the database"""

    def process_item(self, item, spider):
        """Save modules in the database.
        This method is called for every item pipeline component.
        """
        try:
            self.cursor.execute(
                '''
                UPDATE ntu_modules
                SET  remarks = CONCAT(%s, remarks)
                WHERE code = %s AND year = %s AND sem = %s
                ''',
                (item.get('remark'), item.get('code'),
                    item.get('year'), item.get('sem'))
            )
            for lesson in item.get('timetable'):
                print lesson
            self.connection.commit()
        except psycopg2.DatabaseError, e:
            print "Error: %s" % e
            self.connection.rollback()
            raise

        return item
