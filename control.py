from fakecamera import FakeCamera
import numpy as np

FC = FakeCamera()

### control ###

def cameraStandBy():
    FC.device_status = 1
    FC.server_status = 3

def cameraResetZero():
    FC.device_status = 3
    FC.set_angle(0, 0)

def cameraAutoRotate(horizontalAngularVelocity, verticalAngularVelocity):
    FC.device_status = 4
    FC.auto_speed_h = horizontalAngularVelocity
    FC.auto_speed_v = verticalAngularVelocity

def cameraFollow():
    if FC.follow_status != 2:
        FC.follow_status = 2
    else:
        FC.follow_status = 0
        FC.device_status = 3

def cameraCapture(x1, y1, x2, y2):
    FC.capture((x1, y1, x2-x1, y2-y1))

def cameraLocate(horizontalAngle, verticalAngle):
    FC.device_status = 3
    FC.set_angle(horizontalAngle, verticalAngle)

def cameraPowerUp():
    FC.server_status = 3

def cameraShutDown():
    FC.server_status = 0

def cameraThermalPowerUp():
    FC.thermal_status = 3

def cameraThermalShutDown():
    FC.thermal_status = 0

def cameraToVisible():
    FC.camera_mode = 0

def cameraToThermal():
    FC.camera_mode = 1

def cameraVisibleViewLarge():
    FC.visible_view = 1

def cameraVisibleViewSmall():
    FC.visible_view = 0

def cameraThermalViewLarge():
    FC.thermal_view = 1
        
def cameraThermalViewSmall():
    FC.thermal_view = 0

def cameraThermalFocalInc():
    FC.focal_length += 1

def cameraThermalFocalDec():
    FC.focal_length -= 1

def cameraMeasureDistance():
    FC.distance = np.random.randint(100, 200)


### state ###

def getCameraStatus():
    return FC.device_status

def getThermalview():
    return FC.thermal_view

def getThermalstatus():
    return FC.thermal_status

def getVisibleView():
    return FC.visible_view

def getCameraMode():
    return FC.camera_mode

def getServerStatus():
    return FC.server_status

def getHorizontalAngle():
    return FC.angle_h

def getVerticalAngle():
    return FC.angle_v

def getHorizontalRotateSpeed():
    return FC.auto_speed_h

def getVerticalRotateSpeed():
    return FC.auto_speed_v

def getDistance():
    return FC.distance

def getFollowStatus():
    return FC.follow_status
