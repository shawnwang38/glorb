import cv2

print("Opening camera...")
cap = cv2.VideoCapture(0)
print(f"  opened: {cap.isOpened()}")

print("Reading frame...")
ok, frame = cap.read()
print(f"  read ok: {ok}, frame shape: {frame.shape if ok else None}")

if ok:
    print("Showing window (press any key to close)...")
    cv2.imshow("diag", frame)
    key = cv2.waitKey(5000)
    print(f"  key pressed: {key}")
    cv2.destroyAllWindows()

cap.release()
print("Done.")
