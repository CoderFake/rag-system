# Hệ thống RAG với Gemini AI

Hệ thống RAG (Retrieval-Augmented Generation) tích hợp với Gemini AI cho phép xây dựng chatbot trả lời dựa trên kho kiến thức đã được tải lên.

## Tính năng

- Tải lên tài liệu (PDF, DOCX, TXT, CSV) vào kho kiến thức
- Tích hợp với Gemini AI cho việc tạo câu trả lời chất lượng cao
- Hỗ trợ đa ngôn ngữ (Tiếng Việt, Tiếng Anh)
- Xác thực người dùng JWT với MySQL
- Giao diện người dùng thân thiện với Streamlit
- Quản lý tài liệu và cài đặt hệ thống
- Lịch sử chat và đánh giá câu trả lời

## Cấu trúc dự án

```
rag-system/
├── backend/                      # Backend Flask API
│   ├── app.py                    # Entry point
│   ├── admin_routes.py           # Route admin API
│   ├── auth/                     # Xác thực
│   │   ├── auth_routes.py        # API đăng nhập/đăng ký 
│   │   └── jwt_manager.py        # Quản lý JWT
│   ├── config/                   # Cấu hình
│   │   └── settings.py           # Cài đặt hệ thống
│   ├── db/                       # Database
│   │   └── mysql_manager.py      # Kết nối MySQL
│   ├── services/                 # Dịch vụ
│   │   ├── chat_service.py       # Xử lý chat
│   │   ├── document_service.py   # Xử lý tài liệu
│   │   ├── embedding_service.py  # Dịch vụ embedding
│   │   ├── rag_service.py        # Xử lý RAG
│   │   ├── reflection_service.py # Cải thiện truy vấn
│   │   └── semantic_router_service.py # Định tuyến truy vấn
│   ├── models/                   # Models
│   │   ├── document.py           # Model tài liệu
│   │   ├── query.py              # Model truy vấn
│   │   ├── response.py           # Model phản hồi
│   │   └── user.py               # Model người dùng
│   ├── utils/                    # Tiện ích
│   │   ├── file_utils.py         # Xử lý file
│   │   └── text_processor.py     # Xử lý văn bản
│   ├── llm/                      # LLM
│   │   ├── gemini_client.py      # Tích hợp Gemini
│   │   └── prompt_templates.py   # Template prompt
│   ├── vector_store/             # Vector store
│   │   ├── chroma_client.py      # ChromaDB client
│   │   ├── embedding_manager.py  # Quản lý embedding
│   │   └── query_processor.py    # Xử lý truy vấn vector
│   └── Dockerfile                # Docker cho backend
│
├── frontend/                     # Frontend Streamlit
│   ├── app.py                    # Entry point
│   ├── admin_page.py             # Trang admin
│   ├── pages/                    # Các trang
│   │   ├── chat.py               # Trang chat
│   │   ├── admin.py              # Trang admin (alternative)
│   │   └── home.py               # Trang chủ
│   ├── components/               # Các component
│   │   ├── chat_ui.py            # UI chat
│   │   ├── file_uploader.py      # Component upload file
│   │   ├── language_switcher.py  # Chuyển đổi ngôn ngữ
│   │   ├── loading_indicator.py  # Hiển thị loading
│   │   └── login_ui.py           # UI đăng nhập
│   ├── utils/                    # Tiện ích
│   │   ├── api_client.py         # Gọi API
│   │   └── i18n.py               # Đa ngôn ngữ
│   ├── locales/                  # File ngôn ngữ
│   │   ├── vi.json               # Tiếng Việt
│   │   └── en.json               # Tiếng Anh
│   ├── user_auth.py              # Xác thực người dùng
│   └── Dockerfile                # Docker cho frontend
│
├── docker-compose.yml            # Cấu hình Docker Compose
└── .env.example                  # Mẫu biến môi trường
```

## Yêu cầu hệ thống

- Python 3.9+
- MySQL 8.0+
- Docker và Docker Compose (tùy chọn)

## Cài đặt

### Cài đặt thủ công

1. Clone dự án:
```
git clone https://github.com/coderfake/rag-system.git
cd rag-system
```

2. Cài đặt thư viện cho backend:
```
cd backend
pip install -r requirements.txt
```

3. Cài đặt thư viện cho frontend:
```
cd ../frontend
pip install -r requirements.txt
```

4. Tạo file `.env` từ mẫu:
```
cp .env.example .env
```

5. Chỉnh sửa file `.env` với thông tin cấu hình của bạn:
```
# API Keys
GEMINI_API_KEY=your_gemini_api_key

# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=yourpassword
MYSQL_DATABASE=rag_system

# JWT
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ACCESS_TOKEN_EXPIRES=86400
JWT_REFRESH_TOKEN_EXPIRES=604800

# Flask
FLASK_ENV=development
SECRET_KEY=your_flask_secret_key

# Chroma
CHROMA_DB_PATH=./chroma_db
```

6. Khởi tạo cơ sở dữ liệu MySQL:
```sql
CREATE DATABASE rag_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

7. Khởi động backend:
```
cd ../backend
python app.py
```

8. Khởi động frontend (trong terminal mới):
```
cd ../frontend
streamlit run app.py
```

### Sử dụng Docker

1. Clone dự án:
```
git clone https://github.com/coderfake/rag-system.git
cd rag-system
```

2. Tạo file `.env` từ mẫu:
```
cp .env.example .env
```

3. Chỉnh sửa file `.env` với thông tin cấu hình của bạn

4. Khởi động với Docker Compose:
```
docker-compose up -d
```

## Sử dụng

1. Truy cập giao diện frontend: http://localhost:8686
2. Đăng nhập với tài khoản mặc định:
   - Username: admin
   - Password: admin123
3. Vào trang Admin để tải lên tài liệu vào kho kiến thức
4. Quay lại trang Chat để bắt đầu trò chuyện với chatbot

## Các API Endpoint

### Auth API
- `POST /api/auth/login`: Đăng nhập và lấy JWT token
- `POST /api/auth/register`: Đăng ký tài khoản mới
- `POST /api/auth/refresh`: Làm mới token
- `GET /api/auth/profile`: Lấy thông tin người dùng
- `GET /api/auth/users`: Lấy danh sách người dùng (chỉ admin)

### Chat API
- `POST /api/chat`: Gửi câu hỏi và nhận phản hồi
- `GET /api/chat/history`: Lấy lịch sử chat
- `POST /api/chat/feedback`: Thêm đánh giá cho câu trả lời

### Admin API
- `POST /api/admin/upload`: Tải lên tài liệu
- `GET /api/admin/documents`: Lấy danh sách tài liệu
- `DELETE /api/admin/documents/<document_id>`: Xóa tài liệu
- `POST /api/admin/reindex`: Đánh chỉ mục lại tất cả tài liệu
- `GET /api/settings`: Lấy cài đặt hệ thống
- `POST /api/settings`: Cập nhật cài đặt hệ thống

## Tùy chỉnh và mở rộng

### Thêm ngôn ngữ mới

1. Tạo file ngôn ngữ mới trong thư mục `frontend/locales/`
2. Thêm ngôn ngữ vào danh sách trong `frontend/utils/i18n.py`
3. Thêm prompt template cho ngôn ngữ mới trong `backend/services/rag_service.py`

### Thêm loại tài liệu mới

1. Thêm loader mới trong `backend/services/document_service.py`
2. Cập nhật UI upload trong `frontend/components/file_uploader.py`

## Giấy phép

MIT License