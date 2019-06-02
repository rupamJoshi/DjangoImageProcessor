import cv2
s_img = cv2.imread("puppeta.png")
l_img = cv2.imread("large_white_square.png")



x_offset=y_offset=50
l_img[y_offset:y_offset+s_img.shape[0], x_offset:x_offset+s_img.shape[1]] = s_img
cv2.imwrite("vbvb.jpg",l_img);
cv2.waitKey(1000)
