import os
import json
from models import WorkCenter, RoutingSteps, ProductionOrder

#Locate JSON file directory
baseDirectory = os.path.dirname(os.path.abspath(__file__))
projectRoot = os.path.dirname(baseDirectory)
json_path = os.path.join(projectRoot,'json_files','graphics_card.json')

#Load JSON data
with open(json_path) as f:
    data = json.load(f)

work_centers = {}
gpu_RoutingSteps = []

#Create WorkCenter and RoutingSteps instances from JSON data
for workCenter in data ['work_centers']:
    wc = WorkCenter(workCenter['id'], workCenter['maxCapacity'], workCenter['operationType'])
    work_centers[workCenter['id']] = wc

for step in data['routing_steps']:
    wc = work_centers[step['workCenterId']]
    rs = RoutingSteps(step['stepNumber'], wc, step['operationTime'])
    gpu_RoutingSteps.append(rs)