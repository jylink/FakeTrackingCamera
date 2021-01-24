import cv2
import time
import numpy as np
from utils import *

class FakeCamera:
    def __init__(self):
        ################# DESIGN YOUR SCENE HERE ###################
        self.res_x = 800    # frame resolution x
        self.res_y = 600    # frame resolution y

        self._frame = cv2.imread('imgs/background.jpg')
        self._frame = cv2.resize(self._frame, (int(self._frame.shape[1]*1.2), int(self._frame.shape[0]*1.2)))
        self._targets = {
            'person1': cv2.imread('imgs/person1.png', cv2.IMREAD_UNCHANGED),
            'person2': cv2.imread('imgs/person2.png', cv2.IMREAD_UNCHANGED),
        }

        def _simple_moving(background, foreground, time_elapse=None, delta_time=None):
            h, w = background.shape[:2]

            person = foreground['person1']
            person_x = w * 0.6
            person_y = h * 0.55
            person_scale = 0.35
            if time_elapse % 10 < 5:
                person_x += 30 * (time_elapse % 10)
            else:
                person_x += 30 * (10 - (time_elapse % 10))
                person = person[:,::-1]
            if time_elapse < 12:
                if time_elapse > 10:
                    person[:,:,:] = person[:,:,:] * (12-time_elapse)/2
                background = overlay_transparent(background, person, int(person_x), int(person_y), 
                (int(person.shape[1]*person_scale), int(person.shape[0]*person_scale)))

            person = foreground['person2']
            person_x = w * 0.85
            person_y = h * 0.5
            person_scale = 0.25
            if time_elapse % 10 < 5:
                person_x += 30 * (time_elapse % 10)
            else:
                person_x += 30 * (10 - (time_elapse % 10))
                person = person[:,::-1]
            if time_elapse < 32:
                if time_elapse > 30:
                    person[:,:,:] = person[:,:,:] * (32-time_elapse)/2
                background = overlay_transparent(background, person, int(person_x), int(person_y), 
                (int(person.shape[1]*person_scale), int(person.shape[0]*person_scale)))

            return background

        self._update_foreground = _simple_moving
        #########################################################

        self.angle_h = 0                    # horizontal angle, [-180, 180]
        self.angle_v = 0                    # vertical angle, [-90, 90]
        self.auto_speed_h = 0               # horizontal auto rotate speed
        self.auto_speed_v = 0               # vertical auto rotate speed
        self.loc_speed_h = self.res_x // 10   # horizontal location speed
        self.loc_speed_v = self.res_y // 10   # vertical location speed

        frame_y, frame_x = self._frame.shape[:2] 
        assert self.res_x <= frame_x
        assert self.res_y <= frame_y

        self.fov_h = 360 * self.res_x / frame_x  # horizontal field of view
        self.fov_v = 180 * self.res_y / frame_y  # vertical field of view
        
        self._target_position = None  # target position to locate
        self._update_timer0 = None    # time of first update
        self._update_timer = None     # time of latest update
        self._delta_time = None       # time between the latest update and the update before the latest 

        self._tracker = None        # build-in tracker
        self._track_lost = 0        # number of continuous lost frame
        self._max_lost = 30         # max continuous lost frame
        self._track_predict = None  # bbox prediction
        
        self.device_status = 1      # 1: standby, 2: manual rotate, 3: locate, 4: auto rotate
        self.thermal_view = 0       # 0: small view, 1: large view
        self.thermal_status = 0     # 0: closed，2：starting 3：ready
        self.visible_view = 1       # 0: small view, 1: large view
        self.camera_mode = 0        # 0: visible, 1: thermal
        self.server_status = 3      # 0: closed，2：starting 3：ready
        self.follow_status = 0      # 0: idle, 1: captured, 2: tracking, 3: tracking failed
        self.focal_length = 0
        self.distance = 0

    def _to_thermal(self, frame):
        return np.expand_dims(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), axis=2).repeat(3, axis=2)

    def _to_smallview(self, frame):
        h, w = frame.shape[:2]
        return cv2.resize(frame[h//4 : h*3//4, w//4 : w*3//4], (w, h))

    def _focus(self, frame, focal_length):
        if focal_length == 0:
            return frame
        return cv2.GaussianBlur(frame, (abs(focal_length),abs(focal_length)), abs(focal_length))

    def _rotate_h(self, delta_ha):
        # horizontally 360 degree rotation
        return (self.angle_h + 180 + delta_ha) % 360 - 180

    def _rotate_v(self, delta_va):
        # vertically -90~90 degree rotation
        return min(max(self.angle_v + delta_va, -90), 90)

    def pix2ang(self, x, y):
        # pixel on frame to absolute angle
        delta_ha = (x - self.res_x / 2) / self.res_x * self.fov_h
        delta_va = -(y - self.res_y / 2) / self.res_y * self.fov_v
        return self._rotate_h(delta_ha), self._rotate_v(delta_va)

    def set_angle(self, ha, va):
        ha = min(max(ha, -180), 180)
        va = min(max(va, -90), 90)
        self._target_position = (ha, va)

    def capture(self, bbox):
        # bbox: x1, y1, w, h
        if self._update_timer is None:
            return
        frame = self.read_frame()
        frame_y, frame_x = frame.shape[:2] 
        x, y, w, h = bbox
        x = min(max(x, 0), frame_x)
        y = min(max(y, 0), frame_y)
        w = min(max(w, 0), frame_x - x)
        h = min(max(h, 0), frame_y - y)
        self._tracker = cv2.TrackerKCF_create()
        self._tracker.init(frame, (x,y,w,h))

    def update(self):
        if self._update_timer is None:
            self._update_timer0 = time.time()
            self._update_timer = time.time()

        self._delta_time = time.time() - self._update_timer
        self._update_timer = time.time()

        if self.server_status != 3:  # server closed
            return

        if self.follow_status != 2 and self.device_status == 0x01:  # standby
            return

        elif self.follow_status != 2 and (self.device_status == 0x02 or self.device_status == 0x04):  # auto/manual rotate
            self.angle_h = self._rotate_h(self.auto_speed_h * self._delta_time)
            self.angle_v = self._rotate_v(self.auto_speed_v * self._delta_time)

        elif self.follow_status == 2 or self.device_status == 0x03:  # tracking or locating

            if self.follow_status == 2:  # tracking
                frame = self.read_frame()
                success, bbox = self._tracker.update(frame)

                if success:
                    pos = self.pix2ang(bbox[0]+bbox[2]/2, bbox[1]+bbox[3]/2)
                    self._target_position = pos
                    self._track_lost = 0
                    self._track_predict = bbox
                else:
                    self._track_lost += 1
                    self._track_predict = None
                    if self._track_lost >= self._max_lost:
                        self.follow_status = 3
                        self.device_status = 0x03

            self.auto_speed_h = 0
            self.auto_speed_v = 0
            ha, va = self._target_position
            smooth = ((ha - self.angle_h)**2 + (va - self.angle_v) ** 2) / (self.fov_h**2 + self.fov_v**2) * 20
            if self.follow_status == 2:
                smooth = min(smooth, 0.2)
            else:
                smooth = min(smooth, 2)

            hs = 1 if (ha >= self.angle_h and ha - self.angle_h <= 180) or (self.angle_h > ha and self.angle_h - ha > 180) else -1
            vs = 1 if va - self.angle_v > 0 else -1
            delta_ha = self.loc_speed_h * self._delta_time * hs * smooth
            delta_va = self.loc_speed_v * self._delta_time * vs * smooth
            self.angle_h = self._rotate_h(delta_ha) if abs(ha - self.angle_h) > abs(delta_ha) else ha
            self.angle_v = self._rotate_v(delta_va) if abs(va - self.angle_v) > abs(delta_va) else va

    def read_frame(self, debug=False):
        # camera mode (part 1)
        if self.camera_mode == 0:
            frame = self._update_foreground(self._frame, self._targets, time_elapse=time.time()-self._update_timer0, delta_time=self._delta_time)
            frame = self._focus(frame, self.focal_length)
        elif self.thermal_status == 3 and self.camera_mode == 1:
            frame = self._update_foreground(self._frame//4, self._targets, time_elapse=time.time()-self._update_timer0, delta_time=self._delta_time)
            frame = self._to_thermal(frame)
            frame = self._focus(frame, self.focal_length)
        else:
            frame = self._frame * 0

        frame_y, frame_x = frame.shape[:2] 
        cx = int(frame_x / 2 + frame_x * self.angle_h / 360)
        cy = int(frame_y / 2 - frame_y * self.angle_v / 180)
        x1 = cx - self.res_x // 2
        x2 = cx + self.res_x // 2
        y1 = cy - self.res_y // 2
        y2 = cy + self.res_y // 2

        # horizontal cycle
        if x1 < 0:
            frame = cv2.hconcat([frame[:, x1:], frame[:, :x2]])
        elif x2 >= frame_x:
            frame = cv2.hconcat([frame[:, x1:], frame[:, :x2 - frame_x]])
        else:
            frame = frame[:, x1:x2]
        
        # vertical padding
        y1 += frame.shape[0]
        y2 += frame.shape[0]
        frame = cv2.vconcat([frame[::-1], frame, frame[::-1]])
        frame = frame[y1:y2]
        
        # camera mode (part 2)
        if self.camera_mode == 0 and self.visible_view == 0:
            frame = self._to_smallview(frame)
        elif self.thermal_status == 3 and self.camera_mode == 1 and self.thermal_view == 0:
            frame = self._to_smallview(frame)

        if debug:
            if self._track_predict is not None:
                if self.distance > 0:
                    text = f'distance {self.distance}'
                else:
                    text = None
                plot_one_box(ltwh2xyxy(self._track_predict), frame, color=(255,0,0), label=text)
            plot_text((0, self.res_y), frame, color=(255,0,0),
                    text=f'device_stats {self.device_status} thermal_view {self.thermal_view} '\
                        f'thermal_status {self.thermal_status} visible_view {self.visible_view} '\
                        f'\ncamera_mode {self.camera_mode} server_status {self.server_status} follow_status {self.follow_status} '\
                        f'focal_length {self.focal_length} distance {self.distance} ')
        return frame
