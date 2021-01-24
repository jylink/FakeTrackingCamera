# FakeTrackingCamera



This is a fake camera system used to quickly test your object tracking program



Imaging roll a seamless image into a cylinder and put a camera in the center, then it can do horizontal 360 degree rotation to observe the scene

[]()



# Requirements

```
torch
opencv-contrib-python
numpy
torch
matplotlib
pillow
```



# Example

`cameraLocate(angle_h, angle_v)`: rotate to specific angle

* angle_h: [-180, 180]
* angle_v: [-90, 90]

[]()



`cameraAutoRotate(speed_h, speed_v)`: auto rotate with specific speed

[]()



`cameraVisibleViewSmall()`: change to small view

[]()



`cameraThermalFocalInc()` and `cameraThermalFocalDec()`: simulate focal length adjustment

[]()



`cameraThermalPowerUp()` and `cameraToThermal()`: simulate IR camera

[]()



`cameraCapture(x1, y1, x2, y2)` and `cameraFollow()`: use build-in tracking alg (KCF)

[]()



`cameraMeasureDistance()`: simulate laser ranging

[]()



An example using [yolo+deepsort](https://github.com/mikel-brostrom/Yolov3_DeepSort_Pytorch) to track and aim with the fake camera

Edit `FakeCamera.__init__()` to design the scene

[]()