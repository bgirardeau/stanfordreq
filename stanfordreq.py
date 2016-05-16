"""
Extracts requirements data from Stanford course descriptions.

Script usage:

  python stanfordreq.py [-h] [explorecourses] [reqs]

  positional arguments:
    explorecourses  Explorecourses data, one JSON document per class per line
                  (default stdin)
    reqs            Requirements output data, one JSON document per class per
                  line (default stdout)

  optional arguments:
    -h, --help      show this help message and exit

Functions:

  parse_all(courses, filter_codes=True, add_postreq=True)
  parse_course(description, code=None, valid_codes=None)
  extract_courses(datastr, department="")

"""
import argparse
import json
import re
import sys


def parse_all(courses, filter_codes=True, add_postreq=True):
    """
    Parses a set of courses for requirements.

    Arguments:
      courses: list of dictionaries for each class, with required fields
               'code' and 'description'
      filter_codes: flag (default True) indicating whether to filter out
                    course requirements that don't exist in the courses array
      add_postreq: flag (default True) indicating whether to add in postreqs
    Output:
      list of dictionaries for each class with fields 'code', 'description',
      'prereq', 'coreq' 'recommend', and 'postreq' (if add_postreq is True)
    """
    if filter_codes:
        codes = set()
        for course in courses:
            codes.add(course['code'])
    else:
        codes = None
    data = []
    indices = {}
    for i, course in enumerate(courses):
        reqs = parse_course(course['description'], course['code'], codes)
        if add_postreq:
            reqs['postreq'] = []
            indices[course['code']] = i
        data.append(reqs)
    if add_postreq:
        for course in data:
            for prereq in course['prereq']:
                if prereq not in indices:
                    continue
                data[indices[prereq]]['postreq'].append(course['code'])
    return data


def parse_course(description, code=None, valid_codes=None):
    """
    Parses a course description for requirements.
    """
    # regular expression: get everything from a marker (inclusive) to next
    # marker or end of string/sentence (exclusive)
    # ([marker](?:.(?![other markers]|$))*.)
    markers = ["Prerequisite", "Pre-[^:]*corequisite", "Corequisite",
               "Recommended"]
    fields = ["prereq", "coreq", "coreq", "recommend"]
    regexs = ["(%s(?:.(?!%s|$|\. ))*.)" % (item, "|".join(
                marker for i, marker in enumerate(markers) if i != index))
              for index, item in enumerate(markers)]
    searches = list(zip(fields, regexs))

    data = {}
    description = description.replace('\n', ' ').replace('\r', '')

    if code is not None:
        department = code.partition(' ')[0]
        data['code'] = code
    else:
        department = ""

    for field, regex in searches:
        if field not in data:
            data[field] = []
        match = re.search(regex, description)
        if match is not None:
            courses = [cl for cl in extract_courses(match.group(), department)
                       if cl != code]
            if valid_codes is not None:
                courses = [cl for cl in courses if cl in valid_codes]
            data[field].extend(courses)

    return data


def extract_courses(datastr, department=""):
    """
    Extracts all candidate courses in a string.
    """
    rdepartment = re.compile("([A-Z]+)(?:\s*)(?=\d)")
    rcourse_number = re.compile("(\d\d?\d?)([A-Z])?")
    rlist_separator = re.compile("(?:,?\s*(?:or|and)?\s*)")
    rfollow_on_let = re.compile("(?:/|(?:\s+or\s+))([A-Z])(?=\s|,|$)")

    all_courses = []

    current_department = department
    last_position = 0
    # keeps looking for classes until end of string
    while True:
        # find next department and record its position
        department_group = rdepartment.search(datastr, last_position)
        if department_group is not None and department_group.group(1):
            next_department = department_group.group(1)
            dept_position = department_group.end()
        else:
            dept_position = -1

        # look for a course number
        course_number_group = rcourse_number.search(datastr, last_position)
        # if there are no more course numbers, return
        if course_number_group is None or not course_number_group.group(1):
            return all_courses

        # figure out whether this course number is still associated with current department
        if course_number_group.start() != last_position:
            if course_number_group.start() > dept_position:
                current_department = department
            if course_number_group.start() == dept_position:
                current_department = next_department

        last_position = course_number_group.end()

        # find follow on letters for the course (ex: 'CS 106A or B')
        number = course_number_group.group(1)
        letters = [course_number_group.group(2)]
        if letters[0] is None:
            letters[0] = ""
        follow_on_group = rfollow_on_let.match(datastr, last_position)
        if follow_on_group is not None and follow_on_group.group(1):
            letters.append(follow_on_group.group(1))
            last_position = follow_on_group.end()

        courses = [number + letter for letter in letters]
        full = [current_department + " " + course for course in courses]
        all_courses.extend(full)

        # move position past the next list separator before looking for next course
        last_position = rlist_separator.match(datastr, last_position).end()


if __name__ in '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('explorecourses', nargs='?', type=argparse.FileType('r'), default='-',
                        help='Explorecourses data, one JSON document per class per line (default stdin)')
    parser.add_argument('reqs', nargs='?', type=argparse.FileType('w'), default='-',
                        help='Requirements output data, one JSON document per class per line (default stdout)')
    args = parser.parse_args()

    courses = []
    for line in args.explorecourses:
        courses.append(json.loads(line))

    prereqs = parse_all(courses)
    for prereq in prereqs:
        args.prereqs.write(json.dumps(prereq) + '\n')
