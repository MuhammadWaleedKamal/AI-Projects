import cv2
import numpy as np
import ultralytics

# Some neccessary variables for drawing and coordinates.
drawing = False
ix, iy = -1, -1
j = 1
lis = []
done = False

# Function for Annotate Cars.
def annotate_cars(event, x, y, flags, param):
    global drawing, ix, iy, coordinate_list, j, lis, carslist, done
    
    # When Left Button Press.
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
    
    # When Moving the Mouse.
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            # print("Rectangle is drawing")
            pass
    
    # When Release Left Mouse Button.
    elif event == cv2.EVENT_LBUTTONUP:
        nx, ny = x, y
        drawing = False
        find = False
        coor = False
        
        # It will help to create rectangle on screen.
        cv2.rectangle(img, (ix,iy), (nx,ny), (0,255,0), 2)
        
        
        for i in coordinate_list:
            
            # If the rectangle draw on cars exactly.
            if ((ix > i[0] - 30 and iy > i[1] - 30) and (x < i[2] + 30 and y < i[3] + 30)) and ((ix < i[0] + 20 and iy < i[1] + 20) and (x > i[2] - 20  and y > i[3] - 20)):
                
                # Selection message for right car annotated.
                if i not in lis and not done:
                    cv2.rectangle(img, (0,0), (530,25), (0,255,0), -1)
                    cv2.putText(img, f"You selected: {j} cars", (1,15), 1, 1.0, (0,0,0),1)
                    j += 1
                    find = True
                    coor = True
                    lis.append(i)
                    
                    # Congratulations message when we annotate all right cars.
                    if j == len(carslist)+1:
                        cv2.rectangle(img, (0,0), (580,25), (0,255,0), -1)
                        cv2.putText(img, f"Congratulations! You have selected all cars $$$. Press q for quit", (1,15), 1, 1.0, (0,0,0),1)
                        done = True
                        
                    break
                
                # If we already selected the cars.
                if not coor and not done:
                    find = True
                    cv2.rectangle(img, (0,0), (530,25), (0,255,0), -1)
                    cv2.putText(img, f"You have already selected this car", (1,15), 1, 1.0, (0,0,0),1)
                    
                    
        # If we annotate wrong cars or annotate wide area.
        if not find and not done:                        
            cv2.rectangle(img, (0,0), (530,25), (0,255,0), -1)
            cv2.putText(img, f"Wrong car or wide area selected. Try Again", (1,15), 1, 1.0, (0,0,0),1)

# For recording coordinates of moving mouse
# def fetch_xy(event, x,y, flags, param):
#     if event == cv2.EVENT_MOUSEMOVE:
#         print(x,y)
    
# Import YOLO model for Prediction on Image.
model = ultralytics.YOLO("yolo11n.pt")

# Black screen for start a Program.
screen = np.zeros((400, 1000))
cv2.putText(screen, "$ Welcome to our Car Annotating game $", (150, 150), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)
cv2.putText(screen, "Please wait our model is predicting the cars from the image...", (120, 200), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 0), 1)

cv2.imshow("Frame", screen)
cv2.waitKey(3000)

# Open Image and resize it.
# img = cv2.imread("c4.webp")
# img = cv2.imread("c9.jpg")
img = cv2.imread("c10.webp")
img = cv2.resize(img, (580,350))

# Prediction data is in the results.
results = model.predict(img)
# results[0].show()

coordinate_list = []
carslist = []

# For Storing neccessary details from results.
for result in results:
    box = result.boxes.xyxy
    cls = result.boxes.cls
    names = result.names
    
    for bbox in box:
        number_list = [int(i) for i in bbox]
        coordinate_list.append(number_list)
        classes = [names[int(j)] for j in cls]

# For Storing only car string from results.
for car in classes:
    if car == "car":
        carslist.append(car)
        
# Message of Total cars Predicted by Model.
cv2.putText(screen, f"Model Predicted {len(carslist)} Cars. Lets see how many car you annotate correctly", (60, 250), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 0), 1)
cv2.waitKey(1000)

if len(carslist) == 0:
    cv2.waitKey(3000)
    cv2.putText(screen, f"The program is closing. Please wait...", (300, 300), 1, 1.0, (255,0,0),1)
    cv2.destroyWindow("Frame")

# Turn for a User for annotate all correct cars that is predicted by model.
for i in range(5, -1, -1):
    cv2.rectangle(screen, (567, 284), (585, 306), (0, 0, 0), -1)
    cv2.putText(screen, f"Your turn starts in: {i}", (300, 300), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 0), 1)
    cv2.imshow("Frame", screen)
    cv2.waitKey(1000)

# When User Turn started, close the previous window and opens the other one.
cv2.imshow("Frame", screen)
cv2.waitKey(1000)
cv2.destroyWindow("Frame")

# cv2.namedWindow("Frame")
# cv2.setMouseCallback("Frame", fetch_xy)

# Work on Image Window and Set Callback function for Mouse.
cv2.namedWindow("Image")
cv2.setMouseCallback("Image", annotate_cars)

# For showing continuous Image.
while(1):
    cv2.imshow("Image", img)
    
    # When press q button, Loop will end and Program will close.
    if cv2.waitKey(1) & 0XFF == ord("q"):
        break
    
cv2.destroyAllWindows