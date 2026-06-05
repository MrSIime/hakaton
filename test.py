import cv2


cap = cv2.VideoCapture("http://10.1.66.69:81/stream")
while True:
    ret, frame = cap.read()
    if not ret:
        continue
    cv2.imshow("Stream", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
