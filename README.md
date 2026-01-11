# Digital Image Archiving System  
Multimedia Project – Lebanese University, Faculty of Engineering II  
By Chloe Khoury and Lucien Karam

This project recreates and extends the idea behind Google PhotoScan by turning a physical laminated photograph into a clean, high‑quality digital archive. Our system takes a real photo captured with a smartphone, removes glare, corrects perspective and colors, enhances details, and then produces several compressed versions optimized for different storage and sharing needs.

A short demonstration video is included with the submission ⚠️
---

## Project Overview

The goal was to build a complete and realistic archiving pipeline for a difficult real‑world image: a glossy, laminated photo of a night‑time urban scene with very strong contrast and bright artificial lighting. This kind of image is especially challenging because of glare, dark areas, and saturated colors, which makes it a good test case for restoration and compression.

The system processes the image through multiple stages:  
- geometric correction and cropping  
- glare detection and removal  
- color correction and white balance  
- noise and dust removal  
- edge‑preserving sharpening  
- optional AI‑based super‑resolution  
- JPEG compression and quality analysis  

All intermediate and final results are saved automatically for inspection.

---

## System Architecture

The project is organized as a small full‑stack application:

**Backend (Python / OpenCV / Flask)**  
The main processing logic is implemented in `image_processor.py`.  
It contains the full pipeline: loading the image, running all enhancement steps, generating compressed versions, and computing PSNR, SSIM, MSE, and bitrate.  
A Flask server exposes this pipeline so it can be triggered from a user interface.

**Frontend (Web Interface)**  
A simple web interface (built with React/Node.js) allows the user to upload a photo, start the processing, and view the results.  
The interface shows the original image, the processed version, and the different compressed outputs with their quality metrics.

**AI Enhancement (Real‑ESRGAN)**  
For optional super‑resolution, we integrated Real‑ESRGAN, a pre‑trained deep learning model for real‑world image restoration.  
It can be used to upscale and refine the final image before compression when higher visual quality is required.

A separate Tkinter version of the app was also implemented for testing, but the main project uses the web‑based interface.

---

## Image Processing Pipeline

Once an image is uploaded, the following steps are executed automatically:

1. **Perspective correction and cropping**  
   The white border of the photo is detected, the image is geometrically aligned, and only the actual content is kept.

2. **Glare removal**  
   Bright specular reflections caused by the laminated surface are detected and suppressed.

3. **Color correction and white balance**  
   The color cast introduced by lighting and the camera is corrected while preserving the night‑time mood and the strong red sign.

4. **Noise and dust removal**  
   Small speckles and sensor noise are reduced without blurring important edges.

5. **Edge‑preserving sharpening**  
   Important contours and architectural lines are enhanced.

6. **(Optional) AI super‑resolution**  
   Real‑ESRGAN can be applied to improve fine details before saving the final image.

All steps are stored and visualized in a processing timeline image.

---

## Compression and Quality Analysis

The final processed image is compressed into four JPEG target sizes:  
**30 KB, 100 KB, 500 KB, and 1 MB.**

For each version, the system computes:
- **PSNR** (distortion level)  
- **SSIM** (structural similarity)  
- **MSE** (pixel error)  
- **bpp** (bits per pixel)

These values are compared to a high‑quality reference image saved before compression.  
Rate–distortion curves (PSNR vs bpp and SSIM vs bpp) are generated to find the best trade‑off between size and quality.  
In our case, the 500 KB setting provides the best balance, since quality improvements beyond this point become minimal.

---

## How to Use

1. Make sure Python and all required libraries are installed:
`pip install -r requirements.txt`
This installs:
- OpenCV, NumPy, Pillow
- Flask (backend API)
- Matplotlib, scikit‑image (metrics & plots)
- Torch and Real‑ESRGAN dependencies (optional AI upscaling)

2. Clone and install Real‑ESRGAN:
`git clone https://github.com/xinntao/Real-ESRGAN.git
cd Real-ESRGAN
pip install basicsr facexlib gfpgan
pip install -r requirements.txt
python setup.py develop`

3. Download the pretrained model:
`wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth -P weights`

4. Start the backend server (Flask API):
   `python app.py`
   
3. Start the frontend (from the frontend folder):
`cd frontend
npm install
npm start`

5. Open the web interface in your browser:
`http://localhost:5173/`

7. Upload a photo of a laminated image, Click Process to run the full pipeline.
   
9. After running, the output/ folder contains:
- processed_PHOTONAME.jpg – final enhanced image
- reference_for_metrics.png – lossless reference
- Compressed JPEGs (30 KB, 100 KB, 500 KB, 1 MB)
- processing_pipeline.png – visual steps of the pipeline
- Rate‑distortion plots (PSNR vs bpp, SSIM vs bpp)

For a complete walkthrough, please refer to the demo videos included with the submission.

