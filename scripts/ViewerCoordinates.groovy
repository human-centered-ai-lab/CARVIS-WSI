import java.net.ServerSocket
def viewer = getCurrentViewer()

Thread thread = new Thread(){
    public void run(){
        i=0
        try{
            annotationsJsonsOld =""
            viewJsonOld = ""
            while (i<5){
                Thread.sleep(100);
                s = new Socket("localhost", 8089);
                s.withStreams { input, output ->
                  
                  
                   
                  pixelSichtbarInX = viewer.getView().getWidth()* viewer.getDownsampleFactor()
                  pixelSichtbarInY = viewer.getView().getHeight()* viewer.getDownsampleFactor()
                  topLeftX = Math.floor(viewer.getCenterPixelX()-(pixelSichtbarInX/2))
                  topRightX = Math.floor(viewer.getCenterPixelX()+(pixelSichtbarInX/2))
                  bottomLeftX = Math.floor(viewer.getCenterPixelX()-(pixelSichtbarInX/2))
                  bottomRightX = Math.floor(viewer.getCenterPixelX()+(pixelSichtbarInX/2))
               
                  topLeftY = Math.floor(viewer.getCenterPixelY()-(pixelSichtbarInY/2))
                  topRightY = Math.floor(viewer.getCenterPixelY()-(pixelSichtbarInY/2))
                  bottomLeftY = Math.floor(viewer.getCenterPixelY()+(pixelSichtbarInY/2))
                  bottomRightY = Math.floor(viewer.getCenterPixelY()+(pixelSichtbarInY/2))
                  
                  
                  viewJson='{"view":{'
                  viewJson=viewJson+'"Filename":"'+viewer.imageData.getServer().getMetadata().getName()+'",'
                  viewJson=viewJson+'"CurrentCenterX":'+viewer.getCenterPixelX()+','
                  viewJson=viewJson+'"CurrentCenterY":'+viewer.getCenterPixelY()+','
                  viewJson=viewJson+'"CurrentDownsampleFactor":'+viewer.getDownsampleFactor()+','
                  viewJson=viewJson+'"Width":'+viewer.getView().getWidth()+','
                  viewJson=viewJson+'"Height":'+viewer.getView().getHeight()+','
                  viewJson=viewJson+'"CurrentCenterY":'+viewer.getCenterPixelY()+','
                  viewJson=viewJson+'"CurrentCenterY":'+viewer.getCenterPixelY()+','
                  viewJson=viewJson+'"ViewROI":{'
                    
                  viewJson=viewJson+'"TopLeft":{"X":'+topLeftX+',"Y":'+topLeftY+'},'
                  viewJson=viewJson+'"TopRight":{"X":'+topRightX+',"Y":'+topRightY+'},'
                  viewJson=viewJson+'"BottomLeft":{"X":'+bottomLeftX+',"Y":'+bottomLeftY+'},'
                  viewJson=viewJson+'"BottomRight":{"X":'+bottomRightX+',"Y":'+bottomRightY+'}'
                    
                  viewJson=viewJson+'}'
                  viewJson=viewJson+'}}'
                  
                  
                  
                  annotationsJsons = '{"annotations":['
                  annoObj = viewer.imageData.getHierarchy().getAnnotationObjects()
                  hasAnno = 0
                  for (annotation in annoObj) {
                      hasAnno = 1
                      annotationsJsons = annotationsJsons + '{'+
                      '"type":"'+annotation.getROI().getRoiName()+
                      '", '+
                      '"class":"'+annotation.getPathClass()+'"'+
                      ', '+
                      '"points":"'+annotation.getROI().getAllPoints()+'"},'
                  }
                  if (hasAnno){
                      annotationsJsons = annotationsJsons.substring(0, annotationsJsons.length() - 1);
                  }
                  annotationsJsons = annotationsJsons + ']}'
                                  
                  
                  viewJsonSend = viewJson
                  if (viewJsonSend.equals(viewJsonOld)){
                      viewJsonSend="" 
                  }
                  
                  annotationsJsonsSend = annotationsJsons
                  if (annotationsJsonsSend.equals(annotationsJsonsOld)){
                      annotationsJsonsSend="" 
                  }
                 
                  if (!viewJsonSend.equals("") or !annotationsJsonsSend.equals("")){
                      output << "E;1;Qupath;1;;;;QupathData;"+viewJsonSend+";"+annotationsJsonsSend+"\r\n"
                  }
                  annotationsJsonsOld = annotationsJsons
                  viewJsonOld = viewJson
                }
                i = i+0
                // Project Script
             }
         }
         finally{
             s.close()
             print "Close"
         }
    }
  }

  thread.start();

