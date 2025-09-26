class WorkCenter:
    #ID = "WC01", "WC24", "WC07", "Drill" (Unique ID to easily identify the work center)
    #maxCapacity = 0, 50, 10 (The maximum units this work center can hold)
    #operationType = "Assembly","Packaging","Deployment","Quality Control" (What type of operation its performing)
    def __init__(self,id,maxCapacity,operationType):
        self.id = id
        self.maxCapacity = maxCapacity
        self.operationType = operationType
    def to_dict(self):
        return {
            "name": self.id,
            "maxCapacity": self.maxCapacity,
            "operationType": self.operationType
        }
class RoutingSteps: 
    #stepNumber = 1, 2, 5, 24 (Sequence Number of the step in routing)
    #workCenter = "WC01","WC05" (Reference to the work center object where this step is performed)
    #operationTime = 5, 2, 6, 10, 20(based on minutes required to complete the step)
    def __init__(self,stepNumber,workCenter,operationTime):
        self.stepNumber = stepNumber
        self.workCenter = workCenter
        self.operationTime = operationTime
    def to_dict(self):
        return {
            "stepNumber": self.stepNumber,
            "operationTime": self.operationTime,
            "workCenter": self.workCenter.to_dict() if hasattr(self.workCenter, 'to_dict') else str(self.workCenter)
        }
class ProductionOrder:
    #status = "Pending","In Progress","Completed","On Hold" (Current status of the production order)
    #productName = "productA","product24","Metal","Unobtainum","Paladium" (what product is being manufactured)
    #productAmount = 10, 20, 500 (how many of the products we talkin' here?)
    #routingSteps = 5 (A list of RoutingSteps objects that define the manufacturing process)
    def __init__(self,productName,productAmount,routingSteps,status):
        self.productName = productName
        self.productAmount = productAmount
        self.routingSteps = routingSteps
        self.status = status
    def compute_lead_time(self):
        if not isinstance(self.routingSteps, list):
            return 0

        leadTimePerUnit = 0
        for step in self.routingSteps:
            time = getattr(step, 'operationTime', 0)
            leadTimePerUnit += time
            print(f"Step {getattr(step, 'stepNumber', '?')}: {time} mins")

        totalLeadTime = leadTimePerUnit * self.productAmount
        print(f"Lead time per unit: {leadTimePerUnit} mins")
        print(f"Total lead time for {self.productAmount} units: {totalLeadTime} mins")
        return totalLeadTime
    def to_dict(self):
        return {
            "productName": self.productName,
            "productAmount": self.productAmount,
            "status": self.status,
            "routingSteps": [step.to_dict() for step in self.routingSteps]
        }