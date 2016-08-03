hugeListUnprocessed = response.xpath(
    '//tr[position()>1 and position()<last()]'
)

x = [[]]
for item in hugeListUnprocessed:
    if item.extract() == u'<tr>\n<td>\xa0</td>\n</tr>':
        x.append([])
    else:
        x[-1].append(item)

for tr in x:
    # each tr is a module
    item = {}
    # first row contains code, title
    # credit and department
    firstRow = tr[0].xpath('.//font/text()').extract()
    item['code'] = firstRow[0]
    item['title'] = firstRow[1]
    item['credit'] = firstRow[2].strip()
    item['department'] = firstRow[3]
    prerequisites = []
    gradeType = []
    preclusion = []
    availability = []
    description = []
    import re
    for i in xrange(1, len(tr)):
        row = tr[i].xpath('.//font')
        for data in row:
            requirement = data.xpath('text()').extract()
            # empty string, skip
            if not requirement:
                continue
            data = data.extract()
            if ('#FF00FF' in data):
                prerequisites.extend(requirement)
            elif ('RED' in data):
                gradeType.extend(requirement)
            elif ('BROWN' in data):
                preclusion.extend(requirement)
            elif ('GREEN' in data):
                availability.extend(requirement)
            elif i == len(tr) - 1:
                print reduce(clean, requirement)
                for para in requirement:
                    para = re.sub(r'\?(?=[sS])|(?<=[sS])\?', '\'', para)
                    para = re.sub(r' \? ', ' - ', para)
                    description.append(
                        re.sub('\s +', ' ', para)
                        .replace('\t', ' ')
                        .strip()
                    )
    result = ''
    for item in description:
        if (item != ''):
            result += item
    #print result
    print ''