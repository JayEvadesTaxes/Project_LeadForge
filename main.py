#╔══ ❀•°❀°•❀ ══╗
#    LIBRARIES
#╚══ ❀•°❀°•❀ ══╝
import os
from time import sleep 
from flask import Flask, render_template, jsonify, url_for, request, redirect
import json

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
template_dir = os.path.join(os.path.dirname(__file__),'templates')
static_dir = os.path.join(os.path.dirname(__file__),'static')
orders_dir = os.path.join(os.path.dirname(__file__), 'json_files', 'orders.json')
routing_steps_dir = os.path.join(os.path.dirname(__file__), 'json_files', 'routing_steps.json')
workcenter_dir = os.path.join(os.path.dirname(__file__), 'json_files', 'work_centers.json')
#Application
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)


#Dashboard and Production Orders
@app.route('/dashboard')
def dashboard():
    metrics = {
        "defective_units": 3,
        "yield_rate": 97.5
    }

    try:
        with open(orders_dir) as f:
            raw_orders = json.load(f)
            dynamic_orders = []

            for o in raw_orders:
                # Reconstruct RoutingSteps objects from step names
                routing_steps = []
                for step_name in o.get('routing_steps', []):
                    routing_steps.append(RoutingSteps(step_name))  # or use a lookup if needed

                order = ProductionOrder(
                    o['product'],
                    o['amount'],
                    o['status'],
                    o.get('routing_steps', [])
                )
                dynamic_orders.append(order)

    except Exception as e:
        print(f"Error loading orders: {e}")
        dynamic_orders = productionOrderList

    return render_template('production_orders.html', orders=dynamic_orders, data=metrics)

#Production Orders Index
@app.route('/')
def index():
    try:
        with open(orders_dir) as f:
            orders = json.load(f)
    except:
        orders = []

    try:
        with open(routing_steps_dir) as f:
            routing_steps = json.load(f)
    except:
        routing_steps = []

    print("Loaded orders:", orders)

    return render_template('production_orders.html', orders=orders, routing_steps=routing_steps)


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

    # Print to console
    print(linebreakStart)
    print(f"{GREEN}[Production Order Created]{RESET}")
    print(f"Product Name: {product}")
    print(f"Amount: {amount}")
    print(f"Status: {status}")
    print(linebreak)
    print(f"Routing Steps: {selected_steps}")
    print(linebreakEnd)

    # Append to JSON file or database
    with open(orders_dir, 'r+') as f:
        data = json.load(f)
        data.append(new_order)
        f.seek(0)
        json.dump(data, f, indent=2)

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

            updated_orders = [order for idx, order in enumerate(data) if idx not in remove_ids]

            f.seek(0)
            f.truncate()
            json.dump(updated_orders, f, indent=2)

        print(linebreakStart)
        print(f"{RED}[Production Orders Removed]{RESET}")
        print(f"Removed IDs: {remove_ids}")
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
        if os.path.exists(routing_steps_dir):
            with open(routing_steps_dir, 'r') as f:
                data = json.load(f)
        else:
            data = []

        data.append(new_step)

        with open(routing_steps_dir, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"{GREEN}[Routing Step Created]{RESET} → {new_step['stepNumber']}")

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

            updated_steps = [step for idx, step in enumerate(data) if idx not in remove_ids]

            f.seek(0)
            f.truncate()
            json.dump(updated_steps, f, indent=2)

        print(f"{GREEN}[Routing Steps Removed]{RESET} → {remove_ids}")

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

        print(f"{GREEN}[Work Centers Removed]{RESET} → {remove_ids}")

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

        [version 0.6.2]          
""")
sleep(1)
for order in productionOrderList:
    print("Product Name:", order.productName)
    print("Amount of Products:", order.productAmount,"\n")

    print(linebreakStart)
    print("Lead Time Estimation:",order.compute_lead_time(),"minutes")
    print(linebreakEnd,"\n")
    
    print("[Cost Estimation] $", calculate_cost(order)) 
    print(linebreak,"\n")

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
    app.run(debug=True)