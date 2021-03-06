# Modify-api
RESTful API for Modify.sg

  - Normalizes data from NUS and NTU (Huge thanks to [NUSMods-API])
  - Provides a RESTful API to get information
  - Simple

### Usage
#### GET modulesList/&lt;School&gt;/&lt;AcadYear&gt;/&lt;Semester&gt;/

http://api.modify.sg/modulesList/nus/2016/1/

```
[
    "code": "ACC1002",
    "title": "Financial Accounting"
  },
  {
    "code": "ACC1006",
    "title": "Accounting Information Systems"
  },
  ...
]
```

#### GET modules/&lt;School&gt;/&lt;AcadYear&gt;/&lt;Semester&gt;/&lt;ModuleCode&gt;

https://api.modify.sg/modules/ntu/2016/1/AAA18C

```
{
    "code": "AAA18C",
    "department": "NIE",
    "credit": 3,
    "title": "Introduction to Contemporary Sculpture Practice",
    "description": "A study of the skills and knowledge ...",
    "exam_time": null,
    "exam_venue": null,
    "exam_duration": null,
    "prerequisite": "Only opened to NBS students.",
    "preclusion": "AB0301, AB0401, AB0402, AB0501, AB0502, AB0603",
    "availability": "Not available to Programme: ACBS(GA) 1 ...",
    "remarks": "Course is available as ...",
    "timetable": [
        {
            "class_no":"S1",
            "day_text":"MON",
            "lesson_type":"SEM",
            "week_text":"Every week",
            "venue":"LHS-TR+53",
            "start_time":"18:00:00",
            "end_time":"21:00:00"
        }, ...
    ]
}
```

### Tech
Server is a nodejs application hosted on a DigitalOcean droplet.
* [node.js] - back-end server language
* [Express] - node.js network app framework
* [Nginx] - reverse proxy
* [Scrapy] - spider for scraping info
* [PostgreSQL] - database


### Running the spiders
Download and install [Scrapy](http://doc.scrapy.org/en/latest/intro/install.html) and [PostgreSQL](https://wiki.postgresql.org/wiki/Detailed_installation_guides), then, clone this repository.
```sh
git clone https://github.com/li-kai/modify-api.git
cd modify-api/scrapy
```
Set up the postgreSQL user *scrapy* as well as initialize the database with the schema in *db.sql*. Fill up user details in *queries.js* and *settings.py*. Then, run the spiders with the following terminal commands:
```sh
# for nus
scrapy crawl nus_details

# for ntu (note the order)
scrapy crawl ntu_details
scrapy crawl ntu_timetables
python exams.py
```

### Running your own server
Download and install [Node.js](https://docs.npmjs.com/getting-started/installing-node) v4+ to run, then run the following in the terminal:
```sh
git clone https://github.com/li-kai/modify-api.git
cd modify-api
# install dependencies
npm install
# serve at localhost:3000
npm start
```

### Development
The API is still unfinished. Especially with regards to the schema of the database.
Any help is welcomed!


License
----

MIT


[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)


   [NUSMods-API]: <https://github.com/nusmodifications/nusmods-api>
   [node.js]: <http://nodejs.org>
   [Nginx]: <https://www.nginx.com/>
   [Scrapy]: <http://scrapy.org/>
   [PostgreSQL]: <https://www.postgresql.org/>
   [express]: <http://expressjs.com>
