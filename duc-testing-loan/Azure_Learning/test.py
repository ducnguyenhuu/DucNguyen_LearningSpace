from azure.coginitiveservice.vision.customvision.prediction import CustomVisionPredictionClient
from azure.authentication import APIKeyCrendentials

crendetial = APIKeyCrendentials("your-api-key-here")
prediction = CustomVisionPredictionClient(
    endpoint="https://your-custom-vision-endpoint.cognitiveservices.azure.com/",
    credential=crendetial)

image_data = open("test.jpg", "rb").read()
results = prediction.classify_image(project_id="your-project-id", published_name="your-published-name", image_data=image_data)

for itm in results.predictions:
    print(f"{itm.tag_name}: {itm.probability * 100:.2f}%")