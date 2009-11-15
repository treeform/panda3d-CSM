from pandac.PandaModules import *
import sys,os
loadPrcFileData("", "prefer-parasite-buffer #f")

import direct.directbase.DirectStart
from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.actor import Actor
from random import *

font = loader.loadFont("cmss12")

# Function to put instructions on the screen.
def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1,1,1,1), mayChange=1, font = font,
                        pos=(-1.3, pos), align=TextNode.ALeft, scale = .05, shadow=(0,0,0,1), shadowOffset=(0.1,0.1))

# Function to put title on the screen.
def addTitle(text):
    return OnscreenText(text=text, style=1, fg=(1,1,1,1), font = font,
                        pos=(1.3,-0.95), align=TextNode.ARight, scale = .07)


class ShadowCam:
    
    SIZE = 512
    #SIZE = 1024
    #SIZE = 2048
    
    def __init__(self):
         
        self.LCam1, Ldepthmap1 = self.createCam()
        self.LCam2, Ldepthmap2 = self.createCam()
        self.LCam3, Ldepthmap3 = self.createCam()

        self.LCam1.node().getLens().setFilmSize(200)
        #LCam1.node().getLens().setNearFar(10,200)
        
        self.LCam2.node().getLens().setFilmSize(100)
        #LCam2.node().getLens().setNearFar(5,100)

        self.LCam3.node().getLens().setFilmSize(25)
        #LCam3.node().getLens().setNearFar(1,25)


        # default values
        self.pushBias=0.7
        self.ambient=0.1
        self.cameraSelection = 0
        self.lightSelection = 0
    
        # setting up shader
        #render.setShaderInput('light',self.LCam1)
        render.setShaderInput('light1',self.LCam1)
        render.setShaderInput('light2',self.LCam2)
        render.setShaderInput('light3',self.LCam3)
        
        render.setShaderInput('Ldepthmap1',Ldepthmap1)
        render.setShaderInput('Ldepthmap2',Ldepthmap2)
        render.setShaderInput('Ldepthmap3',Ldepthmap3)
        
        render.setShaderInput('ambient',self.ambient,0,0,1.0)
        render.setShaderInput('texDisable',0,0,0,0)
        render.setShaderInput('scale',1,1,1,1)
       
        mci = NodePath(PandaNode("Main Camera Initializer"))
        mci.setShader(Shader.load('csm-shadow.sha'))
        base.cam.node().setInitialState(mci.getState())
    
        self.adjustPushBias(1)

    def createCam(self):
        # creating the offscreen buffer.
        winprops = WindowProperties.size(self.SIZE,self.SIZE)
        props = FrameBufferProperties()
        props.setRgbColor(1)
        props.setAlphaBits(1)
        props.setDepthBits(1)
        LBuffer = base.graphicsEngine.makeOutput(
                 base.pipe, "offscreen buffer", -2,
                 props, winprops,
                 GraphicsPipe.BFRefuseWindow,
                 base.win.getGsg(), base.win)

        if (LBuffer == None):
            raise "Shadow Demo: Video driver cannot create an offscreen buffer."

        Ldepthmap = Texture()
        LBuffer.addRenderTexture(Ldepthmap, GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPDepthStencil)
        if (base.win.getGsg().getSupportsShadowFilter()):
            Ldepthmap.setMinfilter(Texture.FTShadow)
            Ldepthmap.setMagfilter(Texture.FTShadow) 
      
        Lcolormap = Texture()
        LBuffer.addRenderTexture(Lcolormap, GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPColor)
    
        LCam=base.makeCamera(LBuffer)
        LCam.node().setScene(render)
        
        lens = OrthographicLens()
        lens.setFilmSize(200)
        lens.setNearFar(10,200)
        LCam.node().setLens(lens)
        LCam.setPos(0,-60,60)
        LCam.lookAt(0,0,0)
        LCam.node().showFrustum()
        
        
        # Put a shader on the Light camera.
        lci = NodePath(PandaNode("Light Camera Initializer"))
        lci.setShader(Shader.load('caster.sha'))
        LCam.node().setInitialState(lci.getState())
        
        return LCam,Lcolormap
    

    def adjustPushBias(self,inc):
        self.pushBias *= inc
        print         self.pushBias
        #self.inst_a.setText('A/Z: Increase/Decrease the Push-Bias [%F]' % self.pushBias)
        render.setShaderInput('push',self.pushBias,self.pushBias,self.pushBias,0)
  


class World(DirectObject):
    def __init__(self):
        # Preliminary capabilities check.
    
        if (base.win.getGsg().getSupportsBasicShaders()==0):
            self.t=addTitle("Shadow Demo: Video driver reports that shaders are not supported.")
            return
        if (base.win.getGsg().getSupportsDepthTexture()==0):
            self.t=addTitle("Shadow Demo: Video driver reports that depth textures are not supported.")
            return
       
        # Adding a color texture is totally unnecessary, but it helps with debugging.
      
#        self.inst_p = addInstructions(0.95, 'P : stop/start the Panda Rotation')
#        self.inst_w = addInstructions(0.90, 'W : stop/start the Walk Cycle')
#        self.inst_t = addInstructions(0.85, 'T : stop/start the Teapot')
#        self.inst_l = addInstructions(0.80, 'L : move light source far or close')
#        self.inst_v = addInstructions(0.75, 'V: View the Depth-Texture results')
#        self.inst_x = addInstructions(0.70, 'Left/Right Arrow : switch camera angles')
#        self.inst_a = addInstructions(0.65, 'Something about A/Z and push bias')
    
        base.setBackgroundColor(0,0,0,1)
        base.camLens.setNearFar(1.0,10000)
        # Load the scene.
    
        floorTex=loader.loadTexture('maps/envir-ground.jpg')
#        cm=CardMaker('')
#        cm.setFrame(-2,2,-2,2)
#        floor = render.attachNewNode(PandaNode("floor"))
#        for y in range(12):
#            for x in range(12):
#                nn = floor.attachNewNode(cm.generate())
#                nn.setP(-90)
#                nn.setPos((x-6)*4, (y-6)*4, 0)
        floor = loader.loadModel("city.bam")
        floor.setTwoSided(True)
        floor.setHpr(45,-90,0)
        floor.reparentTo(render)
        floor.setTexture(floorTex)
        floor.flattenStrong()
    
        self.pandaAxis=render.attachNewNode('panda axis')
        self.pandaModel=Actor.Actor('panda-model',{'walk':'panda-walk4'})
        self.pandaModel.reparentTo(self.pandaAxis)
        self.pandaModel.setPos(9,0,0)
        self.pandaModel.setShaderInput("scale",0.01,0.01,0.01,1.0)
        self.pandaWalk = self.pandaModel.actorInterval('walk',playRate=1.8)
        self.pandaWalk.loop()
        self.pandaMovement = self.pandaAxis.hprInterval(20.0,Point3(-360,0,0),startHpr=Point3(0,0,0))
        self.pandaMovement.loop()
    
        self.teapot=loader.loadModel('teapot')
        self.teapot.reparentTo(render)
        self.teapot.setPos(0,-20,10)
        self.teapot.setShaderInput("texDisable",1,1,1,1)
        self.teapotMovement = self.teapot.hprInterval(50,Point3(0,360,360))
        self.teapotMovement.loop()
    
        self.accept('escape',sys.exit)
    
#        self.accept("arrow_left", self.incrementCameraPosition, [-1])
#        self.accept("arrow_right", self.incrementCameraPosition, [1])

        

        self.accept("p", self.toggleInterval, [self.pandaMovement])
        self.accept("P", self.toggleInterval, [self.pandaMovement])
        self.accept("t", self.toggleInterval, [self.teapotMovement])
        self.accept("T", self.toggleInterval, [self.teapotMovement])
        self.accept("w", self.toggleInterval, [self.pandaWalk])
        self.accept("W", self.toggleInterval, [self.pandaWalk])
        self.accept("v", base.bufferViewer.toggleEnable)
        self.accept("V", base.bufferViewer.toggleEnable)
#        self.accept("l", self.incrementLightPosition, [1])
#        self.accept("L", self.incrementLightPosition, [1])
        self.accept("o", base.oobe)
        
        
    
        self.shadowCam = ShadowCam()
        
        self.accept("space", self.castFromHere)
        
        self.accept('a',self.shadowCam.adjustPushBias,[1.1])
        self.accept('A',self.shadowCam.adjustPushBias,[1.1])
        self.accept('z',self.shadowCam.adjustPushBias,[0.9])
        self.accept('Z',self.shadowCam.adjustPushBias,[0.9])
    
    def castFromHere(self):
        self.shadowCam.LCam1.setPos(base.cam.getPos())
        self.shadowCam.LCam1.setHpr(base.cam.getHpr())
        self.shadowCam.LCam2.setPos(base.cam.getPos())
        self.shadowCam.LCam2.setHpr(base.cam.getHpr())
        self.shadowCam.LCam3.setPos(base.cam.getPos())
        self.shadowCam.LCam3.setHpr(base.cam.getHpr())
        
# end of __init__

    def toggleInterval(self, ival):
        if (ival.isPlaying()):
            ival.pause()
        else:
            ival.resume()
  
   

World()
class TestFlyer(DirectObject):
    def __init__(self):
        base.disableMouse()
        self.moveVec = Vec3(0,0,0)
        taskMgr.add(self.mouse, 'mouseTask')
        self.accept( "arrow_up" , self.up )
        self.accept( "arrow_down" , self.down )
        self.accept( "arrow_up-up" , self.stop )
        self.accept( "arrow_down-up" , self.stop )
        
        self.accept( "mouse1" , self.pan )
        self.accept( "mouse1-up" , self.panStop )
        self.pan = False
         
    def pan(self):
        md = base.win.getPointer(0)
        self.pan = Vec2(md.getX(),md.getY())
    
    def panStop(self):
        self.pan = False
        
    def stop(self):
        self.moveVec = Vec3(0,0,0)
    
    def up(self):
        self.moveVec = Vec3(0,1,0)
        
    def down(self):
        self.moveVec = Vec3(0,-1,0)
        
    def mouse(self,task):
        base.cam.setPos(base.cam,self.moveVec*globalClock.getDt()*100)
          
        if self.pan:
            md = base.win.getPointer(0)
            #print md
            x = md.getX()
            y = md.getY()
            if x != 0 and y != -48:
                deltax =  (x - self.pan.getX())*0.1
                deltay =  (y - self.pan.getY())*0.1
                base.cam.setH(base.cam, -deltax)
                base.cam.setP(base.cam, -deltay)
                self.pan = Vec2(md.getX(),md.getY())
        return task.cont
   
TestFlyer()
run()
