import hashlib
import re
import pandas
import pm4py
import random

# The log as reported in the "Events" menu on EasyChair
log = """
2023-01-01  10:00 review by Person1 on paper 1 Person1
2023-01-02  10:05 comment on paper 2 Person2
2023-01-03  10:10 review by Person3 on paper 3  Person3
2023-01-04  10:15 comment on paper 4 Person4
2023-01-05  10:20 review by Person5 on paper 5 Person5
2023-01-06  10:25 review by Person6 on paper 6 Person6
2023-01-07  10:30 review by Person7 on paper 7  Person7
2023-01-08  10:35 Decision REJECT on paper 8 Person8
2023-01-09  10:40 Decision REJECT on paper 9 Person9
2023-01-10  10:45 Decision ACCEPT on paper 10 Perso10
"""

def hash(str):
  ho = hashlib.sha256(str.encode())
  return ho.hexdigest()


def processString(str, pattern, dest):
  match = re.search(pattern, str)
  if match is not None:
    return {'activity': dest , 'case-id': hash(match.group(1))}
  return None


def processActivity(str):
  ls = [
      ("submission of paper (\d+)", "paper submission"),
      ("file upload for submission (\d+) \(paper\)", "paper uploaded"),
      ("review by [\w \. \-]+ on paper (\d+)", "review"),
      ("submission (\d+) withdrawn", "withdraw"),
      ("submission (\d+) deleted", "deleted"),
      ("file deleted for submission (\d+) \(paper\)", "file deleted"),
      ("review by [\w \. \-]+ \(for [\w \. \-]+\) on paper (\d+)", "review"),
      ("comment on paper (\d+)", "comment"),
      ("Decision REJECT on paper (\d+)", "decision rejected"),
      # ("Decision accept\? on paper (\d+)", "paper probably accepted"),
      # ("Decision reject\? on paper (\d+)", "paper probably rejected"),
      ("Decision ACCEPT on paper (\d+)", "decision accepted"),
      ("Decision conditional accept on paper (\d+)", "decision conditionally accepted"),
      ("reviews sent to authors of (\d+) submissions", "reviews sent"),
      ("notification sent to authors of (\d+) submissions", "notification sent"),

  ]

  for l in ls:
    if processString(str, l[0], l[1]) is not None:
      return processString(str, l[0], l[1])

  return {}



# Process the CSV file
rows_list = []
for line in log.split("\n"):
  row = line.split("\t")
  dic = processActivity(row[2])
  dic.update({'time':row[0] + " " + row[1], 'resource':hash(row[3])})
  rows_list.append(dic)

# Identify the result for each paper
case_ids = {}
for obj in rows_list:
  if ("case-id" in obj):
    if (obj["activity"] == "decision accepted" and obj["case-id"] not in case_ids):
      case_ids[obj["case-id"]] = "paper accepted"
    if (obj["activity"] == "decision rejected" and obj["case-id"] not in case_ids):
      case_ids[obj["case-id"]] = "paper rejected"
    if (obj["activity"] == "decision conditionally accepted"):
      case_ids[obj["case-id"]] = "paper conditionally accepted"

# Add response activity
for case_id in case_ids:
  rows_list.append({'time': '2022-08-03 23:59', 'case-id':case_id, 'resource':'chairs', 'activity': case_ids[case_id]})


# Construct the actual event log object
dataframe = pandas.DataFrame(rows_list)
dataframe = pm4py.format_dataframe(dataframe, case_id='case-id', activity_key='activity', timestamp_key='time')
event_log = pm4py.convert_to_event_log(dataframe)


# Add review counter
for trace in event_log:
  counter = ['1', '2', '3']
  random.shuffle(counter)
  for event in trace:
    if (event['concept:name'] == "review"):
      if (len(counter) == 0):
        event['concept:name'] = "review extra"
      else:
        event['concept:name'] = "review " + counter.pop()

# Export the log to an XES file
pm4py.write_xes(event_log, 'exported.xes')