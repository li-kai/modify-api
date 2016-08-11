SELECT modules.code, modules.department, modules.credit, modules.title,
	modules.description, modules.exam_time, modules.exam_venue,
	modules.exam_duration, modules.prerequisite, modules.preclusion,
	modules.availability, modules.remarks,
(
	SELECT array_agg(row_to_json(t))
	FROM (
		SELECT lessons.class_no, lessons.day_text, lessons.lesson_type,
		lessons.week_text, lessons.venue, lessons.start_time, lessons.end_time
		FROM lessons
		WHERE lessons.modules_id = modules.id
	) t
) AS timetable
FROM modules
WHERE modules.school = ${school} AND 
modules.year = ${year} AND modules.sem = ${sem} AND modules.code = ${code}