# FakeTrackingCamera



This is a fake camera system used to quickly test your object tracking program



Imagine rolling a seamless image into a cylinder and putting a camera in the center, then it can do a horizontal 360 degree rotation to view the scene

![](https://github.com/jylink/FakeTrackingCamera/blob/main/imgs/cylinder.png)



# Requirements

```
numpy
torch
opencv-contrib-python
matplotlib
pillow
```



# Example

`cameraLocate(angle_h, angle_v)`: rotate to specific angle

* angle_h: [-180, 180]
* angle_v: [-90, 90]

![](https://github.com/jylink/FakeTrackingCamera/blob/main/imgs/locate.gif)



`cameraAutoRotate(speed_h, speed_v)`: auto rotate with specific speed

![](https://github.com/jylink/FakeTrackingCamera/blob/main/imgs/auto.gif)



`cameraVisibleViewSmall()`: change to small view

![](https://github.com/jylink/FakeTrackingCamera/blob/main/imgs/smallview.gif)



`cameraThermalFocalInc()` and `cameraThermalFocalDec()`: simulate focal length adjustment

![](https://github.com/jylink/FakeTrackingCamera/blob/main/imgs/focal.gif)



`cameraThermalPowerUp()` and `cameraToThermal()`: simulate IR camera

![](https://github.com/jylink/FakeTrackingCamera/blob/main/imgs/thermal.gif)



`cameraCapture(x1, y1, x2, y2)` and `cameraFollow()`: use build-in tracking alg (KCF)

![](https://github.com/jylink/FakeTrackingCamera/blob/main/imgs/track.gif)



`cameraMeasureDistance()`: simulate laser ranging

![](https://github.com/jylink/FakeTrackingCamera/blob/main/imgs/track+measure.gif)



An example using [yolo+deepsort](https://github.com/mikel-brostrom/Yolov3_DeepSort_Pytorch) to track and aim with the fake camera

Edit `FakeCamera.__init__()` to design the scene

![](https://github.com/jylink/FakeTrackingCamera/blob/main/imgs/deepsort.gif)
