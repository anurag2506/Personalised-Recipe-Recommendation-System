from ultralytics import YOLO
import streamlit as st
from PIL import Image
import huggingface_hub
from huggingface_hub import hf_hub_download


@st.cache_resource
def load_model():
    repo_id = "anurag2506/yolo_coco"
    model_path = hf_hub_download(repo_id=repo_id, filename="model.pt")
    model = YOLO(model_path)
    return model


def getResult(img):
    results = model(img)
    return results[0].plot()


st.title("Object Detection App")
st.write("Upload an image to classify and visualize the result!")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    model = load_model()
    st.write("Processing and Classifying...")

    result_image = getResult(image)
    st.image(
        result_image, caption="Detected Image with Predictions", use_column_width=True
    )