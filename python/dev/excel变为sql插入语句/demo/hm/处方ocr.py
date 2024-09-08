import requests

# Set the URL of the Flask image upload API
url = "http://219.147.99.189:7701/chufangapi"

# Set the path to the image file you want to upload
image_path = "/Users/awen/Desktop/cs.png"

# Open the image file in binary mode
with open(image_path, "rb") as image_file:
    # Create a dictionary to hold the file data
    files = {"image": image_file}

    # Send a POST request to the Flask API with the image file
    response = requests.post(url, files=files)
    print(response.text)

# Check the response status code
if response.status_code == 200:
    print("Image uploaded successfully!")
else:
    print("Failed to upload image. Error:", response.text)
