import json
import os

class I18nManager:
    """Quản lý đa ngôn ngữ cho ứng dụng"""
    
    def __init__(self, locale_dir="./locales", default_locale="vi"):
        self.locale_dir = locale_dir
        self.default_locale = default_locale
        self.current_locale = default_locale
        self.translations = self._load_translations()
        
    def _load_translations(self):
        """Tải tất cả các file dịch từ thư mục locales"""
        translations = {}
        
        for filename in os.listdir(self.locale_dir):
            if filename.endswith('.json'):
                locale = filename.split('.')[0]
                with open(os.path.join(self.locale_dir, filename), 'r', encoding='utf-8') as f:
                    translations[locale] = json.load(f)
                    
        return translations
        
    def set_locale(self, locale):
        """Thay đổi ngôn ngữ hiện tại"""
        if locale in self.translations:
            self.current_locale = locale
        else:
            self.current_locale = self.default_locale
            
    def get_text(self, key, **kwargs):
        """Lấy văn bản theo key với thay thế tham số"""
        if self.current_locale not in self.translations:
            locale = self.default_locale
        else:
            locale = self.current_locale
            
        text = self.translations.get(locale, {}).get(key, key)
        
        if kwargs:
            text = text.format(**kwargs)
            
        return text
        
    def get_all_locales(self):
        """Lấy danh sách các ngôn ngữ có sẵn"""
        return list(self.translations.keys())

