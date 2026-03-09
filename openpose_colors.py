
_VALID_OPEN_POSE_COLORS = {
    # black and white
    (0, 0, 0),         # Background                     #000000
    (255, 255, 255),         # Stars                          #FFFFFF

    # Joints 0-17 (Red-Yellow gradient)
    (255, 0, 0),       # Joint 0: Nose                  #FF0000
    (255, 85, 0),      # Joint 1: Neck                  #FF5500
    (255, 170, 0),     # Joint 2: Right Shoulder        #FFAA00
    (255, 255, 0),     # Joint 3: Right Elbow           #FFFF00
    (170, 255, 0),     # Joint 4: Right Wrist           #AAFF00
    (85, 255, 0),      # Joint 5: Left Shoulder         #55FF00
    (0, 255, 0),       # Joint 6: Left Elbow            #00FF00
    (0, 255, 85),      # Joint 7: Left Wrist            #00FF55
    (0, 255, 170),     # Joint 8: Right Hip             #00FFAA
    (0, 255, 255),     # Joint 9: Right Knee            #00FFFF
    (0, 170, 255),     # Joint 10: Right Ankle          #00AAFF
    (0, 85, 255),      # Joint 11: Left Hip             #0055FF
    (0, 0, 255),       # Joint 12: Left Knee            #0000FF
    (85, 0, 255),      # Joint 13: Left Ankle           #5500FF
    (170, 0, 255),     # Joint 14: Right Eye            #AA00FF
    (255, 0, 255),     # Joint 15: Left Eye             #FF00FF
    (255, 0, 170),     # Joint 16: Right Ear            #FF00AA
    (255, 0, 85),      # Joint 17: Left Ear             #FF0055

    # Bones & Other Features (Various Gradients)
    (153, 0, 0),       # Bone 1–2: Right Shoulderblade  #990000
    (153, 51, 0),      # Bone 1–5: Left Shoulderblade   #993300
    (153, 102, 0),     # Bone 2–3: Right Arm            #996600
    (153, 153, 0),     # Bone 3–4: Right Forearm        #999900
    (102, 153, 0),     # Bone 5–6: Left Arm             #669900
    (51, 153, 0),      # Bone 6–7: Left Forearm         #339900
    (0, 153, 0),       # Bone 1–8: Right Torso          #009900
    (0, 153, 51),      # Bone 8–9: Right Upper Leg      #009933
    (0, 153, 102),     # Bone 9–10: Right Lower Leg     #009966
    (0, 153, 153),     # Bone 1–11: Left Torso          #009999
    (0, 102, 153),     # Bone 11–12: Left Upper Leg     #006699
    (0, 51, 153),      # Bone 12–13: Left Lower Leg     #003399
    (0, 0, 153),       # Bone 1–0: Head                 #000099
    (51, 0, 153),      # Bone 0–14: Right Eyebrow       #330099
    (102, 0, 153),     # Bone 14–16: Right Ear          #660099
    (153, 0, 153),     # Bone 0–15: Left Eyebrow        #990099
    (153, 0, 102)      # Bone 15–17: Left Ear           #990066
}

__all__ = ["_VALID_OPEN_POSE_COLORS"]
