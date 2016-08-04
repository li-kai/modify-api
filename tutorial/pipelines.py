# -*- coding: utf-8 -*-
import psycopg2
from settings import DATABASE
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class ModulesPipeline(object):
    """Livingsocial pipeline for storing scraped items in the database"""

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

    def process_item(self, item, spider):
        """Save modules in the database.

        This method is called for every item pipeline component.

        """
        try:
            self.cursor.execute(
                '''
                INSERT INTO ntu (
                code,
                title,
                credit,
                gradeType,
                department,
                prerequisite,
                preclusion,
                availability,
                description
                ) values (
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s
                ) ON CONFLICT (code) DO UPDATE SET (
                title,
                credit,
                gradeType,
                department,
                prerequisite,
                preclusion,
                availability,
                description
                ) = (
                EXCLUDED.title,
                EXCLUDED.credit,
                EXCLUDED.gradeType,
                EXCLUDED.department,
                EXCLUDED.prerequisite,
                EXCLUDED.preclusion,
                EXCLUDED.availability,
                EXCLUDED.description
                );
                ''',
                (item.get('code'),
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

    def close_spider(self, spider):
        try:
            self.cursor.close()
            self.connection.close()
        except Exception, e:
            raise e
