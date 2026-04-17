# 🤖 Chatbot Phân tích Phản hồi Sinh viên (Student Feedback Analyzer)

## 👨‍🎓 Thông tin sinh viên
| Họ và Tên | MSSV |
| :--- | :--- |
| **Phước** | **123000218** |

Hệ thống chatbot thông minh hỗ trợ giảng viên và quản lý giáo dục phân tích cảm xúc và trích xuất từ khóa từ phản hồi của sinh viên bằng công nghệ AI (Transformer - PhoBERT).

## 📌 Tính năng nổi bật
- **Phân tích cảm xúc chuẩn xác**: Sử dụng mô hình `wonrax/phobert-base-vietnamese-sentiment` chuyên biệt cho tiếng Việt để phân loại Tích cực, Tiêu cực và Trung lập.
- **Độ tin cậy (Confidence Score)**: Hiển thị xác suất thực tế từ mô hình AI (Giải quyết TODO 8).
- **Trích xuất từ khóa**: Tự động nhận diện các cụm từ quan trọng bằng `underthesea`.
- **Xử lý hàng loạt**: Hỗ trợ upload file CSV/Excel để phân tích hàng trăm phản hồi cùng lúc.
- **Trực quan hóa dữ liệu**: Biểu đồ xu hướng (Timeline), Phân bổ cảm xúc và Word Cloud từ khóa.
- **So sánh A/B**: Chế độ so sánh dữ liệu giữa hai nhóm phản hồi khác nhau.
- **Lưu trữ**: Tự động lưu lịch sử vào file `history.json`.

## 🛠️ Công nghệ sử dụng
- **Ngôn ngữ**: Python 3.9+
- **Giao diện**: Streamlit
- **AI/NLP**: Transformers (Hugging Face), PhoBERT, Underthesea, Langdetect.
- **Dữ liệu**: Pandas, Openpyxl, Plotly.
- **Quản lý gói**: `uv` (Fast Python package installer).

## 🚀 Hướng dẫn cài đặt

1. **Cài đặt uv** (nếu chưa có):
   ```bash
   curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh
   ```

2. **Cài đặt thư viện**:
   ```bash
   uv sync
   ```

3. **Chạy ứng dụng**:
   ```bash
   uv run streamlit run app_chatbot.py
   ```

4. **Chạy Test cases**:
   ```bash
   uv run pytest test_analyzer.py -v
   ```

## 📂 Cấu trúc thư mục
- `app_chatbot.py`: File giao diện chính và xử lý UI.
- `analyzer.py`: Module chứa logic xử lý AI và NLP.
- `test_analyzer.py`: Các unit test đảm bảo hệ thống chạy đúng.
- `stopwords_vi.txt`: Danh sách từ dừng tiếng Việt (để lọc từ khóa).
- `history.json`: File lưu trữ dữ liệu phân tích.


