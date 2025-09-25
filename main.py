#╔══ ❀•°❀°•❀ ══╗
#    LIBRARIES
#╚══ ❀•°❀°•❀ ══╝
import os
from time import sleep 
from flask import Flask, render_template, jsonify, url_for, request, redirect
import json

from ManufacturingData.silicon_wafer_data import siliconWafer_RoutingSteps
from ManufacturingData.graphics_card_data import gpu_RoutingSteps
from models import WorkCenter, RoutingSteps, ProductionOrder

#╔══ ❀•°❀°•❀ ══╗
#     COLORS
#╚══ ❀•°❀°•❀ ══╝
GREEN = '\033[92m'
RESET = '\033[0m' 
#╔══ ❀•°❀°•❀ ══╗
#   FLASK SETUP
#╚══ ❀•°❀°•❀ ══╝
template_dir = os.path.join(os.path.dirname(__file__),'templates')
static_dir = os.path.join(os.path.dirname(__file__),'static')
orders_dir = os.path.join(os.path.dirname(__file__), 'json_files', 'orders.json')

#Application
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)


#Open Dashboard
@app.route('/')
def dashboard():
    metrics = {
        "defective_units": 3,
        "yield_rate": 97.5
    }

    try:
        with open(orders_dir) as f:
            raw_orders = json.load(f)
            dynamic_orders = [
                ProductionOrder(
                    o['product'],
                    o['amount'],
                    siliconWafer_RoutingSteps if "Silicon Wafer" in o['product'] else gpu_RoutingSteps,
                    o['status']
                ) for o in raw_orders
            ]
    except Exception as e:
        print(f"Error loading orders: {e}")
        dynamic_orders = productionOrderList  # fallback

    return render_template('production_orders.html', orders=dynamic_orders, data=metrics)


#Submission requests
@app.route('/submit-order', methods=['POST'])
def submit_order():
    product = request.form['product']
    amount = int(request.form['amount'])
    status = request.form['status']

    new_order = {
        "product": product,
        "amount": amount,
        "status": status
    }

    # Print to console
    print(linebreakStart)
    print(f"{GREEN}[New Production Order Created]{RESET}")
    print(f"Product Name: {product}")
    print(f"Amount: {amount}")
    print(f"Status: {status}")
    print(linebreakEnd)

    # Append to JSON file or database
    with open(orders_dir, 'r+') as f:
        data = json.load(f)
        data.append(new_order)
        f.seek(0)
        json.dump(data, f, indent=2)

    return redirect('/')


#Removal requests
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

    except Exception as e:
        print(f"Error removing orders: {e}")

    return redirect('/')

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

        [version 0.6]          
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


print(siliconWafer_RoutingSteps,"\n")
print(gpu_RoutingSteps,"\n")

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