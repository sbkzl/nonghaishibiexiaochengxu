from ultralytics import YOLO

# 模块加载时只初始化一次模型
model = YOLO("model/best.pt")
CONF_THRESHOLD = 0.4  # 置信度阈值

def predict_image(img_path):
    try:
        res = model(img_path)
        boxes = res[0].boxes
        if len(boxes) == 0:
            return None, None

        # 取置信度最高的目标
        best_idx = boxes.conf.argmax()
        box = boxes[best_idx]
        conf = float(box.conf[0])

        if conf < CONF_THRESHOLD:
            return None, None

        cls_idx = int(box.cls[0])
        label = res[0].names[cls_idx]
        return label, conf

    except Exception as e:
        print(f"推理异常：{str(e)}")
        return None, None
