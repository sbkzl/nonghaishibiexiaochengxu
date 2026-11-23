import os
import uuid
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from utils.model_infer import predict_image
from utils.ip_parser import get_province_by_ip

app = FastAPI(title="植物病害检测系统API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
MAX_FILE_SIZE = 10 * 1024 * 1024


@app.post("/upload", summary="上传图片识别病害")
async def upload_image(request: Request, file: UploadFile = File(...)):
    conn = None
    try:
        if file.size > MAX_FILE_SIZE:
            return {"code": 400, "msg": "图片不能超过10MB"}

        client_ip = request.client.host
        suffix = os.path.splitext(file.filename)[1]
        save_name = f"{uuid.uuid4().hex}{suffix}"
        save_path = os.path.join(UPLOAD_DIR, save_name)

        with open(save_path, "wb") as f:
            f.write(await file.read())

        disease_label, confidence = predict_image(save_path)
        print(f"模型输出标签: {disease_label}, 置信度: {confidence:.3f}")
        if disease_label is None:
            return {"code": 0, "msg": "图片未检测到病害"}

        conn = sqlite3.connect("plant_disease.db")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("SELECT * FROM disease WHERE disease_name = ?", (disease_label,))
        disease_info = cur.fetchone()
        if disease_info is None:
            return {"code": 0, "msg": f"识别标签[{disease_label}]暂无配套防治资料"}
        disease_id = disease_info["id"]

        user_province = get_province_by_ip(client_ip)
        print(f"客户端IP: {client_ip}, 解析省份: {user_province}")
        cur.execute("SELECT * FROM region_prevention WHERE disease_id = ? AND region_type = ?", (disease_id, user_province))
        region_data = cur.fetchone()

        cur.execute("SELECT * FROM season_manage WHERE disease_id = ?", (disease_id,))
        season_data = cur.fetchone()

        cur.execute("""
            SELECT am.*, sm.adapt_reason
            FROM agri_material am
            JOIN season_material sm ON am.id = sm.material_id
            WHERE sm.disease_id = ?
        """, (disease_id,))
        material_rows = cur.fetchall()

        image_url = f"http://10.91.226.115:8000/static/uploads/{save_name}"

        now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("""
        INSERT INTO history(disease_name, chinese_name, confidence, image_url, client_ip, create_time, province)
        VALUES (?,?,?,?,?,?,?)
        """, (disease_label, disease_info["chinese_name"], confidence, image_url, client_ip, now_time, user_province))
        conn.commit()

        result = {
            "code": 200,
            "msg": "识别成功",
            "data": {
                "disease_label": disease_label,
                "chinese_name": disease_info["chinese_name"],
                "crop_name": disease_info["crop_name"],
                "symptom": disease_info["symptom"],
                "general_prevention": disease_info["general_prevention"],
                "region_prevention": dict(region_data) if region_data else None,
                "season_manage": dict(season_data) if season_data else None,
                "materials": [dict(item) for item in material_rows],
                "confidence": round(float(confidence), 3),
                "image_url": image_url
            }
        }
        return result

    except Exception as e:
        print(f"【服务异常】{str(e)}")
        return {"code": 500, "msg": f"服务器错误: {str(e)}"}
    finally:
        if conn:
            conn.close()


@app.get("/history", summary="获取识别历史记录")
async def get_history():
    conn = None
    try:
        conn = sqlite3.connect("plant_disease.db")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM history ORDER BY id DESC")
        rows = cur.fetchall()
        return {"code": 200, "data": [dict(r) for r in rows]}
    except Exception as e:
        print(f"【查询历史异常】{str(e)}")
        return {"code": 500, "msg": f"服务器错误: {str(e)}"}
    finally:
        if conn:
            conn.close()


@app.delete("/history/{record_id}", summary="删除单条历史记录")
async def delete_history(record_id: int):
    conn = None
    try:
        conn = sqlite3.connect("plant_disease.db")
        cur = conn.cursor()
        cur.execute("DELETE FROM history WHERE id = ?", (record_id,))
        conn.commit()
        return {"code": 200, "msg": "删除成功"}
    except Exception as e:
        return {"code": 500, "msg": f"删除失败: {str(e)}"}
    finally:
        if conn:
            conn.close()


@app.get("/diseases", summary="获取所有病害列表")
async def get_diseases():
    conn = None
    try:
        conn = sqlite3.connect("plant_disease.db")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM disease ORDER BY id")
        rows = cur.fetchall()
        return {"code": 200, "data": [dict(r) for r in rows]}
    except Exception as e:
        print(f"【查询病害列表异常】{str(e)}")
        return {"code": 500, "msg": f"服务器错误: {str(e)}"}
    finally:
        if conn:
            conn.close()


@app.get("/recommend", summary="根据省份或季节推荐易发病害")
async def recommend(request: Request):
    conn = None
    try:
        client_ip = request.client.host
        province = get_province_by_ip(client_ip)
        now_month = datetime.now().month

        if 3 <= now_month <= 5:
            season_key, season_name = "春", "春季"
        elif 6 <= now_month <= 8:
            season_key, season_name = "夏", "夏季"
        elif 9 <= now_month <= 11:
            season_key, season_name = "秋", "秋季"
        else:
            season_key, season_name = "冬", "冬季"

        conn = sqlite3.connect("plant_disease.db")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

      
        cur.execute("""
            SELECT DISTINCT d.id, d.chinese_name, d.crop_name, d.symptom, d.general_prevention
            FROM disease d
            LEFT JOIN region_prevention r ON d.id = r.disease_id
            LEFT JOIN season_manage s ON d.id = s.disease_id
            WHERE (r.region_type = ? OR s.season LIKE ?)
            AND d.disease_name NOT LIKE '%healthy%'
            LIMIT 6
        """, (province, f"%{season_key}%"))
        rows = cur.fetchall()

        result = []
        for row in rows:
            result.append({
                "chinese_name": row["chinese_name"],
                "crop_name": row["crop_name"],
                "symptom": row["symptom"],
                "general_prevention": row["general_prevention"]
            })

        return {
            "code": 200,
            "data": {
                "province": province,
                "season": season_name,
                "recommendations": result
            }
        }
    except Exception as e:
        return {"code": 500, "msg": f"推荐失败: {str(e)}"}
    finally:
        if conn:
            conn.close()




if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
