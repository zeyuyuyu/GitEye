import os
import cv2
import numpy as np

def process_image(image_path):
    """Applies various image processing techniques to the input image."""
    # Load the image
    image = cv2.imread(image_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply Canny edge detection
    edges = cv2.Canny(blurred, 100, 200)

    # Find contours in the image
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Draw the contours on the image
    processed_image = cv2.drawContours(image, contours, -1, (0, 255, 0), 2)

    return processed_image

if __name__ == "__main__":
    # Example usage
    image_path = "path/to/your/image.jpg"
    processed_image = process_image(image_path)
    cv2.imwrite("processed_image.jpg", processed_image)
    print("Image processing complete.")
