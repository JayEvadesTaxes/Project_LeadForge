#╔══ ❀•°❀°•❀ ══╗
#    LIBRARIES
#╚══ ❀•°❀°•❀ ══╝
import os
from time import sleep 
from tqdm import tqdm
from flask import Flask, render_template, jsonify, url_for
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

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)



@app.route('/')
def dashboard():
    metrics = {
        "defective_units": 3,
        "yield_rate": 97.5
    }
    return render_template('dashboard.html', orders=productionOrderList, data=metrics)

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

order1 = ProductionOrder("Silicon Wafer",10,siliconWafer_RoutingSteps,"Discarded")
order2 = ProductionOrder("GPU (Graphics Processing Unit)",11,gpu_RoutingSteps,"Delayed")
order3 = ProductionOrder("Silicon Wafer",1,siliconWafer_RoutingSteps, "NIE")
order4 = ProductionOrder("Silicon Wafer",3,siliconWafer_RoutingSteps,"Active")
order5 = ProductionOrder("GPU (Graphics Processing Unit)",11,gpu_RoutingSteps,"On Hold")
order6 = ProductionOrder("GPU (Graphics Processing Unit)",5,gpu_RoutingSteps,"Closed")

productionOrderList = [order1,order2,order3,order4,order5,order6]
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

        [version 0.5.1]          
""")
print(linebreak)
sleep(1)
for i in tqdm(productionOrderList, desc = "Processing Production Orders"):
    sleep(0.1)
sleep(0.5)
print(linebreak)
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
print("TEMPLATE FOLDER DIRECTORY: \n", template_dir)
print("STATIC FOLDER DIRECTORY: \n", static_dir)
print("RUN THIS APP VIA YOUR BROWSER: http://127.0.0.1:5000/")
print("CTRL+C TO STOP THE SERVER!")
print(RESET)

if __name__ == '__main__':
    app.run(debug=True)