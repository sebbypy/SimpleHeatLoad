
import numpy as np


class RoomLoadCalculator:
    
    def __init__(self,
                 floorArea,
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
        
        self.floorArea = floorArea
        self.Uw = Uw
        self.Uroof = Uroof
        self.Uground = Uground
        self.vSystem= vSystem
        self.v50 = v50
        self.Tin = Tin
        self.Tout = Tout
        self.neighbourT=neighbourT
        self.Un=Un
        self.LIR=LIR
        self.heatLossAreaEstimation=heatLossAreaEstimation
        self.ventilationCalculationMethod=ventilationCalculationMethod
        self.exposedPerimeter=exposedPerimeter
        self.onGround=onGround
        self.underRoof=underRoof
        self.addNeighbourLosses=addNeighbourLosses
        self.neighbourPerimeter=neighbourPerimeter
        self.roomType = roomType 
        self.wallHeight=wallHeight
        self.returnDetail=returnDetail
        
    
    def compute(self):

        deltaT=self.Tin-self.Tout
        
        wallHeatLossArea,neighbourWallArea,groundHeatLossArea,roofHeatLossArea,neighbourFloorArea = self.computeHeatLossAreas()


        if self.addNeighbourLosses:
            
            neighbourLosses = self.Un*(self.Tin-self.neighbourT)*(neighbourWallArea+neighbourFloorArea)

        else:
            neighbourLosses=0


        insideDeltaT = max(0,self.Tin-self.neighbourT)

        outsideAirVentilationFlowRate,insideAirVentilationFlowRate = self.getVentilationFlows()
        

        ventilationHeatLoss  = 0.34*(outsideAirVentilationFlowRate)*deltaT + 0.34*(insideAirVentilationFlowRate)*insideDeltaT

        infiltrationHeatLoss = 0.34*self.LIR*self.v50*(wallHeatLossArea + roofHeatLossArea + groundHeatLossArea)*deltaT 
        transmissionHeatLoss = (wallHeatLossArea*self.Uw + roofHeatLossArea*self.Uroof + groundHeatLossArea*self.Uground)*deltaT

        
        totalHeatLoss = transmissionHeatLoss + ventilationHeatLoss + infiltrationHeatLoss + neighbourLosses

        returnDict = {}
        
        returnDict['totalHeatLoss'] = totalHeatLoss
        returnDict['transmissionHeatLoss']=transmissionHeatLoss
        returnDict['ventilationHeatLoss']=ventilationHeatLoss
        returnDict['infilstrationHeatLoss']=infiltrationHeatLoss
        returnDict['neighbourLosses']=neighbourLosses
        
        
        #wallHeatLossArea,neighbourWallArea,groundHeatLossArea,roofHeatLossArea,neighbourFloorArea
        
        
        
        if self.returnDetail:
            return returnDict
        
        else:
            
            return totalHeatLoss


    def computeHeatLossAreas(self):


        if self.heatLossAreaEstimation=='fromFloorArea':
            side = np.sqrt(self.floorArea)
    
            wallHeatLossArea = side*self.wallHeight*2 #2 walls toward outside
            neighbourWallArea = side*self.wallHeight*2 #2 neighbou walls 
    
    
        elif self.heatLossAreaEstimation=='fromExposedPerimeter':
            
            wallHeatLossArea = self.exposedPerimeter*self.wallHeight
            neighbourWallArea = self.neighbourPerimeter*self.wallHeight
    
        
        if self.onGround:
            
            groundHeatLossArea = self.floorArea
            
        else:
            groundHeatLossArea = 0
        
    
        if self.underRoof:
            roofHeatLossArea = self.floorArea
        else:
            roofHeatLossArea = 0
    
    
    
        if groundHeatLossArea == 0:
            neighbourFloorArea = self.floorArea
        else:
            neighbourFloorArea = 0
    
        
    
        return wallHeatLossArea,neighbourWallArea,groundHeatLossArea,roofHeatLossArea,neighbourFloorArea
    

    def getVentilationFlows(self):
        
        #allowed calculations methods:
            # simple
            # NBN D 50 001
            # ...

        #returns flowFromOutside,flowFromInside

        if self.ventilationCalculationMethod=='simple':    

            #assumes only outside air
            #assumes 70% heat recovery for D
            # --> overestimates for wet spaces with system C        

            ventilationAch={'C':1,'D':0.3}  
            volume =  self.floorArea*self.wallHeight
            Vach = ventilationAch[self.vSystem]         

            flow = volume*Vach


            return flow,0    


        if self.ventilationCalculationMethod=='NBN-D-50-001':
            
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
                          'max':150},
                      'None':{
                          'min':0,
                          'max':150},
                      'Toilet':{
                           'min':25,
                           'max':25
                           }
                      }
                          
            
            nomFlow = 3.6*self.floorArea
            
            nomFlow = min(nomFlow,bounds[self.roomType]['max'])
            nomFlow = max(nomFlow,bounds[self.roomType]['min'])


            if self.roomType in ['Living','Bedroom','Bureau']:
                flowFromOutside = nomFlow 
                flowFromInside = 0
                if self.vSystem == 'D':
                    flowFromOutside *= 0.3

            else:
                flowFromOutside = 0
                flowFromInside = nomFlow
           


            return flowFromOutside,flowFromInside


        else:    
            return 0,0

        
        """to fill"""
        
        return





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

    test1 = RoomLoadCalculator(floorArea,Uw, Uroof, Uground, vSystem,v50,Tin,Tout,
                           neighbourT=18,
                           LIR=0.2,
                           heatLossAreaEstimation='fromFloorArea',
                           exposedPerimeter=0,
                           onGround=True,underRoof=False,
                           addNeighbourLosses=False,
                           neighbourPerimeter=0,
                           roomType=None).compute()
    
    
    print(result,test1)

    
    result = 437
    test2 = RoomLoadCalculator(floorArea,Uw,Uroof,Uground,vSystem='D',v50=v50,Tin=24,Tout=Tout,
                           neighbourT=18,
                           LIR=0.2,
                           heatLossAreaEstimation='fromFloorArea',
                           exposedPerimeter=0,
                           onGround=False,underRoof=True,
                           addNeighbourLosses=True,
                           neighbourPerimeter=0,
                           roomType='Bathroom').compute()

    print(result,test2)

    result = 507
    test3 = RoomLoadCalculator(floorArea,Uw,Uroof,Uground,vSystem='D',v50=v50,Tin=24,Tout=Tout,
                           neighbourT=18,
                           LIR=0.2,
                           heatLossAreaEstimation='fromExposedPerimeter',
                           exposedPerimeter=8,
                           onGround=False,underRoof=True,
                           addNeighbourLosses=True,
                           neighbourPerimeter=8,
                           roomType='Bahtroom').compute()

    print(result,test3)    


if __name__ == '__main__':
    
    tests()
