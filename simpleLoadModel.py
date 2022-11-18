
import numpy as np


def roomSimpleLoad(floorArea,
                   Uw,
                   Uroof,
                   Uground,
                   vSystem,
                   v50=6,
                   Tin=20,
                   Tout=-7,
                   neighbourT=18,
                   Un=1.0,
                   LIR=0.2,
                   heatLossAreaEstimation='fromFloorArea',
                   ventilationCalculationMethod='simple',
                   exposedPerimeter=0,
                   onGround=False,
                   underRoof=False,
                   addNeighbourLosses=False,
                   neighbourPerimeter=0,
                   roomType = None,
                   wallHeight=2.7,
                   returnDetail=False):


    deltaT=Tin-Tout
    
    

    wallHeatLossArea,neighbourWallArea,groundHeatLossArea,roofHeatLossArea,neighbourFloorArea = computeHeatLossAreas(floorArea, heatLossAreaEstimation, onGround, underRoof, exposedPerimeter, neighbourPerimeter)


    if addNeighbourLosses:
        
        neighbourLosses = Un*(Tin-neighbourT)*(neighbourWallArea+neighbourFloorArea)

    else:
        neighbourLosses=0


    insideDeltaT = max(0,Tin-neighbourT)

    outsideAirVentilationFlowRate,insideAirVentilationFlowRate = getVentilationFlows(vSystem,floorArea,wallHeight,ventilationCalculationMethod,roomType=roomType)    


    ventilationHeatLoss  = 0.34*(outsideAirVentilationFlowRate)*deltaT + 0.34*(insideAirVentilationFlowRate)*insideDeltaT

    infiltrationHeatLoss = 0.34*LIR*v50*(wallHeatLossArea + roofHeatLossArea + groundHeatLossArea)*deltaT 
    transmissionHeatLoss = (wallHeatLossArea*Uw + roofHeatLossArea*Uroof + groundHeatLossArea*Uground)*deltaT

    
    totalHeatLoss = transmissionHeatLoss + ventilationHeatLoss + infiltrationHeatLoss + neighbourLosses

    returnDict = {}
    
    returnDict['totalHeatLoss'] = totalHeatLoss
    returnDict['transmissionHeatLoss']=transmissionHeatLoss
    returnDict['ventilationHeatLoss']=ventilationHeatLoss
    returnDict['infilstrationHeatLoss']=infiltrationHeatLoss
    returnDict['neighbourLosses']=neighbourLosses
    
    if returnDetail:
        return returnDict
    
    else:
        
        return totalHeatLoss




def computeHeatLossAreas(floorArea,heatLossAreaEstimation,onGround,underRoof,exposedPerimeter,neighbourPerimeter,wallHeight = 2.7):


    if heatLossAreaEstimation=='fromFloorArea':
        side = np.sqrt(floorArea)

        wallHeatLossArea = side*wallHeight*2 #2 walls toward outside
        neighbourWallArea = side*wallHeight*2 #2 neighbou walls 


    elif heatLossAreaEstimation=='fromExposedPerimeter':
        
        wallHeatLossArea = exposedPerimeter*wallHeight
        neighbourWallArea = neighbourPerimeter*wallHeight

    
    if onGround:
        
        groundHeatLossArea = floorArea
        
    else:
        groundHeatLossArea = 0
    

    if underRoof:
        roofHeatLossArea = floorArea
    else:
        roofHeatLossArea = 0



    if groundHeatLossArea == 0:
        neighbourFloorArea = floorArea
    else:
        neighbourFloorArea = 0

    

    return wallHeatLossArea,neighbourWallArea,groundHeatLossArea,roofHeatLossArea,neighbourFloorArea


def getVentilationFlows(vSystem,floorArea,wallHeight,calculationMethod='simple',roomType=None):
    #allowed calculations methods:
        # simple
        # NBN D 50 001
        # ...

    #returns flowFromOutside,flowFromInside

    if calculationMethod=='simple':    

        #assumes only outside air
        #assumes 70% heat recovery for D
        # --> overestimates for wet spaces with system C        

        ventilationAch={'C':1,'D':0.3}  
        volume =  floorArea*wallHeight
        Vach = ventilationAch[vSystem]         

        flow = volume*Vach


        return flow,0    


    if calculationMethod=='NBN-D-50-001':
        
        bounds = {'Living':
                      {'min':75,
                       'max':150
                       },
                  'Kitchen':
                      {'min':50,
                       'max':75},
                  'Bedroom':
                      {'min':25,
                       'max':72},
                  'Laundry':
                      {'min':50,
                       'max':75},
                  'Bathroom':
                      {'min':50,
                       'max':150},
                  None:{
                      'min':0,
                      'max':150}
                  }
                      
        
        nomFlow = 3.6*floorArea
        
        nomFlow = min(nomFlow,bounds[roomType]['max'])
        nomFlow = max(nomFlow,bounds[roomType]['min'])


        if roomType in ['Living','Bedroom','Bureau']:
            flowFromOutside = nomFlow 
            flowFromInside = 0
            if vSystem == 'D':
                flowFromOutside *= 0.3

        else:
            flowFromOutside = 0
            flowFromInside = nomFlow
       


        return flowFromOutside,flowFromInside


    else:    
        return 0,0
    




def tests():
    
    floorArea=10
    Uw=0.24
    Uroof=0.24
    Uground=0.7
    v50=1
    Tin=20
    Tout=-7
    vSystem='C'
    
    result = 578
    test1 = roomSimpleLoad(floorArea,Uw,Uroof,Uground,vSystem,v50,Tin,Tout,
                           neighbourT=18,
                           LIR=0.2,
                           heatLossAreaEstimation='fromFloorArea',
                           exposedPerimeter=0,
                           onGround=True,underRoof=False,
                           addNeighbourLosses=False,
                           neighbourPerimeter=0,
                           roomType=None)
    
    print(result,test1)

    
    result = 437
    test2 = roomSimpleLoad(floorArea,Uw,Uroof,Uground,vSystem='D',v50=v50,Tin=24,Tout=Tout,
                           neighbourT=18,
                           LIR=0.2,
                           heatLossAreaEstimation='fromFloorArea',
                           exposedPerimeter=0,
                           onGround=False,underRoof=True,
                           addNeighbourLosses=True,
                           neighbourPerimeter=0,
                           roomType='Bathroom')

    print(result,test2)

    result = 507
    test3 = roomSimpleLoad(floorArea,Uw,Uroof,Uground,vSystem='D',v50=v50,Tin=24,Tout=Tout,
                           neighbourT=18,
                           LIR=0.2,
                           heatLossAreaEstimation='fromExposedPerimeter',
                           exposedPerimeter=8,
                           onGround=False,underRoof=True,
                           addNeighbourLosses=True,
                           neighbourPerimeter=8,
                           roomType='Bahtroom')

    print(result,test3)    


if __name__ == '__main__':
    
    tests()
