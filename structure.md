    rag-system/
    ├── backend/
    │   ├── __init__.py          # Đánh dấu backend là một package
    │   ├── app.py               # Entry point
    │   ├── admin_routes.py      # Routes cho admin API
    │   ├── config/
    │   │   ├── __init__.py      # Đánh dấu config là một package
    │   │   └── settings.py      # Cấu hình hệ thống
    │   ├── services/
    │   │   ├── __init__.py      # Đánh dấu services là một package
    │   │   ├── document_service.py  # Xử lý tài liệu
    │   │   ├── embedding_service.py # Dịch vụ tạo embeddings
    │   │   ├── rag_service.py       # Xử lý RAG
    │   │   ├── reflection_service.py # Cải thiện truy vấn
    │   │   └── semantic_router_service.py # Định tuyến truy vấn
    │   ├── models/
    │   │   ├── __init__.py      # Đánh dấu models là một package
    │   │   ├── document.py      # Model tài liệu
    │   │   ├── query.py         # Model truy vấn
    │   │   └── response.py      # Model phản hồi
    │   ├── utils/
    │   │   ├── __init__.py      # Đánh dấu utils là một package
    │   │   ├── file_utils.py    # Tiện ích xử lý file
    │   │   └── text_processor.py # Xử lý văn bản
    │   ├── llm/
    │   │   ├── __init__.py      # Đánh dấu llm là một package
    │   │   ├── gemini_client.py # Tích hợp Gemini AI
    │   │   └── prompt_templates.py # Các mẫu prompt
    │   └── vector_store/
    │       ├── __init__.py      # Đánh dấu vector_store là một package
    │       ├── chroma_client.py # Quản lý ChromaDB
    │       ├── embedding_manager.py # Quản lý embedding
    │       └── query_processor.py   # Xử lý truy vấn vector
    │
    ├── frontend/
    │   ├── __init__.py          # Đánh dấu frontend là một package
    │   ├── app.py               # Entry point
    │   ├── pages/
    │   │   ├── __init__.py      # Đánh dấu pages là một package
    │   │   ├── home.py          # Trang chủ
    │   │   ├── chat.py          # Trang chat
    │   │   └── admin.py         # Trang admin
    │   ├── components/
    │   │   ├── __init__.py      # Đánh dấu components là một package
    │   │   ├── chat_ui.py       # UI chat
    │   │   ├── file_uploader.py # UI upload file
    │   │   ├── language_switcher.py # Chuyển đổi ngôn ngữ
    │   │   ├── loading_indicator.py # Hiển thị trạng thái loading
    │   │   └── login_ui.py      # UI đăng nhập (tùy chọn)
    │   ├── utils/
    │   │   ├── __init__.py      # Đánh dấu utils là một package
    │   │   ├── api_client.py    # Tương tác với API
    │   │   └── i18n.py          # Quản lý đa ngôn ngữ
    │   ├── admin_page.py        # Trang admin (chính)
    │   ├── user_auth.py         # Mô-đun xác thực người dùng (tùy chọn)
    │   └── locales/
    │       ├── vi.json          # Ngôn ngữ tiếng Việt
    │       └── en.json          # Ngôn ngữ tiếng Anh
    │
    ├── docker-compose.yml       # Cấu hình Docker Compose
    ├── .env                     # Biến môi trường
    ├── backend/requirements.txt # Thư viện cần thiết cho backend
    ├── frontend/requirements.txt # Thư viện cần thiết cho frontend
    └── README.md                # Hướng dẫn