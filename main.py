#╔══ ❀•°❀°•❀ ══╗
#    LIBRARIES
#╚══ ❀•°❀°•❀ ══╝
import os
from time import sleep 
from flask import Flask, render_template, jsonify, url_for, request, redirect
import json
import webbrowser
import sys

from models import WorkCenter, RoutingSteps, ProductionOrder

#╔══ ❀•°❀°•❀ ══╗
#     COLORS
#╚══ ❀•°❀°•❀ ══╝

GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m' 

#╔══ ❀•°❀°•❀ ══╗
#   FLASK SETUP
#╚══ ❀•°❀°•❀ ══╝

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

# Directories
template_dir = os.path.join(base_path, 'templates')
static_dir = os.path.join(base_path, 'static')
orders_dir = os.path.join(base_path, 'json_files', 'orders.json')
routing_steps_dir = os.path.join(base_path, 'json_files', 'routing_steps.json')
workcenter_dir = os.path.join(base_path, 'json_files', 'work_centers.json')
#Application
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

#Production Orders and Dashboard
@app.route('/')
def dashboard():
    metrics = {
        "defective_units": 3,
        "yield_rate": 97.5
    }

    # Load production orders
    try:
        with open(orders_dir) as f:
            raw_orders = json.load(f)
    except Exception as e:
        print(f"Error loading orders: {e}")
        raw_orders = []

    # Load routing steps
    try:
        with open(routing_steps_dir) as f:
            all_steps = json.load(f)
    except Exception as e:
        print(f"Error loading routing steps: {e}")
        all_steps = []

    # Load work centers
    try:
        with open(workcenter_dir) as f:
            work_centers = json.load(f)
    except Exception as e:
        print(f"Error loading work centers: {e}")
        work_centers = []

    # Enrich orders with detailed routing steps and total time
    dynamic_orders = []
    for o in raw_orders:
        detailed_steps = []

        for step_name in o.get('routingSteps', []):
            match = next((s for s in all_steps if s['stepNumber'] == step_name), None)
            if match:
                wc_match = next((wc for wc in work_centers if wc['id'] == match['workCenterID']), None)
                match['workCenterName'] = wc_match['name'] if wc_match else "Unknown"
                detailed_steps.append(match)

        total_seconds = 0

        for s in detailed_steps:
            time = float(s.get('operationTime', 0))
            unit = s.get('operationUnit', '').lower()

            if unit in ['second', 'seconds']:
                total_seconds += time
            elif unit in ['minute', 'minutes']:
                total_seconds += time * 60
            elif unit in ['hour', 'hours']:
                total_seconds += time * 3600
            else:
                print(f"⚠️ Unknown unit: {unit}")

        # Convert total_seconds to hours, minutes, seconds
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)

        # Format as a readable string
        formatted_time = f"{hours}h {minutes}m {seconds}s"


        order = {
            "product": o['product'],
            "amount": o['amount'],
            "status": o['status'],
            "routingSteps": detailed_steps,
            "totalTime": formatted_time
        }

        dynamic_orders.append(order)

    return render_template('production_orders.html', orders=dynamic_orders, data=metrics, routing_steps = all_steps)



#Routing Steps
@app.route('/create-routing')
def create_routing():
    try:
        with open(routing_steps_dir) as f:
            steps = json.load(f)
    except:
        steps = []

    try:
        with open(workcenter_dir) as f:
            centers = json.load(f)
    except:
        centers = []

            
    return render_template('create_routing.html', steps=steps, centers=centers)


#Work Centers
@app.route('/create-workcenter')
def create_workcenter():
    try:
        with open(workcenter_dir) as f:
            centers = json.load(f)
    except:
        centers = []

    return render_template('create_workcenter.html', centers=centers)

#######################################################

#Production Order Submission
@app.route('/submit-order', methods=['POST'])
def submit_order():
    product = request.form['productName']
    amount = int(request.form['amount'])
    status = request.form['status']
    selected_steps = request.form.getlist("routingSteps")  # ✅


    new_order = {
        "product": product,
        "amount": amount,
        "status": status,
        "routingSteps": selected_steps
    }

    # Append to JSON file or database
    with open(orders_dir, 'r+') as f:
        data = json.load(f)
        data.append(new_order)
        f.seek(0)
        json.dump(data, f, indent=2)

    # Print to console
    print(linebreakStart)
    print(f"{GREEN}[Production Order Created]{RESET}")
    print(f"Product Name: {product}")
    print(f"Amount: {amount}")
    print(f"Status: {status}")
    print(linebreak)
    print(f"Routing Steps: {selected_steps}")
    print(linebreakEnd)

    return redirect('/')


#Production Order Removal
@app.route('/remove-orders', methods=['POST'])
def remove_orders():
    orders_path = os.path.join(os.path.dirname(__file__), 'json_files', 'orders.json')

    try:
        with open(orders_path, 'r+') as f:
            data = json.load(f)
            remove_ids = request.form.getlist('remove_ids')
            remove_ids = [int(i) for i in remove_ids]

            removed_orders = [data[idx] for idx in remove_ids]
            updated_orders = [order for idx, order in enumerate(data) if idx not in remove_ids]

            f.seek(0)
            f.truncate()
            json.dump(updated_orders, f, indent=2)

        print(linebreakStart)
        print(f"{RED}[Production Orders Removed]{RESET}")
        for order in removed_orders:
            print(linebreak)
            print(f"Product: {order['product']} x {order['amount']}")
            print(f"Status: {order['status']}")
            print(f"Routing Steps: {order.get('routingSteps', [])}")
            print(linebreak)
        print(linebreakEnd)
 
    except Exception as e:
        print(f"Error removing orders: {e}")

    return redirect('/')

#Routing Steps Submission
@app.route('/submit-routing', methods=['POST'])
def submit_routing():
    new_step = {
        "stepNumber": request.form['stepNumber'],
        "operationTime": request.form['operationTime'],
        "operationUnit": request.form['operationUnit'],
        "workCenterID": request.form['workCenterID']
    }
    try:
        with open(workcenter_dir) as f:
            centers = json.load(f)
            match = next((c for c in centers if c['id'] == new_step['workCenterID']), None)
            new_step['workCenterName'] = match['name'] if match else "Unknown"
    except Exception as e:
        print(f"Error enriching work center name: {e}")
        new_step['workCenterName'] = "Unknown"

    try:
        if os.path.exists(routing_steps_dir):
            with open(routing_steps_dir, 'r') as f:
                data = json.load(f)
        else:
            data = []

        data.append(new_step)

        with open(routing_steps_dir, 'w') as f:
            json.dump(data, f, indent=2)

        print(linebreakStart)
        print(f"{GREEN}[Routing Step Created]{RESET}")
        print(f"Step Number: {new_step['stepNumber']}")
        print(f"Operation Time: {new_step['operationTime']} {new_step['operationUnit']}")
        print(f"Work Center ID: {new_step['workCenterID']}")
        print(f"Work Center Name: {new_step['workCenterName']}")
        print(linebreakEnd)

    except Exception as e:
        print(f"Error saving routing step: {e}")

    return redirect('/create-routing')




#Routing Steps Removal
@app.route('/remove-routing', methods=['POST'])
def remove_routing():
    try:
        with open(routing_steps_dir, 'r+') as f:
            data = json.load(f)
            remove_ids = request.form.getlist('remove_routing_ids')
            remove_ids = [int(i) for i in remove_ids]

            removed_steps = [data[idx] for idx in remove_ids]
            updated_steps = [step for idx, step in enumerate(data) if idx not in remove_ids]

            f.seek(0)
            f.truncate()
            json.dump(updated_steps, f, indent=2)

        print(linebreakStart)
        print(f"{RED}[Routing Steps Removed]{RESET}")
        for step in removed_steps:
            print(f"Step Number: {step['stepNumber']}")
            print(f"Operation Time: {step['operationTime']} {step['operationUnit']}")
            print(f"Work Center ID: {step['workCenterID']}")
            print(linebreak)
        print(linebreakEnd)
    
    
    except Exception as e:
        print(f"Error removing routing steps: {e}")

    return redirect('/create-routing')

#Work Center Submissions
@app.route('/submit-workcenter', methods=['POST'])
def submit_workcenter():
    new_center = {
        "id": request.form['centerId'],
        "name": request.form['centerName'],
        "operationType": request.form['operationType'],
        "maxCapacity": int(request.form['maxCapacity'])
    }

    try:
        if os.path.exists(workcenter_dir):
            with open(workcenter_dir, 'r') as f:
                data = json.load(f)
        else:
            data = []

        data.append(new_center)

        with open(workcenter_dir, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"{GREEN}[Work Center Created]{RESET} → {new_center['id']} ({new_center['name']})")

    except Exception as e:
        print(f"Error saving work center: {e}")

    print(linebreakStart)
    print(f"{GREEN}[Work Center Created]{RESET}")
    print(f"ID: {new_center['id']}")
    print(f"Name: {new_center['name']}")
    print(f"Operation Type: {new_center['operationType']}")
    print(f"Max Capacity: {new_center['maxCapacity']}")
    print(linebreakEnd)

    return redirect('/create-workcenter')

#Work Center Removal
@app.route('/remove-workcenters', methods=['POST'])
def remove_workcenters():
    try:
        with open(workcenter_dir, 'r+') as f:
            data = json.load(f)
            remove_ids = request.form.getlist('remove_center_ids')
            remove_ids = [int(i) for i in remove_ids]

            updated_centers = [center for idx, center in enumerate(data) if idx not in remove_ids]

            f.seek(0)
            f.truncate()
            json.dump(updated_centers, f, indent=2)

            removed_centers = [data[idx] for idx in remove_ids]
            updated_centers = [center for idx, center in enumerate(data) if idx not in remove_ids]
            
            print(linebreakStart)
            print(f"{RED}[Work Centers Removed]{RESET}")
            for center in removed_centers:
                print(linebreak)
                print(f"ID & Name: {center['id']} — {center['name']}")
                print(linebreak)
            print(linebreakEnd)

    except Exception as e:
        print(f"Error removing work centers: {e}")

    return redirect('/create-workcenter')

#╔══ ❀•°❀°•❀ ══╗
#    FUNCTIONS
#╚══ ❀•°❀°•❀ ══╝
def clearTerminal():
    if os.name == 'nt':
        os.system('cls')#Windows
    else:
        os.system('clear')#macOS/Linux

# UNUSED FOR NOW #
'''
def calculate_cost(order, cost_per_minute=1.5):
    if not isinstance(order.routingSteps, list):
        return 0

    total_minutes = sum(getattr(step, 'operationTime', 0) for step in order.routingSteps)
    total_time = total_minutes * order.productAmount
    total_cost = total_time * cost_per_minute

    print(f"[Cost Simulation] {order.productName} x{order.productAmount}")
    print(f"    >Product Amount: {order.productName} x{order.productAmount}")
    print(f"    >Total Time: {total_time} mins")
    print(f"    >Cost per Minute: ${cost_per_minute}")
    print(f"    >Estimated Cost: ${total_cost:.2f}")
    return total_cost
'''

#Linebreak
linebreak = "=============================="
linebreakStart = "╭── ⋅ ⋅ ──  ── ⋅ ⋅ ──╮"
linebreakEnd = "╰── ⋅ ⋅ ──  ── ⋅ ⋅ ──╯"

#╔══ ❀•°❀°•❀ ══╗
#PRODUCTION ORDERS
#╚══ ❀•°❀°•❀ ══╝ 

productionOrderList = []
json_output = json.dumps(productionOrderList, default=lambda o: o.to_dict(), indent=4)



#Clear Terminal from previous instances
clearTerminal()

#╔══ ❀•°❀°•❀ ══╗
#     OUTPUT
#╚══ ❀•°❀°•❀ ══╝
print("""
[Ｐｒｏｊｅｃｔ]
   __               ______                 
  / /  ___ ___ ____/ / __/__  _______ ____ 
 / /__/ -_) _ `/ _  / _// _ \/ __/ _ `/ -_)
/____/\__/\_,_/\_,_/_/  \___/_/  \_, /\__/ 
                                /___/     

        [version 0.7.1]          
""")
sleep(1)

#╔══ ❀•°❀°•❀ ══╗
#    DEBUGGING
#╚══ ❀•°❀°•❀ ══╝
print(f"{GREEN}【ｄｅｂｕｇ】:\n")


app.config['EXPLAIN_TEMPLATE_LOADING'] = True
print("template FOLDER DIRECTORY: \n", template_dir)
print("static FOLDER DIRECTORY: \n", static_dir)
print("orders.json DIRECTORY:\n",orders_dir)
print("\n")
print("RUN THIS APP VIA YOUR BROWSER: http://127.0.0.1:5000/")
print("CTRL+C TO STOP THE SERVER!")
print(RESET)

if __name__ == '__main__':
    url = "http://127.0.0.1:5000/"
    webbrowser.open_new_tab(url)
    app.run(debug=False, use_reloader = False)