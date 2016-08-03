# -*- coding: utf-8 -*-
import psycopg2
import settings.DATABASE as DATABASE
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
            conn = psycopg2.connect(
                database=DATABASE['database'],
                user=DATABASE['username'],
                password=DATABASE['password'],
            )
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS modify ("
                           "id serial PRIMARY KEY,"
                           "code text NOT NULL,"
                           "title text NOT NULL,"
                           "department text NOT NULL,"
                           "description text NOT NULL,"
                           "credit real NOT NULL,"
                           "prerequisite text,"
                           "preclusion text,"
                           "availability text,"
                           "gradeType text"
                           ");"
                           )

            self.Cursor = cursor
        except Exception, e:
            raise e

    def process_item(self, item, spider):
        """Save modules in the database.

        This method is called for every item pipeline component.

        """

        try:
            cursor = self.Cursor()
            cursor.execute("INSERT INTO modify ("
                           "code,"
                           "title,"
                           "credit,"
                           "gradeType,"
                           "department,"
                           "prerequisite,"
                           "preclusion,"
                           "availability,"
                           "description"
                           ") VALUES (%s, %s)"
                           "ON CONFLICT (key) DO UPDATE",
                           (100, "abc'def")
                           )
            cursor.commit()
        except:
            cursor.rollback()
            raise
        finally:
            cursor.close()

        return item
