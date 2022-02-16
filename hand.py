from xyz import xyz

class Hand:
    def __init__(self, handdata_raw):
        self.thumb_tip = xyz(0, 0, 0)
        self.index_tip = xyz(0, 0, 0)
        self.middle_tip = xyz(0, 0, 0)
        self.ring_tip = xyz(0, 0, 0)
        self.pinky_tip = xyz(0, 0, 0)
        self.thumb_base = xyz(0, 0, 0)
        self.index_base = xyz(0, 0, 0)
        self.middle_base = xyz(0, 0, 0)
        self.ring_base = xyz(0, 0, 0)
        self.pinky_base = xyz(0, 0, 0)
        self.wrist = xyz(0, 0, 0)
        self.palm_center = xyz(0, 0, 0)

        # getting upper joint coordinate of each finger
        self.thumb_upperj = xyz(0, 0, 0)
        self.index_upperj = xyz(0, 0, 0)
        self.middle_upperj = xyz(0, 0, 0)
        self.ring_upperj = xyz(0, 0, 0)
        self.pinky_upperj = xyz(0, 0, 0)

    def update(self, handdata_raw):
        # takes hand landmark data from mediapipe hands and processes it
        if handdata_raw == None:  # hand is out of frame
            self.reset()
            return

        # Getting hand interestpoints: (x,y,z)
        self.thumb_tip = xyz(
            handdata_raw.landmark[4].x,
            handdata_raw.landmark[4].y,
            handdata_raw.landmark[4].z,
        )
        self.index_tip = xyz(
            handdata_raw.landmark[8].x,
            handdata_raw.landmark[8].y,
            handdata_raw.landmark[8].z,
        )
        self.middle_tip = xyz(
            handdata_raw.landmark[12].x,
            handdata_raw.landmark[12].y,
            handdata_raw.landmark[12].z,
        )
        self.ring_tip = xyz(
            handdata_raw.landmark[16].x,
            handdata_raw.landmark[16].y,
            handdata_raw.landmark[16].z,
        )
        self.pinky_tip = xyz(
            handdata_raw.landmark[20].x,
            handdata_raw.landmark[20].y,
            handdata_raw.landmark[20].z,
        )
        self.thumb_base = xyz(
            handdata_raw.landmark[2].x,
            handdata_raw.landmark[2].y,
            handdata_raw.landmark[2].z,
        )
        self.index_base = xyz(
            handdata_raw.landmark[5].x,
            handdata_raw.landmark[5].y,
            handdata_raw.landmark[5].z,
        )
        self.middle_base = xyz(
            handdata_raw.landmark[9].x,
            handdata_raw.landmark[9].y,
            handdata_raw.landmark[9].z,
        )
        self.ring_base = xyz(
            handdata_raw.landmark[13].x,
            handdata_raw.landmark[13].y,
            handdata_raw.landmark[13].z,
        )
        self.pinky_base = xyz(
            handdata_raw.landmark[17].x,
            handdata_raw.landmark[17].y,
            handdata_raw.landmark[17].z,
        )
        self.wrist = xyz(
            handdata_raw.landmark[0].x,
            handdata_raw.landmark[0].y,
            handdata_raw.landmark[0].z,
        )
        self.thumb_upperj = xyz(
            handdata_raw.landmark[3].x,
            handdata_raw.landmark[3].y,
            handdata_raw.landmark[3].z,
        )
        self.index_upperj = xyz(
            handdata_raw.landmark[7].x,
            handdata_raw.landmark[7].y,
            handdata_raw.landmark[7].z,
        )
        self.middle_upperj = xyz(
            handdata_raw.landmark[11].x,
            handdata_raw.landmark[11].y,
            handdata_raw.landmark[11].z,
        )
        self.ring_upperj = xyz(
            handdata_raw.landmark[15].x,
            handdata_raw.landmark[15].y,
            handdata_raw.landmark[15].z,
        )
        self.pinky_upperj = xyz(
            handdata_raw.landmark[19].x,
            handdata_raw.landmark[19].y,
            handdata_raw.landmark[19].z,
        )
    
    def reset(self):
        """Gets called when hand is out of frame"""
        
        # reset hand interestpoints (x,y,z)
        self.thumb_tip = xyz(0, 0, 0)
        self.index_tip = xyz(0, 0, 0)
        self.middle_tip = xyz(0, 0, 0)
        self.ring_tip = xyz(0, 0, 0)
        self.pinky_tip = xyz(0, 0, 0)
        self.thumb_base = xyz(0, 0, 0)
        self.index_base = xyz(0, 0, 0)
        self.middle_base = xyz(0, 0, 0)
        self.ring_base = xyz(0, 0, 0)
        self.pinky_base = xyz(0, 0, 0)
        self.wrist = xyz(0, 0, 0)
        self.palm_center = xyz(0, 0, 0)
        self.thumb_upperj = xyz(0, 0, 0)
        self.index_upperj = xyz(0, 0, 0)
        self.middle_upperj = xyz(0, 0, 0)
        self.ring_upperj = xyz(0, 0, 0)
        self.pinky_upperj = xyz(0, 0, 0)
