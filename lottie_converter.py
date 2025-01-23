import cv2
import json
import base64
import os

def main():
    try:
        frames_count = int(input("Please enter the desired number of frames for the Lottie sequence (e.g., 40): "))
    except ValueError:
        print("Invalid input for the number of frames. Please enter an integer.")
        return

    input_mp4_path = input("Please enter the file path to the MP4 file: ")
    output_dir = input("Please enter the target directory for the output JSON file: ")

    if not os.path.isfile(input_mp4_path):
        print("The specified MP4 file was not found.")
        return

    if not os.path.isdir(output_dir):
        print("The specified target directory was not found.")
        return

    output_json_path = os.path.join(output_dir, "project.json")

    cap = cv2.VideoCapture(input_mp4_path)
    if not cap.isOpened():
        print("Error opening the video file.")
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    if total_frames == 0:
        print("The video contains no usable frames or could not be read.")
        cap.release()
        return

    step = total_frames / frames_count

    frames_data = []

    for i in range(frames_count):
        frame_idx = int(i * step)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        success, frame = cap.read()

        if not success:
            print(f"Frame {frame_idx} could not be read. Aborting.")
            break

        ret, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not ret:
            print(f"Error encoding frame {frame_idx}")
            break

        b64_str = base64.b64encode(buffer).decode("utf-8")

        frames_data.append(b64_str)

    cap.release()

    if not frames_data:
        print("No frames were successfully processed. Aborting.")
        return

    lottie_dict = {
        "v": "5.5.2",
        "fr": fps,
        "ip": 0,
        "op": frames_count,
        "w": width,
        "h": height,
        "nm": "@forresto/movie-to-lottie",
        "ddd": 0,
        "assets": [],
        "layers": []
    }

    for idx, b64_str in enumerate(frames_data):
        asset_id = f"fr_{idx}"
        image_item = {
            "id": asset_id,
            "w": width,
            "h": height,
            "u": "",
            "p": f"data:image/jpeg;base64,{b64_str}",
            "e": 1
        }
        lottie_dict["assets"].append(image_item)

        layer_item = {
            "ddd": 0,
            "ind": idx + 1,
            "ty": 2,
            "nm": f"{asset_id}.jpg",
            "cl": "jpg",
            "refId": asset_id,
            "sr": 1,
            "ks": {
                "o": {"a": 0, "k": 100, "ix": 11},
                "r": {"a": 0, "k": 0, "ix": 10},
                "p": {"a": 0, "k": [width / 2, height / 2, 0], "ix": 2},
                "a": {"a": 0, "k": [width / 2, height / 2, 0], "ix": 1},
                "s": {"a": 0, "k": [100, 100, 100], "ix": 6}
            },
            "ao": 0,
            "ip": idx,
            "op": idx + 1,
            "st": idx,
            "bm": 0
        }
        lottie_dict["layers"].append(layer_item)

    try:
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(lottie_dict, f, ensure_ascii=False, indent=2)
        print(f"Done! The JSON file has been created at '{output_json_path}'.")
    except Exception as e:
        print(f"Error writing the JSON file: {e}")

if __name__ == "__main__":
    main()
